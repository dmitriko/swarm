""" Base classes for UnitTest cases 
The tests require U have local version
of RabbitMQ up and running

"""

import os
import uuid
import shutil

from tornado.testing import AsyncTestCase
from tornado.options import parse_config_file, options

import pika

from swarm.config import define_common_options, define_node_options
from swarm.amqp.nclient import NodeAMQPClient
from swarm.amqp.mclient import ManagerAMQPClient
from swarm.entity import Entity
from swarm.cluster import Cluster
from swarm.stuff import Storage


DIR = os.path.realpath(os.path.dirname(__file__))


class BaseTestCase(AsyncTestCase):
    def setUp(self):
        AsyncTestCase.setUp(self)
        for key in options.keys():
            del options[key]
        define_common_options()
        define_node_options()
        parse_config_file(os.path.join(DIR, 'config_data.py'))
        self.init_storages()
        self.node_oid = str(uuid.uuid1())
        Cluster.instance().init()

    def init_storages(self):
        self.storage1_path = '/tmp/storage1'
        self.storage2_path = '/tmp/storage2'
        self.storage1_oid = Storage.ensure(self.storage1_path)
        self.storage2_oid = Storage.ensure(self.storage2_path)

    def tearDown(self):
        try:
            shutil.rmtree(self.storage1_path)
            shutil.rmtree(self.storage2_path)
        except:
            pass

class AMQPCase(BaseTestCase):
    "Test AMQP messaging"

    def setUp(self):
        BaseTestCase.setUp(self)
        self.manager_oid = str(uuid.uuid1())
        self.manager = None
        self.node = None
        parameters = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=options.rpc_exchange, type='topic')
        channel.exchange_declare(exchange=options.reports_exchange, 
                                 type='topic')
        channel.queue_declare(queue=options.reports_queue)

        channel.queue_bind(queue=options.reports_queue, 
                           exchange=options.reports_exchange,
                           routing_key='#')
        
    def tearDown(self):
        parameters = pika.ConnectionParameters('localhost')
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_unbind(queue=options.reports_queue, 
                             exchange=options.reports_exchange,
                             routing_key='#')
        channel.exchange_delete(exchange=options.rpc_exchange)
        channel.exchange_delete(exchange=options.reports_exchange)
        channel.queue_delete(queue=options.reports_queue)

        BaseTestCase.tearDown(self)
        
    def set_manager(self, *args, **kw):
        kw['oid'] = self.manager_oid
        kw['io_loop']  = self.io_loop
        self.manager = ManagerAMQPClient(*args, **kw)
        self.manager.connect()

    def set_node(self, *args, **kw):
        kw['oid'] = self.node_oid
        kw['io_loop']  = self.io_loop
        self.node = NodeAMQPClient(*args, **kw)
        self.node.connect()

    def entity_from_json(self, json_str):
        "Return Entity instance for given json str"
        return Entity.from_json(json_str)

        


