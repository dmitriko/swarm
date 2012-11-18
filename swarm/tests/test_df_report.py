from .base import BaseTestCase
from .fixtures import DF_RAW
from swarm.reports import DFReport


class DFParseCase(BaseTestCase):
    def test_parsing(self):
        report = DFReport.create(self.node_oid, raw_data=DF_RAW)
        data = report.parsed_data
        self.assertTrue('/home' in data)
        self.assertEqual(data['/home']['avail'], '702G')
