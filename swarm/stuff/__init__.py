import uuid
import os

from tornado.options import options

from swarm.entity import Entity
from swarm.cluster import Cluster


class Node(Entity):
    "Host for hypervisor"
    def __init__(self, hostname, **kw):
        self.hostname = hostname
        self.host_nics = kw.get('host_nics', {})
        self.storages = kw.get('storages', [])
        self.vm_processes = kw.pop('vm_processes', {})
        Entity.__init__(self, **kw)

    def update_host_nic(self, name, **kw):
        nic = self.get_host_nic(name)
        if nic:
            nic.set(**kw)
        else:
            nic = HostNic(self, name, **kw)
            self.host_nics[name] = nic.oid
            Cluster.instance().store(nic)

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
    
    def update_vm_process(self, libvirt_id, vm_config):
        if libvirt_id not in self.vm_processes or self.vm_processes[
            libvirt_id].vm_config.oid != vm_config.oid:
            vm_process = VmProcess(self, libvirt_id, vm_config)
            Cluster.instance().store(vm_process)
            self.vm_processes[libvirt_id] = vm_process
        
    def get_vm_processes(self):
        result = []
        for id_ in sorted(self.vm_processes.keys()):
            result.append(self.vm_processes[id_])
        return result


    @classmethod
    def get_storage_points(cls, client):
        "Return list of StoragePoints for given config settings"
        if not options.storages:
            return []
        result = []
        for path in options.storages.split(','):
            result.append(StoragePoint(node_oid=client.oid,
                                       storage_oid=Storage.ensure(path),
                                       path=path))
        return result


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


class StoragePoint(Entity):
    "Store host-storage relation, could be mount or just regular dir"
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
                StoragePoint) if x.storage_oid == self.oid]
    
    @classmethod
    def ensure(cls, path, oid=None):
        """Create a dir in at file path, 
        generate uuid and store it in file, return storage oid

        """
        sys_dir = os.path.join(path, '.vgd')
        if not os.path.exists(sys_dir):
            os.makedirs(sys_dir)
        oid_file_path = os.path.join(sys_dir, 'oid')
        if os.path.exists(oid_file_path):
            return open(oid_file_path).read().strip()
        oid = oid or str(uuid.uuid1())
        open(os.path.join(sys_dir, 'oid'), 'w').write(oid)
        return oid


class Network(Entity):
    "Represent virtual network in system"
    def __init__(self, title, host_nics=None, **kw):
        self.title = title
        if host_nics:
            self.host_nics = set(host_nics)
        else:
            self.host_nics = set()
        Entity.__init__(self, **kw)
    
    def add_host_nic(self, nic):
        assert isinstance(nic, HostNic)
        if not nic.bridge_for and nic.in_bridge:
            nic = nic.in_bridge
        self.host_nics.add(nic.oid)
        self.set(host_nics=self.host_nics)
        
    def remove_host_nic(self, nic):
        assert isinstance(nic, HostNic)
        try:
            self.host_nics.remove(nic.oid)
            self.set(host_nics=self.host_nics)
        except KeyError:
            pass

    def get_host_nics(self):
        cluster = Cluster.instance()
        return [cluster.get(x) for x in self.host_nics]


class VmDisk(Entity):
    def __init__(self, storage, path, type, info=None, stat=None, **kw):
        self.storage = storage
        self.path = path
        self.type = type
        self.info = info
        self.stat = stat
        Entity.__init__(self, **kw)


class VmNic(Entity):
    def __init__(self, mac, bridge, target, **kw):
        self.mac = mac
        self.bridge = bridge
        self.target = target
        Entity.__init__(self, **kw)


class VmConfig(Entity):
    def __init__(self, vcpu, memory, disks=None, nics=None, extra_devices=None, 
                 libvirt_xml=None, name=None, features=None, **kw):
        self.vcpu = vcpu
        self.memory = memory
        self.disks = disks or []
        self.nics = nics or []
        self.extra_devices = extra_devices
        self.libvirt_xml = libvirt_xml
        self._name = name
        self.features = features or []
        Entity.__init__(self, **kw)

    def name(self):
        return self._name or self.oid

    def to_xml(self):
        "Create xml to use in libvirt"
        pass


class VmProcess(Entity):
    "Represent running VM on host"
    def __init__(self, host, libvirt_id, vm_config=None, **kw):
        self.host = host
        self.libvirt_id = libvirt_id
        self.vm_config = vm_config
        Entity.__init__(self, **kw)

