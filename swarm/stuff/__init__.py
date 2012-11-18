import uuid
import os

from tornado.options import options

from swarm.entity import Entity
from swarm.cluster import Cluster
from swarm import fields


class Node(Entity):
    "Host for hypervisor"

    hostname = fields.BaseField('hostname')
    host_nics = fields.DictField('host_nics')
    vm_procs = fields.DictField('vm_procs')
    state = fields.BaseField('state', choices=['offline', 'online'])

    def update_host_nic(self, name, **kw):
        nic = self.get_host_nic(name)
        if nic:
            nic.set(**kw)
        else:
            nic = HostNic(host=self, name=name, **kw)
            self.host_nics[name] = nic.oid
            Cluster.instance().store(nic)

    @property
    def storages(self):
        return [x for x in Cluster.instance().entities_by_class(
                StoragePoint) if x.node_oid == self.oid]

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
        if self.vm_procs.get(libvirt_id) != vm_config.oid:
            vm_process = VmProcess(node=self, 
                                   libvirt_id=libvirt_id, 
                                   vm_config=vm_config)
            Cluster.instance().store(vm_process)
            self.vm_procs[libvirt_id] = vm_process.oid
        
    def get_vm_procs(self):
        cluster = Cluster.instance()
        return [cluster.get(x) for x in self.vm_procs.values()]



    @classmethod
    def get_storage_points(cls, client):
        "Return list of StoragePoints for given config settings"
        if not options.storages:
            return []
        result = []
        for path in options.storages.split(','):
            result.append(dict(node_oid=client.oid,
                               storage_oid=Storage.ensure(path),
                               path=path))
        return result


class HostNic(Entity):
    "Host network interface"
    host = fields.ReferenceField('host')
    name = fields.BaseField('name')
    mac = fields.BaseField('mac')
    inet_addr = fields.BaseField('inet_addr')
    mask = fields.BaseField('mask')
    rx_bytes = fields.BaseField('rx_bytes')
    tx_bytes = fields.BaseField('tx_bytes')
    in_bridge = fields.BaseField('in_bridge')
    bridge_for = fields.BaseField('bridge_for')


class StoragePoint(Entity):
    "Store host-storage relation, could be mount or just regular dir"
    node_oid = fields.BaseField('node', required=True)
    storage_oid = fields.BaseField('storage')
    path = fields.BaseField('path')


class Storage(Entity):

    avail = fields.BaseField('avail')

    def get_mount_points(self):
        "Return list of mount points for this storage"
        cluster = Cluster.instance()
        return [x for x in cluster.entities_by_class(
                StoragePoint) if x.storage.oid == self.oid]

    @classmethod
    def update_points(cls, points):

        cluster = Cluster.instance()

        def is_exists(info):
            for spoint in cluster.entities_by_class(StoragePoint):
                if spoint.node_oid == info['node_oid'] and \
                        spoint.path == info['path'] and \
                        spoint.storage_oid == info['storage_oid']:
                    return True
            return False

        for point in points:
            storage_oid = point['storage_oid']
            if not cluster.is_stored(storage_oid):
                cluster.store(Storage(oid=storage_oid))
            if not is_exists(point):
                cluster.store(StoragePoint(node_oid=point['node_oid'],
                                           storage_oid=point['storage_oid'],
                                           path=point['path']))

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
    title = fields.BaseField('title')
    host_nics = fields.SetField('host_nics')
    
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
    storage = fields.ReferenceField('storage')
    path = fields.BaseField('path')
    type = fields.BaseField('type')
    info = fields.DictField('info')
    stat = fields.DictField('stat')


class VmNic(Entity):
    mac = fields.BaseField('mac')
    bridge = fields.BaseField('bridge')
    target = fields.BaseField('target')


class VmConfig(Entity):
    name = fields.BaseField('name')
    vcpu = fields.BaseField('vcpu')
    memory = fields.BaseField('memory')
    disks = fields.SetField('disks')
    nics = fields.SetField('nics')
    extra_devices = fields.BaseField('extra')
    libvirt_xml = fields.BaseField('libvirt_xml')
    features = fields.SetField('features')


    def to_xml(self):
        "Create xml to use in libvirt"
        pass


class VmProcess(Entity):
    "Represent running VM on host"
    node = fields.ReferenceField('node')
    libvirt_id = fields.BaseField('libvirt_id')
    vm_config = fields.BaseField('vm_config')


