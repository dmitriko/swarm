"AMQP client to communicate from Node to AMQP server"

from Queue import Queue

from tornado.options import options
from tornado import gen

import pika

from swarm.amqp.base import AMQPClient
from swarm.utils.log import log
from swarm.scenarios.onevent import on_node_started


class NodeAMQPClient(AMQPClient):
    
    def __init__(self, *args, **kw):
        AMQPClient.__init__(self, *args, **kw)
        self.reports_to_send = Queue()

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

        self.channel.basic_consume(self.get_consumer_callback(self.rpc_queue),
                                   queue=self.rpc_queue)
        on_node_started(self)

    def publish_report(self, report):
        "Put report to queue and transfer control to main thread"
        self.reports_to_send.put(report)
        self.io_loop.add_callback(self.process_reports_queue)

    def process_reports_queue(self):
        "Get Report from queue and publish it"
        report = self.reports_to_send.get()
        self.publish_entity(report, options.reports_exchange)


    def publish_entity(self, entity, exchange):
        self.channel.basic_publish(
            body=entity.to_json(),
            exchange=exchange,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=1),
            routing_key="%s.%s" % (self.oid, entity.__class__.__name__))

        log.debug("%s is published" % (entity.to_json()))
