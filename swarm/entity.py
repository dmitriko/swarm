""" Base classes for Enity like Task, Event, Reports ... """

import time
import uuid
import json
from copy import copy


class ValidationError(Exception): 
    pass


def json_encode(obj):
    if isinstance(obj, Entity):
        return obj.to_json()
    return str(obj)


def json_decode(obj):
    if obj.has_key('cls'):
        return Entity.from_dict(obj)
    return obj


class MetaEntity(type):
    "Register every Entity class in registry"

    Registry = {} # class name : class itself. 

    def __init__(mcs, *args, **kw):

        MetaEntity.Registry[mcs.__name__] = mcs


class Entity(object):

    __metaclass__ = MetaEntity

    def __init__(self, oid=None, created=None, updated=None):
        self.oid = oid or str(uuid.uuid1())
        self.created = created or time.time()
        self.updated = updated or time.time()
        self.validate()

    def validate(self):
        pass

    def set(self, info=None,  **kw):
        if info:
            assert isinstance(info, dict)
        else:
            info = {}
        info.update(kw)
        for key, value in info.items():
            setattr(self, key, value)
        self.validate()
        self.updated = time.time()

    def to_json(self):
        "Return JSON object"
        info = copy(self.__dict__)
        info['cls'] = self.__class__.__name__
        return json.dumps(info, default=json_encode)

    @classmethod
    def from_dict(cls, info):
        if not info.has_key('cls'):
            raise RuntimeError("%s has not cls member" % info)
        cls_name = info['cls']
        del info['cls']
        entity_class = MetaEntity.Registry.get(cls_name)
        if not entity_class:
            raise RuntimeError("%s is not valid class name" % cls_name)
        info = dict((str(x), y) for x, y in info.items())
        return entity_class(**info)
        
    @classmethod
    def from_json(cls, json_str):
        "Return Entity instance for given json str"
        try:
            return json.loads(json_str, object_hook=json_decode)
        except ValueError:
            raise RuntimeError("JSON for enity is not valid %s %s" % json_str)
#        return cls.from_dict(info)
