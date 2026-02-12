from gameplay.entities.visuals.environments import Leaves, BackgroundDroplet
from gameplay.ui.components import MenuArrow, LogoLoading
from gameplay.entities.visuals.particles import particles, screen_particles
from gameplay.world.weather import weather
from gameplay.states import Bank, OptionMenu, OptionDisplay, OptionSounds
from gameplay.entities.enemies import Reindeer, CultistWarrior, CultistRogue
from gameplay.entities.platforms import Bubble, SeedPlatform
from gameplay.entities.items import *
from gameplay.entities.projectiles import *
from gameplay.entities.visuals.cosmetics import *
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay import point_arrow
from gameplay.entities.interactables import AbilityBall

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

        #interactbales
        AbilityBall.pool(game_objects)

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
        Blood.pool(game_objects)
        PlayerSoul.pool(game_objects)
        PrayEffect.pool(game_objects)        
        ThunderBall.pool(game_objects)
        ThunderSpark.pool(game_objects)
        ConversationBubbles.pool(game_objects)
        InteractableIndicator.pool(game_objects)

        #effects
        FadeEffect.pool(game_objects)

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
        ProjectileDroplet.pool(game_objects)
        SlamAttack.pool(game_objects)

        #UI
        MenuArrow.pool(game_objects)
        LogoLoading.pool(game_objects)        
        point_arrow.PointArrow.pool(game_objects)

        Leaves.pool(game_objects)
        BackgroundDroplet.pool(game_objects)

        particles.Circle.pool(game_objects)
        particles.Spark.pool(game_objects)
        particles.Goop.pool(game_objects)
        particles.FloatyParticles.pool(game_objects)

        weather.FlashFX.pool(game_objects)

        #platform
        Bubble.pool(game_objects)
        SeedPlatform.pool(game_objects)

        #states
        Bank.pool(game_objects)
        OptionMenu.pool(game_objects)
        OptionDisplay.pool(game_objects)
        OptionSounds.pool(game_objects)



        #temp
        from gameplay.entities.visuals.particles.component_based.particles import Circle, Spark, Goop

        Circle.pool(game_objects)
        Spark.pool(game_objects)
        Goop.pool(game_objects)
