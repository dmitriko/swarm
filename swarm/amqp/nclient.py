"AMQP client to communicate from Node to AMQP server"

from Queue import Queue

from tornado.options import options
from tornado import gen

import pika

from swarm.amqp.base import AMQPClient
from swarm.utils.log import log
from swarm.events import NodeOnlineEvent


class NodeAMQPClient(AMQPClient):
    
    def __init__(self, *args, **kw):
        AMQPClient.__init__(self, *args, **kw)
        self.events_to_send = Queue()

    @gen.engine
    def on_channel_created(self, channel):
        AMQPClient.on_channel_created(self, channel)
        frame = yield gen.Task(channel.queue_declare, 
                               exclusive=True, auto_delete=True) 
        self.rpc_queue = frame.method.queue

        yield gen.Task(channel.queue_bind,
                       exchange=options.rpc_exchange,
                       routing_key=self.oid,
                       queue=self.rpc_queue)

        log.debug("rpc_queue %s for node %s is created" % (
                self.rpc_queue, self.oid))

        self.publish_event(NodeOnlineEvent(self.oid))

        self.channel.basic_consume(self.get_consumer_callback(self.rpc_queue),
                                   queue=self.rpc_queue)

    def publish_event(self, event):
        "Put event to queue and transfer control to main thread"
        self.events_to_send.put(event)
        self.io_loop.add_callback(self.process_events_queue)

    def process_events_queue(self):
        "Get Event from queue and publish it"
 
        event = self.events_to_send.get()

        self.channel.basic_publish(
            body=event.to_json(),
            exchange=options.events_exchange,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=1),
            routing_key="%s.%s" % (self.oid, event.__class__.__name__))

        log.debug("Event %s is published" % (event.to_json()))
