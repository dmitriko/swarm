"Base class for various tasks"

import time
from copy import copy

from swarm.entity import Entity, ValidationError
from swarm.events import TaskUpdated

STATUSES = ['created', 'accepted', 'inprogress', 'failed', 'success']


class BaseTask(Entity):
    def __init__(self, performer, **kw):
        self.performer = performer
        self.status = kw.get('status', 'created')
        self.valid_period = kw.get('valid_period', 30) # sec
        self.progress = kw.get('progress', 0)
        self.result = kw.get('result')
        self.error = kw.get('error')
        Entity.__init__(self, **kw)

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

    def report(self, client):
        "Report about update"
        event = TaskUpdated(client.oid, copy(self))
        client.publish_event(event)
