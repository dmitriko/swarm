"Test Task sending from manager to node an reports back"

from swarm.entity import Entity
from swarm.events import TaskUpdated, TaskSuccess
from swarm.tasks import TestConnectTask
from swarm.tasks.worker import TaskThreadWorker

from .base import AMQPCase


class TaskSendCase(AMQPCase):

    def test_task_send(self):

        self.mngr_msg_count = 0

        def on_mngr_msg(client, body, routing_key):

            self.mngr_msg_count += 1

            event = Entity.from_json(body)
            self.assertEqual(event.reporter, self.node_oid)

            if self.mngr_msg_count == 1: # got NodeOnline Event
                self.assertEqual(event.__class__.__name__, 'NodeOnlineEvent')
                client.send_task(TestConnectTask(self.node_oid))

            if self.mngr_msg_count == 2:
                # TaskUpdated events
                self.assertEqual(event.task.performer, self.node_oid)
                self.assertEqual(event.task.status, 'accepted')

            if self.mngr_msg_count == 3:
                self.assertEqual(event.task.status, 'inprogress')
                self.assertEqual(event.task.progress, 50)

            if self.mngr_msg_count == 4:
                self.assertEqual(event.__class__.__name__, 'TaskSuccess')
                self.assertEqual(event.task.status, 'success')
                self.stop()

        def on_node_msg(client, body, routing_key):
            task = Entity.from_json(body)
            self.assertEqual(task.performer, self.node_oid)
            worker = TaskThreadWorker(client, task)
            worker.start()
            
        self.set_manager(on_mngr_msg)
        self.set_node(on_node_msg)
        self.wait()
