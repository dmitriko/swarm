"Cluster instance represent state of the system"

import threading
import uuid
from collections import defaultdict

from swarm.entity import Entity


class Cluster(object):

    _instance_lock = threading.Lock()

    def __init__(self):
        self._data = {}
        self._entities = defaultdict(set)

    def get(self, oid, default=None):
        return self._data.get(oid, default)

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
            self._data[entity.oid].set(entity.to_dict())

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
