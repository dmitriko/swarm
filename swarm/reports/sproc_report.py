import re

from .base_report import SubprocessReport


class IFConfigReport(SubprocessReport):
    "Result of /sbin/ifconfig"
    cmd = ['/sbin/ifconfig']

    def parsed_data(self):
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

class DFReport(SubprocessReport):
    "Result of df -h from Node"
    cmd = ['df', '-h']
