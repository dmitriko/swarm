from .base import AMQPCase
from .fixtures import IFCONFIG_DATA as RAW_DATA
from swarm.reports import IFConfigReport, NodeOnlineReport
from swarm.cluster import Cluster
from swarm.scenarios.onevent import on_mngr_msg as default_callback


class IFConfigReportCase(AMQPCase):

    def test_publish_ifconfig_report(self):

        def on_mngr_msg(client, body, routing_key):
            inst = self.entity_from_json(body)
            default_callback(client, body, routing_key)

            if isinstance(inst, NodeOnlineReport):
                self.node.publish_report(
                    IFConfigReport.create(self.node_oid, raw_data=RAW_DATA))

            if isinstance(inst, IFConfigReport):
                self.assertEqual(inst.raw_data, RAW_DATA)
                cluster = Cluster.instance()
                node = cluster.get(self.node_oid)
                self.assertTrue(node)
                self.assertEqual(node.get_host_nic('eth1').inet_addr,
                                 '10.0.1.1')
                self.assertEqual(node.get_host_nic('vnet0').rx_bytes,
                                 11546476)
                self.stop()

        self.set_manager(on_mngr_msg)
        self.set_node()

        self.wait()
