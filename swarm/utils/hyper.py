"Libvirt and mock connection to manager VM"

from tornado.options import options

from swarm.tests import fixtures


class MockDomain(object):

    def __init__(self, _id):
        self._id = _id

    def XMLDesc(self, _):
        return fixtures.LIBVIRT_XML


class MockLibvirtConn(object):

    def listDomainsID(self):
        return [1]

    def lookupByID(self, _id):
        return MockDomain(_id)


def get_hypervisor():
    "Return open libvirt connection or mock depends on options.on_test"
    if options.on_test:
        return MockLibvirtConn()
    else:
        return get_libvirt_conn()


def get_libvirt_conn():
    import libvirt
    return libvirt.open('qemu:///system')
    
