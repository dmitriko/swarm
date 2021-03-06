"Cluster instance represent state of the system"

import threading
import uuid
import time
from copy import copy
from collections import defaultdict

from swarm.entity import Entity


class Cluster(object):

    _instance_lock = threading.Lock()

    def __init__(self):
        self.init()

    def init(self):
        self._data = {}
        self._entities = defaultdict(set)

    def get(self, oid, default=None):
        return self._data.get(oid, default)

    def get_or_error(self, oid):
        entity = self._data.get(oid, None)
        if entity is None:
            raise RuntimeError(
                "Entity with oid %s does not exist" % oid)
        return entity

    def oids_by_class(self, class_):
        "Return list of stored oids for entites of given class"

        if isinstance(class_, basestring):
            class_name = class_
        else:
            assert issubclass(class_, Entity)
            class_name = class_.__name__

        return list(self._entities[class_name])

    def entities_by_class(self, class_):
        return [self._data.get(x) for x in self.oids_by_class(class_)]

    def store(self, entity):
        "Persist entity"
        assert isinstance(entity, Entity)
        self._entities[entity.__class__.__name__].add(entity.oid)
        if entity.oid not in self._data:
            self._data[entity.oid] = entity
        else:
            info = copy(entity._data) # TODO move to Entity
            del info['created']
            info['updated'] = time.time()
            self._data[entity.oid]._data.update(info)

    def is_stored(self, entity_or_oid):
        if isinstance(entity_or_oid, Entity):
            oid = entity_or_oid.oid
        else:
            oid = entity_or_oid
        return oid in self._data

    def delete(self, entity_or_oid):
        "Remove item from storage, accept entity or oid"
        if isinstance(entity_or_oid, Entity):
            entity = entity_or_oid
        else:
            entity = self._data[entity_or_oid]
        del self._data[entity.oid]
        self._entities[entity.__class__.__name__].remove(entity.oid)
            
    @staticmethod
    def instance():
        if not hasattr(Cluster, "_instance"):
            with Cluster._instance_lock:
                if not hasattr(Cluster, "_instance"):
                    Cluster._instance = Cluster()
        return Cluster._instance

    def search(self, query):
        if self._data.has_key(query):
            return self._data[query]
        for node in self.entities_by_class('Node'):
            if node.hostname == query:
                return node
        for vm_config in self.entities_by_class('VmConfig'):
            if vm_config.name.startswith(query):
                return vm_config
        for item in self._data.values():
            if item.oid.startswith(query):
                return item
        return None
