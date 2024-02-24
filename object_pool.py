import Entities, particles, entities_parallax

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.objects = {'Amber_Droplet':Entities.Amber_Droplet.pool(game_objects),'Bone':Entities.Bone.pool(game_objects),
        'Heal_item':Entities.Heal_item.pool(game_objects),'Water_running_particles':Entities.Water_running_particles.pool(game_objects),
        'Grass_running_particles':Entities.Grass_running_particles.pool(game_objects),'Dust_running_particles':Entities.Dust_running_particles.pool(game_objects)
        ,'Circle':particles.Circle.pool(game_objects), 'Leaves':entities_parallax.Leaves.pool(game_objects),'Spark':particles.Spark.pool(game_objects),
        'Slash':Entities.Slash.pool(game_objects)}
