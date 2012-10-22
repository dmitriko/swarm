"React on Event(Report) arrived to Manager"


from swarm.entity import Entity
from swarm.events.base_event import Event
from swarm.reports import IFConfigReport, BrctlShowReport
from swarm.events import NodeOnlineEvent
from swarm.cluster import Cluster
from swarm.stuff import Node, HostNic, Storage


def on_mngr_msg(client, body, routing_key):
    entity = Entity.from_json(body)
    if isinstance(entity, Event):
        return on_event(entity)


def on_node_started(client):
    event = NodeOnlineEvent(client.oid)
    event.storages = Storage.get_node_mountpoints(client)
    client.publish_event(event)


def on_event(event):
    if isinstance(event, NodeOnlineEvent):
        return on_node_online(event)
    if isinstance(event, IFConfigReport):
        return on_ifconfig(event)
    if isinstance(event, BrctlShowReport):
        return on_brctl_show(event)


def on_node_online(event):
    cluster = Cluster.instance()
    node = Node(oid=event.node_oid)
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

