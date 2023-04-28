import Entities
import copy

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game
    def __init__(self,game_objects):
        self.game_objects = game_objects
        pos = [0,0]
        self.objects = {'Migawari_entity':Entities.Migawari_entity(pos,game_objects),'Amber_Droplet':Entities.Amber_Droplet(pos,game_objects)}

    def spawn(self,object):
        return self.objects[object].copy()
