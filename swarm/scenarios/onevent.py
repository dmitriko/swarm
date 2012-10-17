"React on Event(Report) arrived to Manager"


from swarm.entity import Entity
from swarm.events.base_event import Event
from swarm.reports import IFConfigReport
from swarm.events import NodeOnlineEvent
from swarm.cluster import Cluster
from swarm.stuff import Node


def on_mngr_msg(client, body, routing_key):
    entity = Entity.from_json(body)
    if isinstance(entity, Event):
        return on_event(entity)


def on_event(event):
    if isinstance(event, NodeOnlineEvent):
        return on_node_online(event)
    if isinstance(event, IFConfigReport):
        return on_ifconfig(event)


def on_node_online(event):
    cluster = Cluster.instance()
    node = Node(oid=event.node_oid)
    cluster.store(node)


def on_ifconfig(report):
    pass

