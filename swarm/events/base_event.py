

from swarm.entity import Entity


class Event(Entity):

    def __init__(self, reporter, **kw):
        self.reporter = reporter
        Entity.__init__(self, **kw)
    
