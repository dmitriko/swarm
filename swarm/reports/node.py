
from swarm.reports.base_report import BaseReport, SubprocessReport
from swarm import fields


class NodeOnlineReport(BaseReport):
    hostname = fields.BaseField('hostname', required=True)
    storages = fields.ListField('storages')


class DFReport(SubprocessReport):
    "Result of df -h from Node"
    cmd = ['df', '-h']

    @property
    def parsed_data(self):
        if self.raw_data is None:
            return {}
        result = {}
        for line in self.raw_data.split('\n'):
            parts = line.split()
            if len(parts) < 5 or parts[0].startswith('Filesystem'):
                continue
            mounted = parts[-1]
            result[mounted] = dict(use=parts[-2],
                                   avail=parts[-3],
                                   used=parts[-4],
                                   size=parts[-5])
        return result
