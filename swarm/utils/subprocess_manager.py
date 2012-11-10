"""Run subprocess commands from reports """

import time
from subprocess import Popen, PIPE
from functools import partial

from tornado.ioloop import IOLoop

from swarm.entity import Entity
from swarm.utils.log import log


class SubprocessManager(object):

    def __init__(self, client, io_loop=None):
        "client is NodeAMQPClient"
        self.client = client
        self._reports = {} # key is a report class, value is an interval
        self.io_loop = io_loop or client.io_loop

    def add_report(self, report_class, interval):
        "Add report class and interval in seconds"
        assert issubclass(report_class, Entity)
        assert isinstance(interval, int)
        self._reports[report_class] = interval

    def report_done(self, report_class, data):
        log.debug("data collected for %s" % report_class)
        report = report_class.create(self.client.oid, raw_data=data)
        self.client.publish_report(report)

    def report_failed(self, report_class, err_data):
        from swarm.events import ReportCollectFailed
        self.client.publish_report(ReportCollectFailed(
                self.client.oid, report=report_class.__name__,
                error=err_data))
        

    def wait_and_publish(self, proc, report_class, interval):
        log.debug("wait for %s collect result" % report_class)
        returncode = proc.poll()
        if returncode is None:
            self.io_loop.add_timeout(
                time.time() + 1, 
                partial(self.wait_and_publish, proc, report_class, interval))
            return

        if returncode == 0:
            data = proc.communicate()[0]
            self.report_done(report_class, data)
        else:
            err_data = proc.communicate()[1]
            self.report_failed(self, report_class, err_data)
        
        self.io_loop.add_timeout(
            time.time() + interval, 
            partial(self.start_report_process, report_class, interval))                     
        
    def start_report_process(self, report_class, interval):
        log.debug("Start reporting by %s" % report_class)
        proc = Popen(report_class.cmd, stderr=PIPE, stdout=PIPE)
        self.io_loop.add_callback(
            partial(self.wait_and_publish, proc, report_class, interval))
        
    def start(self):
        "Start performing data collection and sending"
        for report_class, interval in self._reports.items():
            self.start_report_process(report_class, interval)
        log.debug("SubrocessManager started with %s reports" % (
                str(self._reports.keys())))
