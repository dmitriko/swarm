from .fixtures import VIRSH_LIST
from .base import BaseTestCase

from swarm.reports import VirshListReport


class VirshListCase(BaseTestCase):
    def test_raw_data(self):
        report = VirshListReport(self.node_oid, raw_data=VIRSH_LIST)
        self.assertEqual(report.parsed_data[2]['name'], 'hydravm')
