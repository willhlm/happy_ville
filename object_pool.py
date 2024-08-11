import Entities, particles, entities_parallax, weather, platforms

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self,game_objects):        
        Entities.Amber_Droplet.pool(game_objects)
        Entities.Bone.pool(game_objects)
        Entities.Heal_item.pool(game_objects)
        Entities.Water_running_particles.pool(game_objects)
        Entities.Grass_running_particles.pool(game_objects)
        Entities.Dust_running_particles.pool(game_objects)
        Entities.Slash.pool(game_objects)
        Entities.Conversation_bubbles.pool(game_objects)
        Entities.Slime.pool(game_objects)
        Entities.Twinkle.pool(game_objects)
        Entities.Loot_magnet.pool(game_objects)
        Entities.Half_dmg.pool(game_objects)
        Entities.Logo_loading.pool(game_objects)
        Entities.Blood.pool(game_objects)
        Entities.Player_Soul.pool(game_objects)
        Entities.Pray_effect.pool(game_objects)

        Entities.Boss_HP.pool(game_objects)
        Entities.Sword.pool(game_objects)
        Entities.Arrow.pool(game_objects)

        Entities.Tungsten.pool(game_objects)

        entities_parallax.Leaves.pool(game_objects)
        entities_parallax.Droplet.pool(game_objects)
        entities_parallax.Falling_rock.pool(game_objects)

        particles.Circle.pool(game_objects)
        particles.Spark.pool(game_objects)
        particles.Goop.pool(game_objects)
        particles.Floaty_particles.pool(game_objects)

        #screen_shader.Screen_shader.pool(game_objects)

        weather.Fog.pool(game_objects)
        weather.Circles.pool(game_objects)
        weather.Vertical_circles.pool(game_objects)
        weather.Ominous_circles.pool(game_objects)
        weather.Rain.pool(game_objects)
        weather.Fireflies.pool(game_objects)
        weather.Flash.pool(game_objects)

        platforms.Bubble.pool(game_objects)
        platforms.Bubble_static.pool(game_objects)
