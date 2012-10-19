import uuid

from .fixtures import BRCTL_SHOW_DATA, IFCONFIG_DATA
from .base import BaseTestCase

from swarm.scenarios.onevent import on_event
from swarm.reports import BrctlShowReport, IFConfigReport
from swarm.events import NodeOnlineEvent
from swarm.cluster import Cluster


class BrctlShowCase(BaseTestCase):

    def test_report_arrived(self):
        node_oid = str(uuid.uuid1())
        on_event(NodeOnlineEvent(node_oid))
        on_event(IFConfigReport(node_oid, raw_data=IFCONFIG_DATA))
        on_event(BrctlShowReport(node_oid, raw_data=BRCTL_SHOW_DATA))
        cluster = Cluster.instance()
        node = cluster.get(node_oid)
        self.assertTrue(node)
        eth2 = node.get_host_nic('eth2')
        self.assertTrue(eth2)
        self.assertEqual(eth2.bridge, 'virbr2')
