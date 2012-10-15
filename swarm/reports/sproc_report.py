
from .base_report import SubprocessReport


class IFConfigReport(SubprocessReport):
    "Result of /sbin/ifconfig"
    def cmd(self):
        return ['/sbin/ifconfig']


class DFReport(SubprocessReport):
    "Result of df -h from Node"
    def cmd(self):
        return ['df', '-h']
