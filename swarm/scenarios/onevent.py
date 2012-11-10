"React on Event(Report) arrived to Manager"


from swarm.entity import Entity
from swarm.reports import IFConfigReport, BrctlShowReport, VmXMLReport, NodeOnlineReport
from swarm.cluster import Cluster
from swarm.stuff import Node, HostNic, Storage, VmProcess, VmConfig, VmNic, StoragePoint


def on_mngr_msg(client, body, routing_key):
    from swarm.reports.base_report import BaseReport
    entity = Entity.from_json(body)
    if isinstance(entity, BaseReport):
        return on_report(entity)


def on_node_started(client):
    "Use it only in node context"
    import socket
    report = NodeOnlineReport.create(client.oid, 
                                    hostname=socket.gethostname())
    report.storages = [x.to_dict() for x in Node.get_storage_points(client)]
    client.publish_report(report)


def on_report(report):
    if isinstance(report, NodeOnlineReport):
        return on_node_online(report)
    if isinstance(report, IFConfigReport):
        return on_ifconfig(report)
    if isinstance(report, BrctlShowReport):
        return on_brctl_show(report)
    if isinstance(report, VmXMLReport):
        return on_vmxml(report)


def on_report_from_offline_node(report):
    """Handle situation when we got any report from 
    node and we have no any info about that node

    """
    raise RuntimeError("Report %s for offline node %s" % (
            report, report.node_oid))
    

def on_vmxml(report):
    "Procedures on libvirt xml report"
    cluster = Cluster.instance()
    node = cluster.get(report.node_oid)
    if node is None:
        return on_report_from_offline_node(report)
    data = report.parsed_data
    nics = []
    for nic in data['nics']:
        nics.append(VmNic(**nic))
    vm_config = VmConfig(oid=data['uuid'],
                         vcpu=data['vcpu'],
                         memory=data['memory'],
                         name=data['name'],
                         features=data['features'],
                         libvirt_xml=report.raw_data,
                         nics=nics)
    cluster.store(vm_config)
    if data.get('libvirt_id'):
        node.update_vm_process(data['libvirt_id'], vm_config)


def on_node_online(report):
    from swarm.stuff import Storage
    cluster = Cluster.instance()
    node = Node(oid=report.node_oid, storages=report.storages, hostname=report.hostname)
    cluster.store(node)


def on_brctl_show(report):
    cluster = Cluster.instance()
    node = cluster.get(report.node_oid)
    if not node:
        raise RuntimeError("Got report %s for non existed node" % report.__dict__)

    for bridge_name, nic_names in report.parsed_data.items():
        for nic_name in nic_names:
            nic = node.get_host_nic(nic_name)
            if nic:
                # if not - didn't get ifconfig report yet, nothing we can do
                nic.in_bridge = bridge_name
                node.update_host_nic(nic)
        bridge = node.get_host_nic(bridge_name)
        if bridge:
            bridge.bridge_for = nic_names
            node.update_host_nic(bridge)


def on_ifconfig(report):
    cluster = Cluster.instance()
    node = cluster.get(report.node_oid)
    if not node:
        raise RuntimeError("Cluster has no Node %s" % report.node_oid)
    for name, info in report.parsed_data.items():
        mac = info.get('mac')
        if not mac:
            continue # lo 
        node.update_host_nic(name, **info)

