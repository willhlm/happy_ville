import Entities

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.objects = {'Amber_Droplet':Entities.Amber_Droplet.pool(),'Bone':Entities.Bone.pool(),'Heal_item':Entities.Heal_item.pool(),'Water_running_particles':Entities.Water_running_particles.pool(),'Grass_running_particles':Entities.Grass_running_particles.pool(),'Dust_running_particles':Entities.Dust_running_particles.pool()}
