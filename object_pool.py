import Entities, particles, entities_parallax, screen_shader, weather

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self,game_objects):
        self.game_objects = game_objects
        objects = {'Amber_Droplet':Entities.Amber_Droplet.pool(game_objects),'Bone':Entities.Bone.pool(game_objects),
        'Heal_item':Entities.Heal_item.pool(game_objects),'Water_running_particles':Entities.Water_running_particles.pool(game_objects),
        'Grass_running_particles':Entities.Grass_running_particles.pool(game_objects),'Dust_running_particles':Entities.Dust_running_particles.pool(game_objects)
        ,'Circle':particles.Circle.pool(game_objects), 'Leaves':entities_parallax.Leaves.pool(game_objects),'Spark':particles.Spark.pool(game_objects),
        'Slash':Entities.Slash.pool(game_objects), 'Screen_shader':screen_shader.Screen_shader.pool(game_objects),'Goop':particles.Goop.pool(game_objects)}

        Entities.Slime.pool(game_objects)

        weather.Fog.pool(game_objects)
        weather.Circles.pool(game_objects)
        weather.Vertical_circles.pool(game_objects)
        weather.Ominous_circles.pool(game_objects)
        weather.Rain.pool(game_objects)
        weather.Fireflies.pool(game_objects)
        weather.Flash.pool(game_objects)
