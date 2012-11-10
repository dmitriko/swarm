from swarm.entity import Entity
from swarm import fields


class BaseReport(Entity):
    "Represent any report info in wire"
    reporter_oid = fields.BaseField('reporter_oid', required=True)
    node_oid = fields.BaseField('node_oid')
    raw_data = fields.BaseField('raw_data')

    @classmethod
    def create(cls, node_oid, **kw):
        "Return instance"
        return cls(reporter_oid = node_oid,
                   node_oid = node_oid,
                   **kw)


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
    
