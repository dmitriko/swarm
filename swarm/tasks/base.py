"Base class for various tasks"

import time
from copy import copy

from swarm.entity import Entity, ValidationError
from swarm.reports import TaskUpdated
from swarm import fields
from swarm.utils.log import log

STATUSES = ['created', 'accepted', 'inprogress', 'failed', 'success']


class BaseTask(Entity):

    node_oid = fields.BaseField('node_oid', required=True)
    status = fields.BaseField('status', choices=STATUSES, default='created')
    valid_period = fields.BaseField('valid_period', default=30)
    progress = fields.BaseField('progress', default=0)
    result = fields.BaseField('result')
    error = fields.BaseField('error')

    @property
    def is_acceptable(self):
        "Return True if Task can be accepted by node"
        if self.status == 'created':
            if (time.time() - self.created) <= self.valid_period:
                return True
        return False
        
    def validate(self):
        "Check parameters set"
        if self.status not in STATUSES:
            raise ValidationError(
                "status is %s but should be in %s" % (
                    self.status, STATUSES))

    def perform(self, amqp_client):
        "Code that performs a real job"
        if not self.is_acceptable:
            raise RuntimeError("%s is expired")
        
    def on_fail(self):
        "Todo on fail"
        pass

    def report(self, client, info):
        "Report aboute task update"
        event = TaskUpdated.create(client.oid, task=info)
        client.publish_report(event)
