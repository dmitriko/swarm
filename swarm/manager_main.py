"Main script to start manager process"

from tornado.options import options, parse_command_line
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop

from swarm.cluster import Cluster
from swarm.config import define_common_options
from swarm.utils.log import log, init_logging
from swarm.amqp.mclient import ManagerAMQPClient


class BaseHandler(RequestHandler):
    def render(self, template, **kw):
        def get_link(obj, title):
            return "<a href='/entity/%s'>%s</a>" % (obj.oid, title)
        kw['get_link'] = get_link
        RequestHandler.render(self, template, **kw)


class VMListHandler(RequestHandler):
    def get(self):
        cluster = Cluster.instance()
        self.render('vmlist.html',  
                    vm_list = cluster.entities_by_class('VmProcess'))


def get_app():
    import os
    static_path = os.path.join(os.path.dirname(__file__), 'static') 
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    return Application([(r'/', VMListHandler)], 
                       static_path=static_path,
                       template_path=template_path)


def load_fixtures():
    "Load demo data for development"
    import uuid
    from swarm.scenarios import on_report
    from swarm.tests import fixtures
    from swarm.reports import (NodeOnlineReport, VmXMLReport, IFConfigReport,
                               BrctlShowReport)
    log.debug('Loading test data')

    node_oid = str(uuid.uuid4())

    on_report(NodeOnlineReport.create(node_oid,
                                      hostname='testhost'))
    on_report(IFConfigReport.create(node_oid,
                                    raw_data=fixtures.IFCONFIG_DATA))
    on_report(BrctlShowReport.create(node_oid,
                                     raw_data=fixtures.BRCTL_SHOW_DATA))
    on_report(VmXMLReport.create(node_oid, raw_data=fixtures.LIBVIRT_XML))


if __name__ == '__main__':
    define_common_options()
    parse_command_line()
    init_logging()
    if options.on_test:
        load_fixtures()
    get_app().listen(options.http_port)
    IOLoop.instance().start()
