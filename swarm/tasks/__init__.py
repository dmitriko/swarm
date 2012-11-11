
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


class VMInventoryTask(BaseTask):
    """Send VmXMLReport for every running 
    VM on host

    """

    def perform(self, client):
        from swarm.reports import VmXMLReport
        from swarm.utils.hyper import get_hypervisor

        BaseTask.perform(self, client)
        self.set(status='accepted')
        self.report(client, self.to_dict())
        hyper = get_hypervisor()
        for libvirt_id in hyper.listDomainsID():
            domain = hyper.lookupByID(libvirt_id)
            report = VmXMLReport.create(client.oid,
                                        raw_data=domain.XMLDesc(0))
            client.publish_report(report)

    
