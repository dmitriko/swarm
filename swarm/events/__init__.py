

from swarm.entity import Entity


class Event(Entity):

    def __init__(self, reporter, **kw):
        self.reporter = reporter
        Entity.__init__(self, **kw)
    

class NodeEvent(Event):
    def __init__(self, reporter, **kw):
        "Raised when node went online"

        if 'node_oid' in kw:
            self.node_oid = kw.pop('node_oid')
        else:
            self.node_oid = reporter

        Event.__init__(self, reporter, **kw)


class NodeOnlineEvent(NodeEvent): pass


class NodeOffline(NodeEvent): pass


class TaskEvent(NodeEvent):
    def __init__(self, reporter, task, **kw):
        self.reporter = reporter
        self.task = task


class TaskUpdated(TaskEvent): pass


class TaskFailed(TaskEvent): pass


class TaskSuccess(TaskEvent): pass
