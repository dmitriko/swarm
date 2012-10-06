""" Base classes for Enity like Task, Event, Reports ... """

import time
import uuid
import json
from copy import copy


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
