"Main script to start manager process"

from tornado.options import options, parse_command_line
from tornado.web import Application, RequestHandler
from tornado.ioloop import IOLoop


class VMListHandler(RequestHandler):
    def get(self):
        self.render('vmlist.html')


def get_app():
    import os
    static_path = os.path.join(os.path.dirname(__file__), 'static') 
    template_path = os.path.join(os.path.dirname(__file__), 'templates')
    return Application([(r'/', VMListHandler)], 
                       static_path=static_path,
                       template_path=template_path)


if __name__ == '__main__':
    get_app().listen(8443)
    IOLoop.instance().start()
