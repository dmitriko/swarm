
import uuid
import time

from tornado.options import options

from swarm.node.amqp import NodeAMQPClient
import pika

from swarm.manager.amqp import ManagerAMQPClient
from swarm.common.entities.event import Event

from .base import BaseTestCase


class AMQPCase(BaseTestCase):
    "Test manager-node RPC"

    def setUp(self):
        BaseTestCase.setUp(self)
        self.manager_oid = str(uuid.uuid1())
        self.node_oid = str(uuid.uuid1())
        self.manager = None
        self.node = None
        parameters = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=options.rpc_exchange, type='topic')
        channel.exchange_declare(exchange=options.events_exchange, type='topic')
        channel.exchange_declare(exchange=options.reports_exchange, type='topic')
        channel.queue_declare(queue=options.events_queue)
        channel.queue_bind(queue=options.events_queue, exchange=options.events_exchange,
                           routing_key='#')

    def tearDown(self):
        parameters = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_unbind(queue=options.events_queue, exchange=options.events_exchange,
                           routing_key='#')
        channel.exchange_delete(exchange=options.rpc_exchange)
        channel.exchange_delete(exchange=options.events_exchange)
        channel.exchange_delete(exchange=options.reports_exchange)
        channel.queue_delete(queue=options.events_queue)

        BaseTestCase.tearDown(self)

    def set_manager(self, msg_callback):
        self.manager = ManagerAMQPClient(msg_callback, self.manager_oid, self.io_loop)        
        self.manager.connect()

    def set_node(self, msg_callback):
        self.node = NodeAMQPClient(msg_callback, self.node_oid, self.io_loop)
        self.node.connect()
        

    def test_event_msg(self):

        def on_mngr_msg(body, queue, routing_key):
            event = Event.from_json(body)
            self.assertEqual(event.__class__.__name__,
                             'NodeOnlineEvent')
            self.assertEqual(event.node_oid, self.node_oid)
            self.stop()

        self.set_manager(on_mngr_msg)
        self.set_node(lambda *args: 1)

        self.wait()

    def __test_task_send(self):

        def on_mngr_msg(body, queue, routing_key):
            pass

        def on_node_msg(queue, channel, method, headers, body):
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
