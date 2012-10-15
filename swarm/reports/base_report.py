from swarm.events.base_event import Event


class BaseReport(Event):
    "Represent any report info in wire"
    def __init__(self, reporter, raw_data=None, **kw):
        Event.__init__(self, reporter, **kw)
        self.raw_data = raw_data


class SubprocessReport(BaseReport):
    "Use popen to collect raw data"
    def _cmd(self):
        "Return list of string for usring in subprocess call"
        raise NonImplementedError
    cmd = property(_cmd)
