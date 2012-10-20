from .base_event import Event


class NodeEvent(Event):

    def __init__(self, reporter, **kw):
        "Raised when node went online"

        if 'node_oid' in kw:
            self.node_oid = kw.pop('node_oid')
        else:
            self.node_oid = reporter

        Event.__init__(self, reporter, **kw)


class NodeOnlineEvent(NodeEvent):
    def __init__(self, reporter, storages=None, **kw):
        NodeEvent.__init__(self, reporter)
        self.storages = storages or []

    def to_dict(self):
        info = NodeEvent.to_dict(self)
        info['storages'] = [x.to_dict() for x in info['storages']]
        return info

class NodeOffline(NodeEvent): pass


class TaskEvent(NodeEvent):
    def __init__(self, reporter, task, **kw):
        self.reporter = reporter
        self.task = task


class TaskUpdated(TaskEvent): pass


class TaskFailed(TaskEvent): pass


class TaskSuccess(TaskEvent): pass


class ReportCollectFailed(NodeEvent):
    def __init__(self, reporter, report, error, **kw):
        NodeEvent.__init__(self, reporter, **kw)
        self.report = report
        self.error = error
