"React on Event(Report) arrived to Manager"


from swarm.entity import Entity
from swarm.events.base_event import Event
from swarm.reports import IFConfigReport, BrctlShowReport, VmXMLReport
from swarm.events import NodeOnlineEvent
from swarm.cluster import Cluster
from swarm.stuff import Node, HostNic, Storage, VmProcess, VmConfig, VmNic


def on_mngr_msg(client, body, routing_key):
    entity = Entity.from_json(body)
    if isinstance(entity, Event):
        return on_event(entity)


def on_node_started(client):
    "Use it only in node context"
    import socket
    event = NodeOnlineEvent(client.oid, socket.gethostname())
    event.storages = Node.get_storage_points(client)
    client.publish_event(event)


def on_event(event):
    if isinstance(event, NodeOnlineEvent):
        return on_node_online(event)
    if isinstance(event, IFConfigReport):
        return on_ifconfig(event)
    if isinstance(event, BrctlShowReport):
        return on_brctl_show(event)
    if isinstance(event, VmXMLReport):
        return on_vmxml(event)


def on_report_from_offline_node(report):
    """Handle situation when we got any report from 
    node and we have no any info about that node

    """
    raise RuntimeError("Report %s for offline node %s" % (
            report, report.node_oid))
    

def on_vmxml(event):
    "Procedures on libvirt xml report"
    cluster = Cluster.instance()
    node = cluster.get(event.node_oid)
    if node is None:
        return on_report_from_offline_node(event)
    data = event.parsed_data
    nics = []
    for nic in data['nics']:
        nics.append(VmNic(**nic))
    vm_config = VmConfig(oid=data['uuid'],
                         vcpu=data['vcpu'],
                         memory=data['memory'],
                         name=data['name'],
                         features=data['features'],
                         libvirt_xml=event.raw_data,
                         nics=nics)
    cluster.store(vm_config)
    if data.get('libvirt_id'):
        node.update_vm_process(data['libvirt_id'], vm_config)


def on_node_online(event):
    cluster = Cluster.instance()
    node = Node(oid=event.node_oid, storages=event.storages, hostname=event.hostname)
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

