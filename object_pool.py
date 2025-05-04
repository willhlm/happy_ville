import entities, particles, entities_parallax, weather, platforms, entities_UI, ui_backpack, game_states_facilities, dialogue, seeds

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self, game_objects):
        #loot
        entities.Amber_droplet.pool(game_objects)
        entities.Bone.pool(game_objects)
        entities.Heal_item.pool(game_objects)
        entities.Tungsten.pool(game_objects)
        entities.Red_infinity_stone.pool(game_objects)
        entities.Green_infinity_stone.pool(game_objects)
        entities.Blue_infinity_stone.pool(game_objects)
        entities.Orange_infinity_stone.pool(game_objects)
        entities.Purple_infinity_stone.pool(game_objects)

        #omamori
        entities.Boss_HP.pool(game_objects)
        entities.Loot_magnet.pool(game_objects)
        entities.Half_dmg.pool(game_objects)

        #cosmetics
        entities.Water_running_particles.pool(game_objects)
        entities.Grass_running_particles.pool(game_objects)
        entities.Dust_running_particles.pool(game_objects)
        entities.Slash.pool(game_objects)
        entities.Twinkle.pool(game_objects)
        entities.Logo_loading.pool(game_objects)
        entities.Blood.pool(game_objects)
        entities.Dusts.pool(game_objects)
        entities.Player_Soul.pool(game_objects)
        entities.Pray_effect.pool(game_objects)
        entities.Fade_effect.pool(game_objects)

        #projectiles
        entities.Bouncy_balls.pool(game_objects)
        entities.Explosion.pool(game_objects)
        entities.Poisoncloud.pool(game_objects)
        entities.Falling_rock.pool(game_objects)
        entities.Projectile_1.pool(game_objects)
        entities.Poisonblobb.pool(game_objects)
        entities.Sword.pool(game_objects)
        entities.Arrow.pool(game_objects)
        entities.Wind.pool(game_objects)
        entities.Shield.pool(game_objects)
        entities.Thunder.pool(game_objects)
        entities.Droplet.pool(game_objects)

        entities_UI.Menu_Arrow.pool(game_objects)
        entities.Arrow_UI.pool(game_objects)


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
        weather.Wind.pool(game_objects)

        platforms.Bubble.pool(game_objects)
        seeds.Seed_platform.pool(game_objects)

        #UI backpack
        ui_backpack.InventoryUI.pool(game_objects)
        ui_backpack.NecklaseUI.pool(game_objects)
        ui_backpack.JournalUI.pool(game_objects)
        ui_backpack.MapUI.pool(game_objects)

        #states
        game_states_facilities.Bank.pool(game_objects)

        dialogue.Conversation_bubbles.pool(game_objects)
