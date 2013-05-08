"Main script to start manager process"

import uuid
import functools
import os

from tornado.options import options, parse_command_line, parse_config_file
from tornado.web import Application, RequestHandler, HTTPError
from tornado.ioloop import IOLoop

from swarm.cluster import Cluster
from swarm.entity import Entity
from swarm.config import define_common_options, define_manager_options
from swarm.utils.log import log, init_logging
from swarm.amqp.mclient import ManagerAMQPClient
from swarm.views import get_entity_view, vm_list_view
from swarm.scenarios.onevent import on_mngr_msg
from swarm import tasks


def HTTPBasic(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        import base64
        try:
            auth_type, auth_data = self.request.headers[
                "Authorization"].split()
            assert auth_type == "Basic"
            usr, pwd = base64.b64decode(auth_data).split(":", 1)
            if usr == options.user:
                assert pwd == options.password, 'wrong password'
            else:
                assert False, "no such user, %s" % usr
        except (KeyError, AssertionError), exc:
            log.warn(
                "No auth request %s, %s" % (
                    self.request.headers, str(exc)))
            self.set_header('WWW-Authenticate', 'Basic realm=VGDCloud')
            self.set_status(401)
            self.finish()
        else:
            return method(self, *args, **kwargs)
    return wrapper


class IPython(RequestHandler):
    def get(self):
        cluster = Cluster.instance()
        import IPython; IPython.embed()
        self.redirect('/')


class IndexHandler(RequestHandler):
    @HTTPBasic
    def get(self):
        self.render('page.html',
                    cmd=None,
                    view=None)
    @HTTPBasic
    def post(self):
        import IPython; IPython.embed()
        cmd = self.get_argument('cmd', '')
        cluster = Cluster.instance()
        view = None
        if cmd == 'vms':
            view = vm_list_view(
                cluster.entities_by_class('VmProcess'))
        entity = cluster.search(cmd)
        if entity:
            self.redirect('/%s' % entity.oid)
        self.render('page.html',
                    cmd=cmd,
                    view=view)
    

class EntityHandler(RequestHandler):
    @HTTPBasic
    def get(self, path):
        """Return view for entity 

        """
        
        entity = Cluster.instance().get(path)
        if not entity:
            raise HTTPError(404)
        self.render('entity.html', 
                    class_name = entity.__class__.__name__,
                    oid = entity.oid,
                    cmd = entity.oid,
                    table = get_entity_view(entity).get_html())
        

def get_app():
    import os
    static_path = os.path.join(os.path.dirname(__file__), 'static') 
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    return Application([(r'/', IndexHandler),
                        (r'/ipython', IPython),
                        (r'/([^/]+)', EntityHandler),
                        ],
                       debug=options.debug,
                       static_path=static_path,
                       template_path=template_path)


def load_fixtures(node_oid):
    "Load demo data for development"
    from swarm.scenarios import on_report
    from swarm.tests import fixtures
    from swarm.reports import (NodeOnlineReport, VmXMLReport, IFConfigReport,
                               BrctlShowReport, DFReport)
    log.debug('Loading test data')
    storage_oid = str(uuid.uuid4())
    on_report(NodeOnlineReport.create(node_oid,
                                      hostname='testhost',
                                      storages = [dict(
                    storage_oid=storage_oid, path='/home/vgdcloud/storage1')]))
                    
    on_report(IFConfigReport.create(node_oid,
                                    raw_data=fixtures.IFCONFIG_DATA))
    on_report(BrctlShowReport.create(node_oid,
                                     raw_data=fixtures.BRCTL_SHOW_DATA))
    on_report(VmXMLReport.create(node_oid, raw_data=fixtures.LIBVIRT_XML))
    on_report(DFReport.create(node_oid, raw_data=fixtures.DF_RAW))


def main():
    define_common_options()
    define_manager_options()
    parse_command_line()
    if options.config and os.path.exists(options.config):
        parse_config_file(options.config)
    init_logging()
    log.info("Starting application")
    manager_oid = options.oid or str(uuid.getnode())
    if options.on_test:
        load_fixtures(manager_oid)
    log.info("listen on %s:%s" % (options.http_host, options.http_port))
    ManagerAMQPClient(oid=manager_oid, on_msg_callback=on_mngr_msg).connect()
    get_app().listen(options.http_port)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()
