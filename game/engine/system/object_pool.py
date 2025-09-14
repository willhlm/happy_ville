from gameplay.entities.enviroment import Leaves, Droplet, FallingRock
from gameplay.ui.elements import entities_ui
from gameplay.visuals.particles import particles, screen_particles
from gameplay.world import weather
from gameplay.states.facilities import facilities
from gameplay.states.menus import menus
from gameplay.entities.projectiles import seeds
from gameplay.entities.enemies import Reindeer, CultistWarrior, CultistRogue
from gameplay.entities.platforms import Bubble, SeedPlatform
from gameplay.entities.items import *
from gameplay.entities.projectiles import *
from gameplay.entities.cosmetics import *
from gameplay.visuals.effects import effects
from gameplay.ui.overlay import point_arrow

class Object_pool():#a class that contains the objecte one may one to spawn duirng the game: it preloads stiff that needs to be loaded from file
    def __init__(self, game_objects):
        #loot
        AmberDroplet.pool(game_objects)
        Bone.pool(game_objects)
        HealItem.pool(game_objects)
        Tungsten.pool(game_objects)
        RedInfinityStone.pool(game_objects)
        BlueInfinityStone.pool(game_objects)
        GreenInfinityStone.pool(game_objects)
        OrangeInfinityStone.pool(game_objects)
        PurpleInfinityStone.pool(game_objects)

        #radna
        BossHP.pool(game_objects)
        LootMagnet.pool(game_objects)
        HalfDamage.pool(game_objects)
        Rings.pool(game_objects)

        #cosmetics
        Water.pool(game_objects)
        Grass.pool(game_objects)
        Dust.pool(game_objects)
        Dusts.pool(game_objects)
        Slash.pool(game_objects)
        Twinkle.pool(game_objects)
        LogoLoading.pool(game_objects)
        Blood.pool(game_objects)
        PlayerSoul.pool(game_objects)
        PrayEffect.pool(game_objects)        
        ThunderBall.pool(game_objects)
        ThunderSpark.pool(game_objects)
        ConversationBubbles.pool(game_objects)
        InteractableIndicator.pool(game_objects)

        #effects
        effects.FadeEffect.pool(game_objects)

        #enemies
        Reindeer.pool(game_objects)
        CultistWarrior.pool(game_objects)
        CultistRogue.pool(game_objects)

        #projectiles
        BouncyBalls.pool(game_objects)
        Explosion.pool(game_objects)
        PoisonCloud.pool(game_objects)
        FallingRock.pool(game_objects)
        Projectile_1.pool(game_objects)
        PoisonBlob.pool(game_objects)
        Sword.pool(game_objects)
        Arrow.pool(game_objects)
        Wind.pool(game_objects)
        Shield.pool(game_objects)
        Droplet.pool(game_objects)
        SlamAttack.pool(game_objects)

        #UI
        entities_ui.MenuArrow.pool(game_objects)
        point_arrow.PointArrow.pool(game_objects)

        Leaves.pool(game_objects)
        Droplet.pool(game_objects)
        FallingRock.pool(game_objects)

        particles.Circle.pool(game_objects)
        particles.Spark.pool(game_objects)
        particles.Goop.pool(game_objects)
        particles.Floaty_particles.pool(game_objects)

        weather.FlashFX.pool(game_objects)

        #platform
        Bubble.pool(game_objects)
        SeedPlatform.pool(game_objects)

        #states
        facilities.Bank.pool(game_objects)
        menus.Option_menu.pool(game_objects)
