""" Base classes for work with AMQP """

import socket

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import options

import pika
from pika.adapters import BaseConnection
from pika.adapters.select_connection import SelectConnection
from pika.adapters.tornado_connection import TornadoConnection

from ..utils.log import log


def get_conn_params():
    "Return pika connection parameters"
    credentials = pika.PlainCredentials(options.amqp_user,
                                        options.amqp_password)
    return pika.ConnectionParameters(host=options.amqp_host,
                                     port=options.amqp_port,
                                     virtual_host=options.amqp_vhost,
                                     credentials=credentials)


class AMQPConnection(TornadoConnection):
    """Provide pika.TornadoConnection but with ability to set
    ioloop excplicitly for testing etc

    """
    def __init__(self, parameters, on_open, io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        TornadoConnection.__init__(self, parameters, on_open)

    def _adapter_connect(self, host, port):
        "Connect to the given host and port"
        BaseConnection._adapter_connect(self, host, port)
        self.ioloop = self.io_loop
        self.ioloop.add_handler(self.socket.fileno(),
                                self._handle_events,
                                self.event_state)
        log.debug("adapter connecting to RabbitMQ %s %s" % (host, port))
        self._on_connected()
   

class AMQPClient(object):
    "Connect to RabbitMQ and create a channel"

    def __init__(self, on_msg_callback=None, oid=None, io_loop=None,
                 on_channel_created=None):
        self.oid = oid or options.oid
        self.io_loop = io_loop
        self.on_msg_callback = on_msg_callback
        self.connection = None
        self.channel = None
        self._on_channel_created = on_channel_created
        self.checker = PeriodicCallback(self._check_connection, 1000)

    def connect(self):
        "Connect to RabbitMQ"
        log.debug("Connecting to RabbitMQ")
        if self.connection:
            return
        self.connection = AMQPConnection(
            get_conn_params(),
            self.on_connected,
            io_loop=self.io_loop)

    def on_connected(self, connection):
        "Create a channel just after connected"
        log.debug("%s is established" % connection)
        self.connection.channel(self.on_channel_created)
        self.checker.start()

    def on_channel_created(self, channel):
        "Implement in subclasses"
        log.debug("%s is established" % channel)
        self.channel = channel
        if self._on_channel_created:
            self._on_channel_created(channel)

    def _check_connection(self):
        "Restablish connection to server if we lost it"
        if self.connection:
            try:
                self.connection.socket.fileno()
            except socket.error, exc:
                log.debug("lost connection to RabbitMQ, %s" % str(exc))
                self.checker.stop()
                self.connection = None
                self.connect()

    def get_consumer_callback(self, queue_name):
        "Return func to use in channel.basic_consume"
        from functools import partial

        def consumer_callback(queue_name, channel, method, headers, body):
            "Ack message and call on_msg_callback if exists"
            if self.on_msg_callback:
                channel.basic_ack(delivery_tag=method.delivery_tag)
                self.on_msg_callback(self, body, queue_name, method.routing_key)
            else:
                log.warn("No message callback set in %s" % self)
            
        return partial(consumer_callback, queue_name)
