from swarm.entity import Entity


class Node(Entity):
    "Host for hypervisor"
    def __init__(self, **kw):
        self.host_nics = kw.get('host_nics', [])
        self.vm_nics = kw.get('vm_nics', [])
        self.vm_processes = kw.get('vm_processes', [])
        Entity.__init__(self, **kw)


