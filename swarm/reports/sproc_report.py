import re

from .base_report import SubprocessReport


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

        
class IFConfigReport(SubprocessReport):
    "Result of /sbin/ifconfig"
    cmd = ['/sbin/ifconfig']

    @property
    def parsed_data(self):
        """Return dict where nic name (like eth0) is a key
        and dict with various nic info is a value

        """
        result = {}
        if not  self.raw_data:
            return result

        for info in self.raw_data.split('\n\n'):

            nic = {}

            match = re.match('^(\S+).*$', info, re.M)
            if match:
                name = match.group(1)
            else:
                raise RuntimeError("Could not parse %s" % info)

            match = re.search(r'HWaddr\s+(\S+)', info)
            if match:
                nic['mac'] = match.group(1)
            
            match = re.search(r'inet addr:(\S+).*Mask:(\S+)',  info)
            if match:
                nic['inet_addr'] = match.group(1)
                nic['mask'] = match.group(2)

            match = re.search('RX bytes:(\d*).*TX bytes:(\d*)', info)
            if match:
                nic['rx_bytes'] = int(match.group(1))
                nic['tx_bytes'] = int(match.group(2))

            result[name] = nic

        return result


class BrctlShowReport(SubprocessReport):
    "Result of brctl show"
    cmd = ['brctl', 'show']

    @property
    def parsed_data(self):
        """Return dict where keys are bridge name,
        values is a lists with names of nics in this bridge

        """
        if not self.raw_data:
            return {}
        result = {}
        bridge_name = None
        nics = None
        for line in self.raw_data.split('\n'):
            if line.startswith('bridge name'):
                continue
            match = re.search(r'^(\S+)', line)
            if match:
                nics = []
                result[match.group(1)] = nics
            match = re.search(r'(\S+)$', line)
            if match:
                if nics is None:
                    raise RuntimeError("Could not parse %s" % self.raw_data)
                nics.append(match.group(1))
        return result


class DFReport(SubprocessReport):
    "Result of df -h from Node"
    cmd = ['df', '-h']
