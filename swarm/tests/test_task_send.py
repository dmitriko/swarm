"Test Task sending from manager to node an reports back"

from swarm.entity import Entity
from swarm.reports import TaskUpdated, TaskSuccess
from swarm.tasks import TestConnectTask
from swarm.tasks.worker import TaskThreadWorker
from swarm.scenarios import on_report

from .base import AMQPCase


class TaskSendCase(AMQPCase):

    def test_task_send(self):

        self.mngr_msg_count = 0

        def on_mngr_msg(client, body, routing_key):

            self.mngr_msg_count += 1

            report = Entity.from_json(body)
            on_report(report)
            self.assertEqual(report.reporter_oid, self.node_oid)

            if self.mngr_msg_count == 1: # got NodeOnline Report
                self.assertEqual(report.__class__.__name__, 'NodeOnlineReport')
                client.send_task(TestConnectTask(node_oid=self.node_oid))

            if self.mngr_msg_count == 2:
                # TaskUpdated reports
                self.assertEqual(report.task.node_oid, self.node_oid)
                self.assertEqual(report.task.status, 'accepted')

            if self.mngr_msg_count == 3:
                self.assertEqual(report.task.status, 'inprogress')
                self.assertEqual(report.task.progress, 50)

            if self.mngr_msg_count == 4:
                self.assertEqual(report.__class__.__name__, 'TaskSuccess')
                self.assertEqual(report.task.status, 'success')
                self.stop()

        def on_node_msg(client, body, routing_key):
            task = Entity.from_json(body)
            self.assertEqual(task.node_oid, self.node_oid)
            worker = TaskThreadWorker(client, task)
            worker.start()
            
        self.set_manager(on_mngr_msg)
        self.set_node(on_node_msg)
        self.wait()
