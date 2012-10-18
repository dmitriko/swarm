from swarm.events.base_event import Event


class BaseReport(Event):
    "Represent any report info in wire"
    def __init__(self, reporter, raw_data=None, **kw):
        Event.__init__(self, reporter, **kw)
        self.raw_data = raw_data


class SubprocessReport(BaseReport):
    "Use popen to collect raw data"

    cmd  = [] # parameters for subprocess

    def __init__(self, *args, **kw):
        BaseReport.__init__(self, *args, **kw)
        if not isinstance(self.cmd, list):
            raise RuntimeError(
                "cls.cmd is not set or not a list")

    def parsed_data(self):
        "Return dict with parsed items"
        raise NotImplementedError
    
