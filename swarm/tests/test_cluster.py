from .base import BaseTestCase
from swarm.cluster import Cluster
from swarm.entity import Entity

class Item(Entity):
    def __init__(self, name, **kw):
        self.name = name
        Entity.__init__(self, **kw)

class Baz(Item): pass
    
class ClusterCase(BaseTestCase):

    def test_instance(self):
        self.assertEqual(
            Cluster.instance(), Cluster.instance())

    def test_entites_storing(self):
        cluster = Cluster.instance()
        item1 = Item('foo')
        item2 = Item('bar')
        item3 = Baz('baz')
        cluster.store(item1)
        cluster.store(item2)
        cluster.store(item3)
        
        self.assertEqual(cluster.get(item1.oid), item1)
        self.assertEqual(len(cluster.entities_by_class('Item')), 2)
        self.assertEqual(len(cluster.entities_by_class(Baz)), 1)
        self.assertEqual(cluster.entities_by_class(Baz)[0],
                         item3)
        cluster.delete(item1)
        self.assertEqual(len(cluster.oids_by_class(Item)), 1)
