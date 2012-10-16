
from .base_report import SubprocessReport


class IFConfigReport(SubprocessReport):
    "Result of /sbin/ifconfig"
    cmd = ['/sbin/ifconfig']


class DFReport(SubprocessReport):
    "Result of df -h from Node"
    cmd = ['df', '-h']
