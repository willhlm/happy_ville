import Entities, particles, entities_parallax, weather

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self,game_objects):        

        Entities.Amber_Droplet.pool(game_objects)
        Entities.Bone.pool(game_objects)
        Entities.Heal_item.pool(game_objects)
        Entities.Water_running_particles.pool(game_objects)
        Entities.Grass_running_particles.pool(game_objects)
        Entities.Dust_running_particles.pool(game_objects)
        Entities.Slash.pool(game_objects)

        entities_parallax.Leaves.pool(game_objects)
        
        particles.Circle.pool(game_objects)
        particles.Spark.pool(game_objects)
        particles.Goop.pool(game_objects)

        #screen_shader.Screen_shader.pool(game_objects)
        Entities.Conversation_bubbles.pool(game_objects)

        Entities.Slime.pool(game_objects)

        weather.Fog.pool(game_objects)
        weather.Circles.pool(game_objects)
        weather.Vertical_circles.pool(game_objects)
        weather.Ominous_circles.pool(game_objects)
        weather.Rain.pool(game_objects)
        weather.Fireflies.pool(game_objects)
        weather.Flash.pool(game_objects)
