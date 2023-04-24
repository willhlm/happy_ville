import Entities

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game
    def __init__(self):
        self.objects = {'Migawari_entity':Entities.Migawari_entity}

    def spawn(self,object):
        self.objects[object]
        return
