import uuid

from .fixtures import BRCTL_SHOW_DATA, IFCONFIG_DATA
from .base import BaseTestCase

from swarm.scenarios.onevent import on_report
from swarm.reports import BrctlShowReport, IFConfigReport, NodeOnlineReport
from swarm.cluster import Cluster


class BrctlShowCase(BaseTestCase):

    def test_report_arrived(self):
        node_oid = str(uuid.uuid1())
        on_report(NodeOnlineReport.create(node_oid, hostname='testhost'))
        on_report(IFConfigReport.create(node_oid, raw_data=IFCONFIG_DATA))
        on_report(BrctlShowReport.create(node_oid, raw_data=BRCTL_SHOW_DATA))
        cluster = Cluster.instance()
        node = cluster.get(node_oid)
        self.assertTrue(node)
        eth2 = node.get_host_nic('eth2')
        self.assertTrue(eth2)
        self.assertEqual(eth2.in_bridge, 'virbr2')
        virbr2 = node.get_host_nic('virbr2')
        self.assertEqual(virbr2.bridge_for,
                         ['eth2', 'vnet0', 'vnet1'])
