
class ValidationError(Exception): pass


class BaseField(object):
    def __init__(self, key, choices=None, required=False, default=None):
        self.key = key
        self.choices = choices
        self.required = required
        self.default = default

    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = instance._data.get(self.key)
        if value is None:
            value = self.default
            if callable(value):
                value = value()
        return self.from_store(value)

    def __set__(self, instance, value):
        instance._data[self.key] = self.to_store(value)

    def from_store(self, value):
        return value

    def to_store(self, value):
        return value


class ReferenceField(BaseField):
    def from_store(self, value):
        from swarm.cluster import Cluster
        return Cluster.instance().get(value)

    def to_store(self, value):
        if hasattr(value, 'oid'):
            return value.oid
        return value


class ListField(BaseField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.key not in instance._data:
            instance._data[self.key] = []
        return instance._data[self.key]
    

class SetField(BaseField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.key not in instance._data:
            instance._data[self.key] = set()
        return instance._data[self.key]


class DictField(BaseField):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.key not in instance._data:
            instance._data[self.key] = {}
        return instance._data[self.key]
