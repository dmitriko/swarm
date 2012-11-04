from .base import AMQPCase
from swarm.reports import IFConfigReport
from swarm.utils import SubprocessManager


class SubProccessMngrCase(AMQPCase):

    def test_sprocess_manager(self):

        def on_mngr_msg(client, body, routing_key):
            inst = self.entity_from_json(body)
            if isinstance(inst, IFConfigReport):
                self.stop()
            if inst.__class__.__name__ == 'NodeOnlineEvent':
                smanager = SubprocessManager(self.node)
                smanager.add_report(IFConfigReport, 15)
                smanager.start()

        self.set_manager(on_mngr_msg)
        self.set_node()

        self.wait()
            
