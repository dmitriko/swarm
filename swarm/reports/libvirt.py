import re

from .base_report import BaseReport, SubprocessReport
        

class VirshListReport(SubprocessReport):
    "Result of virsh list"
    cmd = ['virsh', 'list']
    
    @property
    def parsed_data(self):
        """Return key where libvirt vm id is a key and 
        value is a dict with name and state

        """
        result = {}
        if not self.raw_data:
            return result
        for line in self.raw_data.split('\n'):
            match = re.search('(\d+)\s+(\w+)\s+(\w+)', line)
            if match:
                result[int(match.group(1))] = dict(name=match.group(2),
                                              state=match.group(3))
        return result


class VmXMLReport(BaseReport):
    "Report from libvirt with XML for VM"

    def _parse_simple_el(self, root, name):
        "Return text of element for given name"
        elm = root.find(name)
        if elm is not None:
            return elm.text
        return None

    def _get_nics(self, root):
        "Return list of dicts with info for vm nic interface"
        result = []
        for elm in root.findall('devices/interface'):
            nic = {}
            mac_el = elm.find('mac')
            if mac_el is not None:
                nic['mac'] = mac_el.attrib['address']
            bridge_el = elm.find('source')
            if bridge_el is not None:
                nic['bridge'] = bridge_el.attrib['bridge']
            target_el = elm.find('target')
            if target_el is not None:
                nic['target'] = target_el.attrib['dev']
            result.append(nic)
        return result

    def _get_disks(self, root):
        "Return list of pathes for disks" 
        return [x.attrib['file'] for x in root.findall('devices/disk/source')]

    @property
    def parsed_data(self):
        """Return dict with info about VM
        
        """
        from xml.etree import ElementTree as ET
        result = {}
        if not self.raw_data:
            return result
        root = ET.fromstring(self.raw_data)
        result['libvirt_id'] = root.attrib.get('id')
        for name in ['name', 'uuid', 'memory', 'vcpu']:
            value = self._parse_simple_el(root, name)
            if value:
                result[name] = value
        result['features'] = [x.tag for x in root.findall('features/*')]
        result['disks'] = self._get_disks(root)
        result['nics'] = self._get_nics(root)

        return result
        
        
        
