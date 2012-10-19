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
        self.bridge = kw.get('bridge')
