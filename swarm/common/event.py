

from swarm.common.entity import Entity


class Event(Entity):

    def __init__(self, reporter, **kw):
        self.reporter = reporter
        Entity.__init__(self, **kw)
    

class NodeOnlineEvent(Event):
    def __init__(self, reporter, node_oid=None, **kw):
        """reporter is a node oid
        comm_queue is AMPQ queue name for RPC

        """
        Event.__init__(self, reporter, **kw)
        self.node_oid = node_oid or reporter


class NodeOffline(NodeOnlineEvent):
    pass
