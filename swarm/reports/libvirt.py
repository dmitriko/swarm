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

