import uuid
import socket
import time
import os
from functools import partial

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.options import options, parse_command_line, parse_config_file
from tornado.web import Application, HTTPError, url, RequestHandler
from tornado.websocket import WebSocketHandler

from swarm.amqp.nclient import NodeAMQPClient
from swarm.utils.log import log, init_logging
from swarm.config import define_common_options, define_node_options
from swarm.entity import Entity
from swarm.tasks.base import BaseTask
from swarm.utils import SubprocessManager
from swarm.reports import (NodeOnlineReport, IFConfigReport, BrctlShowReport,
                           DFReport)
from swarm.tasks import VMInventoryTask
from swarm.tasks.worker import TaskThreadWorker
from swarm.scenarios.onevent import on_node_started

class NoVNCHandler(RequestHandler):
    def get(self, vm_uuid):
        return self.render('novnc.html', vm_uuid=vm_uuid)


class NoVNCWebSocketHandler(WebSocketHandler):
    "Proxy websocket traffic to socket"

    def open(self, vm_uuid):
        "Browser connected"
        log.debug("Open web socket connection for %s" % vm_uuid)
        self.vm_uuid = vm_uuid
        self.stream = self.get_stream()

    def on_message(self, msg):
        "Handle message from browser"
        from base64 import b64decode
        self.stream.write(b64decode(msg))
     
    def on_close(self, *args):
        "Browser closed connection"
        pass

    def get_vnc_port(self):
        "Return VNC port number"
        import commands
        import re
        out = commands.getoutput(
            'virsh -c qemu:///system vncdisplay %s' % self.vm_uuid)
        match = re.search(':(\d)+', out)
        if not match:
            log.error("Coulg not get vnc port, %s" % out)
            raise HTTPError(404)
        return int(match.group(1))

    def get_stream(self):
        "Return IOStream or SSLIOstream to VNC server"
        import socket
        import commands
        from tornado.iostream import IOStream
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        stream = IOStream(sock)
        stream.set_close_callback(self.on_close)
        stream.connect(
            ('127.0.0.1', self.get_vnc_port()), self.connected_to_vnc)
        return stream

    def on_vnc_data(self, data):
        "Proxy VNC data to browser"
        from base64 import b64encode
        self.write_message(b64encode(data))

    def connected_to_vnc(self):
        "Start reading from VNC server"
        self.stream.read_until_close(callback=self.on_close,
                                streaming_callback=self.on_vnc_data)


def get_app():
    import os
    static_path = os.path.join(os.path.dirname(__file__), 'static') 
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    return Application([url(r'/vmconsole/([^/]+)', NoVNCHandler),
                        url(r'/wsocket/([^/]+)', NoVNCWebSocketHandler)], 
                       static_path=static_path,
                       template_path=template_path,
                       debug=True)

def vm_inventory(client):
    log.debug('Inventory VMs')
    task = VMInventoryTask(node_oid=client.oid)
    worker = TaskThreadWorker(client, task)
    worker.start()


def channel_created(client):
    log.debug("%s to RabbitMQ is created" % client.channel)
    on_node_started(client)
    smanager = SubprocessManager(client)
    smanager.add_report(IFConfigReport, 30)
    smanager.add_report(BrctlShowReport, 300)
    smanager.add_report(DFReport, 300)
    smanager.start()
    heartbeat = PeriodicCallback(partial(on_node_started, client),
                                 15000)
    heartbeat.start()
    client.io_loop.add_timeout(time.time() + 15,
                               partial(vm_inventory, client))
                               


def on_msg(client, body, routing_key):
    try:
        entity = Entity.from_json(body)
        assert isinstance(entity, BaseTask)
        worker = TaskThreadWorker(client, entity)
        worker.start()
    except Exception:
        log.error("on msg processing", exc_info=True)


def main():
    define_common_options()
    define_node_options()
    parse_command_line()
    if options.config and os.path.exists(options.config):
        parse_config_file(options.config)
    init_logging()
    node_oid = options.oid or str(uuid.getnode())
    client = NodeAMQPClient(oid=node_oid, 
                            on_msg_callback=on_msg,
                            on_channel_created=channel_created)
    client.connect()
    IOLoop.instance().start()


if __name__ == '__main__':
    main()


