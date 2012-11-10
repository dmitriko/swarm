from .base import BaseTestCase

from .fixtures import LIBVIRT_XML

from swarm.reports import VmXMLReport, NodeOnlineReport
from swarm.scenarios import on_report
from swarm.cluster import Cluster


class VmXMLCase(BaseTestCase):
    def test_parsing(self):
        report = VmXMLReport.create(self.node_oid, raw_data=LIBVIRT_XML)
        data = report.parsed_data
        self.assertEqual('c2127a40-eb4c-4e3c-af5b-ab455fd8bb40', data['uuid'])
        self.assertEqual(data['name'], 'usbvm')
        self.assertEqual(data['libvirt_id'], '1')
        self.assertEqual(data['vcpu'], '4')
        self.assertEqual(data['memory'], '2048000')

        self.assertEqual(len(data['features']), 3)
        self.assertEqual(data['features'][1], 'apic')
        self.assertEqual(len(data['disks']), 2)
        self.assertEqual(data['disks'][0], '/home/vgd/storage2/usbvm_d0.qcow2')
        self.assertEqual(len(data['nics']), 1)
        nic = data['nics'][0]
        self.assertEqual(nic['mac'], '52:54:00:fe:49:df')
        self.assertEqual(nic['bridge'], 'virbr2')
        self.assertEqual(nic['target'], 'vnet0')

    def test_vmxml_report_updates_cluster(self):
        on_report(NodeOnlineReport.create(self.node_oid, hostname='testhost'))
        report = VmXMLReport.create(self.node_oid, raw_data = LIBVIRT_XML)
        on_report(report)
        cluster = Cluster.instance()
        vms = cluster.entities_by_class('VmProcess')
        self.assertEqual(len(vms), 1)
        node = cluster.get(self.node_oid)
        self.assertEqual(len(node.get_vm_procs()), 1)
        vm_proc = vms[0]
        self.assertEqual(vm_proc.vm_config.nics[0].target, 'vnet0')
