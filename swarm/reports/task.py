from swarm.reports.base_report import BaseReport
from swarm import fields


class TaskReport(BaseReport):
    task = fields.BaseField('task')

class TaskUpdated(TaskReport): pass

class TaskFailed(TaskReport): pass

class TaskSuccess(TaskReport): pass
