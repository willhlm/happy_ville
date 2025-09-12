from gameplay.entities.enviroment import entities_parallax
from gameplay.ui.elements import entities_ui
from gameplay.visuals.particles import particles, screen_particles
from gameplay.world import weather
from gameplay.entities.platforms import platforms
from gameplay.states.facilities import facilities
from gameplay.states.menus import menus
from gameplay.entities.projectiles import seeds
from gameplay.entities.enemies import enemies
from gameplay.entities.items import items
from gameplay.entities.projectiles import projectiles
from gameplay.entities.cosmetics import cosmetics
from gameplay.entities.enviroment import background
from gameplay.visuals.effects import effects
from gameplay.ui.overlay import point_arrow

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self, game_objects):
        #loot
        items.Amber_droplet.pool(game_objects)
        items.Bone.pool(game_objects)
        items.Heal_item.pool(game_objects)
        items.Tungsten.pool(game_objects)
        items.Red_infinity_stone.pool(game_objects)
        items.Green_infinity_stone.pool(game_objects)
        items.Blue_infinity_stone.pool(game_objects)
        items.Orange_infinity_stone.pool(game_objects)
        items.Purple_infinity_stone.pool(game_objects)

        #radna
        items.Boss_HP.pool(game_objects)
        items.Loot_magnet.pool(game_objects)
        items.Half_dmg.pool(game_objects)
        items.Rings.pool(game_objects)

        #cosmetics
        cosmetics.Water_running_particles.pool(game_objects)
        cosmetics.Grass_running_particles.pool(game_objects)
        cosmetics.Dust_running_particles.pool(game_objects)
        cosmetics.Slash.pool(game_objects)
        cosmetics.Twinkle.pool(game_objects)
        cosmetics.Logo_loading.pool(game_objects)
        cosmetics.Blood.pool(game_objects)
        cosmetics.Dusts.pool(game_objects)
        cosmetics.Player_Soul.pool(game_objects)
        cosmetics.Pray_effect.pool(game_objects)
        effects.FadeEffect.pool(game_objects)
        cosmetics.ThunderBall.pool(game_objects)
        cosmetics.ThunderSpark.pool(game_objects)
        cosmetics.ConversationBubbles.pool(game_objects)
        cosmetics.InteractableIndicator.pool(game_objects)

        #enemies
        enemies.Reindeer.pool(game_objects)
        enemies.Cultist_warrior.pool(game_objects)
        enemies.Cultist_rogue.pool(game_objects)

        #projectiles
        projectiles.Bouncy_balls.pool(game_objects)
        projectiles.Explosion.pool(game_objects)
        projectiles.Poisoncloud.pool(game_objects)
        projectiles.Falling_rock.pool(game_objects)
        projectiles.Projectile_1.pool(game_objects)
        projectiles.Poisonblobb.pool(game_objects)
        projectiles.Sword.pool(game_objects)
        projectiles.Arrow.pool(game_objects)
        projectiles.Wind.pool(game_objects)
        projectiles.Shield.pool(game_objects)
        projectiles.Droplet.pool(game_objects)
        projectiles.SlamAttack.pool(game_objects)

        #UI
        entities_ui.MenuArrow.pool(game_objects)
        point_arrow.PointArrow.pool(game_objects)

        entities_parallax.Leaves.pool(game_objects)
        entities_parallax.Droplet.pool(game_objects)
        entities_parallax.Falling_rock.pool(game_objects)

        particles.Circle.pool(game_objects)
        particles.Spark.pool(game_objects)
        particles.Goop.pool(game_objects)
        particles.Floaty_particles.pool(game_objects)

        weather.FlashFX.pool(game_objects)

        platforms.Bubble.pool(game_objects)
        seeds.Seed_platform.pool(game_objects)

        #states
        facilities.Bank.pool(game_objects)
        menus.Option_menu.pool(game_objects)
