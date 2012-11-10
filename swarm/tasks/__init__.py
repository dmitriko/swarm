
from .base import BaseTask

class TestConnectTask(BaseTask):
    "Ensure we have connection with Node"
    def perform(self, amqp_client):
        BaseTask.perform(self, amqp_client)
        self.set(status='accepted')
        self.report(amqp_client, self.to_dict())
        self.set(progress=50, status='inprogress')
        self.report(amqp_client, self.to_dict())
        self.set(status='success')
        self.set(result='ok')
