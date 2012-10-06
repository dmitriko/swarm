""" Base classes for Enity like Task, Event, Reports ... """

import time
import uuid


class Entity(object):

    def __init__(self, oid=None, created=None, updated=None):
        self.oid = oid or str(uuid.uuid1())
        self.created = created or time.time()
        self.updated = updated or time.time()

    def set(self, info=None,  **kw):
        if info:
            assert isinstance(info, dict)
        else:
            info = {}
        info.update(kw)
        for key, value in info.items():
            setattr(self, key, value)
        self.updated = time.time()

    def to_json(self):
        info = copy(self.__dict__)
        info['cls'] = self.__class__.__name__
        return json.dumps(info)

    @classmethod
    def from_json(cls, json_str):
        try:
            info = dict((str(x), y) for x, y in json.loads(json_str).items())
            cls_name = info['cls']
        except (ValueError, KeyError): 
            raise RuntimeError("JSON for enity is not valid %s %s" % json_str)
        del info['cls']
        entity_class = globals().get(cls_name)
        if not entity_class:
            raise RuntimeError("%s is not valid class name" % cls_name)
        return entity_class(**info)
