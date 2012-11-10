
from swarm.reports.base_report import BaseReport
from swarm import fields


class NodeOnlineReport(BaseReport):
    hostname = fields.BaseField('hostname', required=True)
    storages = fields.ListField('storages')

