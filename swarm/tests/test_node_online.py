from swarm.entity import Entity
from swarm.scenarios.onevent import on_mngr_msg as default_mngr_callback
from swarm.cluster import Cluster
from swarm.events import NodeOnlineEvent
from swarm.stuff import Node

from .base import AMQPCase


class NodeManagerCommCase(AMQPCase):

    def test_node_online_update_cluster(self):
        def on_mngr_msg(client, body, routing_key):
            default_mngr_callback(client, body, routing_key)
            event = Entity.from_json(body)
            if isinstance(event, NodeOnlineEvent):
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
                             'NodeOnlineEvent')
            self.assertEqual(event.node_oid, self.node_oid)
            self.stop()

        self.set_manager(on_mngr_msg)

        self.set_node(lambda *args: 1)

        self.wait()
