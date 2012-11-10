""" Thread that perform a task a reports about """

from threading import Thread

from swarm.reports import TaskUpdated, TaskFailed, TaskSuccess
from swarm.utils.log import log


class TaskThreadWorker(Thread):
    "There where task is performed"
    def __init__(self, amqp_client, task):
        self.task = task
        self.amqp_client = amqp_client
        Thread.__init__(self)

    def publish_report(self, report_class):
        "Use client to send event via AMQP"
        self.amqp_client.publish_report(
            report_class.create(self.amqp_client.oid, task=self.task))

    def run(self):
        try:
            self.task.perform(self.amqp_client)
            self.publish_report(TaskSuccess)
        except Exception, exc:
            log.error("Error on task perform", exc_info=True)
            self.task.set(progress=100,
                          error=str(exc),
                          status='failed')
            self.publish_report(TaskFailed)

