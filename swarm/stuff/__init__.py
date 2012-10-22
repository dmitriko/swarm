from tornado.options import options

from swarm.entity import Entity
from swarm.cluster import Cluster


class Node(Entity):
    "Host for hypervisor"
    def __init__(self, **kw):
        self.host_nics = kw.get('host_nics', {})
        Entity.__init__(self, **kw)

    def update_host_nic(self, nic):
        assert isinstance(nic, HostNic)
        cluster = Cluster.instance()
        self.host_nics[nic.name] = nic.oid
        existed_nic = cluster.get(nic.oid)
        if existed_nic:
            existed_nic.set(nic.to_dict())
            cluster.store(existed_nic)
        else:
            cluster.store(nic)

    def get_host_nic(self, nic_name):
        cluster = Cluster.instance()
        try:
            nic_oid = self.host_nics[nic_name]
            nic = cluster.get(nic_oid)
            if nic is None:
                raise KeyError(nic_name)
            return nic
        except KeyError:
            return None


class HostNic(Entity):
    "Host network interface"
    def __init__(self, host, name, **kw):
        Entity.__init__(self, **kw)
        self.host = host
        self.name = name
        self.mac = kw.get('mac')
        self.inet_addr = kw.get('inet_addr')
        self.mask = kw.get('mask')
        self.rx_bytes = kw.get('rx_bytes')
        self.tx_bytes = kw.get('rx_bytes')
        self.in_bridge = kw.get('in_bridge')
        self.bridge_for = kw.get('bridge_for', [])


class MountPoint(Entity):
    "Store host-storage relation"
    def __init__(self, node_oid, storage_oid, path, **kw):
        Entity.__init__(self, **kw)
        self.node_oid = node_oid
        self.storage_oid = storage_oid
        self.path = path


class Storage(Entity):
    def get_mount_points(self):
        "Return list of mount points for this storage"
        cluster = Cluster.instance()
        return [x for x in cluster.entities_by_class(
                MountPoint) if x.storage_oid == self.oid]
    
    @classmethod
    def ensure(self, path, oid=None):
        """Create a dir in at file path, 
        generate uuid and store it in file, return storage oid

        """

        import uuid
        import os
        sys_dir = os.path.join(path, '.vgd')
        if not os.path.exists(sys_dir):
            os.makedirs(sys_dir)
        oid_file_path = os.path.join(sys_dir, 'oid')
        if os.path.exists(oid_file_path):
            return open(oid_file_path).read().strip()
        oid = oid or str(uuid.uuid1())
        open(os.path.join(sys_dir, 'oid'), 'w').write(oid)
        return oid

    @classmethod
    def get_node_mountpoints(cls, client):
        "Return list of MountPoints for given config settings"
        if not options.storages:
            return []
        result = []
        for path in options.storages.split(','):
            result.append(MountPoint(node_oid=client.oid,
                                     storage_oid=cls.ensure(path),
                                     path=path))
        return result
