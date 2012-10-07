""" Base classes for UnitTest cases 
The tests require U have local version
of RabbitMQ up and running

"""

import os
import uuid

from tornado.testing import AsyncTestCase
from tornado.options import parse_config_file, options

import pika

from swarm.config import define_common_options
from swarm.amqp.nclient import NodeAMQPClient
from swarm.amqp.mclient import ManagerAMQPClient


DIR = os.path.realpath(os.path.dirname(__file__))


class BaseTestCase(AsyncTestCase):
    def setUp(self):
        AsyncTestCase.setUp(self)
        define_common_options()
        parse_config_file(os.path.join(DIR, 'config_data.py'))

    def tearDown(self):
        for key in options.keys():
            del options[key]


class AMQPCase(BaseTestCase):
    "Test AMQP messaging"

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
        

        


