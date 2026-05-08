from gameplay.entities.areas import SlowmotionField
from gameplay.entities.enemies import CultistRogue, CultistWarrior, Reindeer
from gameplay.entities.interactables import BossRewardBall
from gameplay.entities.items import *
from gameplay.entities.platforms import Bubble, SeedPlatform
from gameplay.entities.projectiles import *
from gameplay.entities.visuals.cosmetics import *
from gameplay.entities.visuals.effects import FadeEffect
from gameplay.entities.visuals.environments import BackgroundDroplet, Leaves
from gameplay.entities.visuals.particles.particles import Circle, FloatyParticles, Goop, Spark
from gameplay.states import Bank, OptionDisplay, OptionMenu, OptionSounds
from gameplay.ui.components import LogoLoadingOverlay, MenuArrow
from gameplay.ui.components.overlay import point_arrow
from gameplay.world.weather import weather


class AssetPreloader:
    """Preload shared assets once and retain them for the session."""

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._loaded_scopes = set()
        self._scope_registry = {
            "global": (
                MenuArrow,
                point_arrow.PointArrow,
                LogoLoadingOverlay,
                Bank,
                OptionMenu,
                OptionDisplay,
                OptionSounds,
                AmberDroplet,
                Bone,
                HealItem,
                Tungsten,
                Dyes,
                Journal,
                RedInfinityStone,
                BlueInfinityStone,
                GreenInfinityStone,
                OrangeInfinityStone,
                PurpleInfinityStone,
                BossRewardBall,
                BossHP,
                LootMagnet,
                HalfDamage,
                Rings,
                Water,
                Grass,
                Dust,
                Dusts,
                Slash,
                Twinkle,
                Blood,
                PlayerSoul,
                PrayEffect,
                ThunderBall,
                ThunderSpark,
                ConversationBubbles,
                InteractableIndicator,
                FadeEffect,
                SlowmotionField,
                Reindeer,
                CultistWarrior,
                CultistRogue,
                BouncyBalls,
                Explosion,
                PoisonCloud,
                FallingRock,
                Projectile_1,
                PoisonBlob,
                Arrow,
                Wind,
                Shield,
                ProjectileDroplet,
                SlamAttack,
                Tagg,
                Leaves,
                BackgroundDroplet,
                weather.FlashFX,
                Bubble,
                SeedPlatform,
                Circle,
                Spark,
                Goop,
                FloatyParticles,
            ),
        }
        self.preload_scope("global")

    def preload_scope(self, scope):
        if scope in self._loaded_scopes:
            return

        scope_assets = self._scope_registry.get(scope)
        if not scope_assets:
            return

        for asset_cls in scope_assets:
            self._preload_class(asset_cls)

        self._loaded_scopes.add(scope)

    def _preload_class(self, asset_cls):
        pool = getattr(asset_cls, "pool", None)
        if callable(pool):
            pool(self.game_objects)

        self._retain_class_assets(asset_cls)

    def _retain_class_assets(self, asset_cls):
        if getattr(asset_cls, "_retain_preloaded_assets", False):
            return

        original_release = getattr(asset_cls, "release_texture", None)
        if callable(original_release):
            asset_cls._original_release_texture = original_release

            def _release_texture_noop(self):
                return None

            asset_cls.release_texture = _release_texture_noop

        asset_cls._retain_preloaded_assets = True
