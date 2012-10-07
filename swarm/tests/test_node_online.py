from swarm.entity import Entity

from .base import AMQPCase


class NodeManagerCommCase(AMQPCase):

    def test_node_online_event(self):

        def on_mngr_msg(client, body, queue, routing_key):
            event = Entity.from_json(body)
            self.assertEqual(event.__class__.__name__,
                             'NodeOnlineEvent')
            self.assertEqual(event.node_oid, self.node_oid)
            self.stop()

        self.set_manager(on_mngr_msg)

        self.set_node(lambda *args: 1)

        self.wait()
