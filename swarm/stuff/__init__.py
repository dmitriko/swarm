from swarm.entity import Entity
from swarm.cluster import Cluster


class Node(Entity):
    "Host for hypervisor"
    def __init__(self, **kw):
        self.host_nics = kw.get('host_nics', {})
        Entity.__init__(self, **kw)

    def add_host_nic(self, nic):
        assert isinstance(nic, HostNic)
        self.host_nics[nic.name] = nic.oid
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
            raise RuntimeError("No NIC with name %s in %s" % (
                    nic_name, self))


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
        self.bridge = kw.get('bridge')
