from .base import BaseTestCase

from .fixtures import LIBVIRT_XML

from swarm.reports import VmXMLReport


class VmXMLCase(BaseTestCase):
    def test_parsing(self):
        report = VmXMLReport(self.node_oid, LIBVIRT_XML)
        data = report.parsed_data
        self.assertEqual('c2127a40-eb4c-4e3c-af5b-ab455fd8bb40', data['uuid'])
        self.assertEqual(data['name'], 'usbvm')
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
