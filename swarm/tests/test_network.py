from .base import BaseTestCase, AMQPCase
from .fixtures import IFCONFIG_DATA

from swarm.stuff import Network, Node
from swarm.reports import IFConfigReport
from swarm.scenarios import on_event
from swarm.cluster import Cluster


class NetworkBaseTest(BaseTestCase):
    def test_crud(self):
        cluster = Cluster.instance()
        node = Node(hostname='testhost')
        cluster.store(node)
        on_event(IFConfigReport(node.oid, raw_data=IFCONFIG_DATA))
        network = Network(title='TestNetwork')
        virbr2 = node.get_host_nic('virbr2')
        network.add_host_nic(virbr2)
        self.assertTrue(virbr2.oid in network.host_nics)
        eth2 = node.get_host_nic('eth2')
        self.assertEqual(len(network.host_nics), 1)
        self.assertFalse(eth2.oid in network.host_nics) # only bridge should be added
