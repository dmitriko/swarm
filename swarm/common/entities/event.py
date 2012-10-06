

from swarm.common.entities.base import Entity


class Event(Entity):

    def __init__(self, reporter, **kw):
        self.reporter = reporter
        Entity.__init__(self, **kw)
    

    @classmethod
    def from_json(cls, json_str):
        import json
        try:
            info = dict((str(x), y) for x, y in json.loads(json_str).items())
            cls_name = info['cls']
        except (ValueError, KeyError): 
            raise RuntimeError("JSON for enity is not valid %s %s" % json_str)
        del info['cls']
        entity_class = globals().get(cls_name)
        if not entity_class:
            raise RuntimeError("%s is not valid class name" % cls_name)
        return entity_class(**info)


class NodeOnlineEvent(Event):
    def __init__(self, reporter, node_oid=None, **kw):
        """reporter is a node oid
        comm_queue is AMPQ queue name for RPC

        """
        Event.__init__(self, reporter, **kw)
        self.node_oid = node_oid or reporter


class NodeOffline(NodeOnlineEvent):
    pass
