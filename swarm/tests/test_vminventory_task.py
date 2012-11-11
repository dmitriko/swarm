"Test Task sending from manager to node an reports back"

from swarm.entity import Entity
from swarm.reports import TaskUpdated, TaskSuccess
from swarm.tasks import VMInventoryTask
from swarm.tasks.worker import TaskThreadWorker
from swarm.scenarios import on_report
from swarm.reports import IFConfigReport
from swarm.cluster import Cluster

from .base import AMQPCase
from .fixtures import IFCONFIG_DATA


class TaskSendCase(AMQPCase):

    def test_task_send(self):

        self.mngr_msg_count = 0

        def on_mngr_msg(client, body, routing_key):
            report = Entity.from_json(body)
            on_report(report)
            self.assertEqual(report.reporter_oid, self.node_oid)
            if report.__class__.__name__ == 'NodeOnlineReport':
                on_report(IFConfigReport.create(self.node_oid, 
                                                raw_data=IFCONFIG_DATA))
                client.send_task(VMInventoryTask(node_oid=self.node_oid))
            if report.__class__.__name__ == 'VmXMLReport':
                cluster = Cluster.instance()
                vm_config = cluster.entities_by_class('VmConfig')[0]
                self.assertEqual(vm_config.oid, 'c2127a40-eb4c-4e3c-af5b-ab455fd8bb40')
                self.stop()

        def on_node_msg(client, body, routing_key):
            task = Entity.from_json(body)
            self.assertEqual(task.node_oid, self.node_oid)
            worker = TaskThreadWorker(client, task)
            worker.start()
            
        self.set_manager(on_mngr_msg)
        self.set_node(on_node_msg)
        self.wait()
