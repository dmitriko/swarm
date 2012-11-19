from swarm.entity import Entity
from swarm.scenarios.onevent import on_mngr_msg as default_mngr_callback
from swarm.cluster import Cluster
from swarm.reports import NodeOnlineReport
from swarm.stuff import Node


from .base import AMQPCase, BaseTestCase


class NodeManagerCommCase(AMQPCase):

    def test_node_online_update_cluster(self):
        def on_mngr_msg(client, body, routing_key):
            default_mngr_callback(client, body, routing_key)
            event = Entity.from_json(body)
            if isinstance(event, NodeOnlineReport):
                node = Cluster.instance().get(self.node_oid)
                self.assertEqual(len(node.storages), 2)
                for mount_point in node.storages:
                    if mount_point.storage_oid == self.storage1_oid:
                        self.assertEqual(mount_point.path, 
                                         self.storage1_path)
                self.stop()

        self.set_manager(on_mngr_msg)
        self.set_node()
        self.wait()
        cluster = Cluster.instance()
        node = cluster.get(self.node_oid)
        self.assertTrue(isinstance(node, Node))

        

    def test_node_online_event(self):

        def on_mngr_msg(client, body, routing_key):
            event = Entity.from_json(body)
            self.assertEqual(event.__class__.__name__,
                             'NodeOnlineReport')
            self.assertEqual(event.node_oid, self.node_oid)
            self.stop()

        self.set_manager(on_mngr_msg)

        self.set_node(lambda *args: 1)

        self.wait()


class NodeUpdateCase(BaseTestCase):
    def test_update(self):
        cluster = Cluster.instance()
        node = Node(oid=self.node_oid,
                    hostname='hostname')
        cluster.store(node)
        node.vm_procs = dict(a='dummy')
        self.assertEqual(cluster.get(self.node_oid).vm_procs['a'],
                         'dummy')
        cluster.store(Node(oid=self.node_oid,
                           hostname='hostname'))
        self.assertEqual(cluster.get(self.node_oid).vm_procs['a'],
                         'dummy')
