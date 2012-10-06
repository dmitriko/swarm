"AMQP client to communicate from Node to AMQP server"

from tornado.options import options
from tornado import gen

from swarm.common.amqp import AMQPClient
from swarm.utils.log import log


class ManagerAMQPClient(AMQPClient):

    @gen.engine
    def on_channel_created(self, channel):

        AMQPClient.on_channel_created(self, channel)

        yield gen.Task(channel.exchange_declare,
                       exchange=options.rpc_exchange, type='topic')
        yield gen.Task(channel.exchange_declare,
                       exchange=options.events_exchange, type='topic')
        yield gen.Task(channel.exchange_declare,
                       exchange=options.reports_exchange, type='topic')
        yield gen.Task(channel.queue_declare, queue=options.events_queue)

        log.debug("Exchanges for Manager are declared")

        yield gen.Task(channel.queue_bind,
                       queue=options.events_queue, 
                       exchange=options.events_exchange,
                       routing_key='#')

        log.debug("events queue %s is bound" % options.events_queue)

        self.channel.basic_consume(
            consumer_callback=self.get_consumer_callback(options.events_queue),
            queue=options.events_queue,
            no_ack=False)
        
