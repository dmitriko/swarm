""" Base classes for UnitTest cases 
The tests require U have local version
of RabbitMQ up and running

"""

from tornado.testing import AsyncTestCase
from tornado.options import parse_config_file, options

from swarm.config import define_common_options
import os

DIR = os.path.realpath(os.path.dirname(__file__))


class BaseTestCase(AsyncTestCase):
    def setUp(self):
        AsyncTestCase.setUp(self)
        define_common_options()
        parse_config_file(os.path.join(DIR, 'config_data.py'))

    def tearDown(self):
        for key in options.keys():
            del options[key]

        


