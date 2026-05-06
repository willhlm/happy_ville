from engine.physics.collision_queries import CollisionQueries
from engine.physics.overlap_dispatcher import OverlapDispatcher
from engine.physics.platform_solver import PlatformCollisionSolver
from engine.physics.platform_spatial_index import PlatformSpatialIndex


class PhysicsManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.collision_queries = CollisionQueries(game_objects)
        self.overlap_dispatcher = OverlapDispatcher(game_objects)
        self.platform_solver = PlatformCollisionSolver(game_objects)
        self.platform_spatial_index = PlatformSpatialIndex()

    def clear_state(self):
        self.overlap_dispatcher.clear_state()
        self.platform_spatial_index.clear()

    def rebuild_platform_index(self):
        self.platform_spatial_index.rebuild(self.game_objects.platforms.sprites())

    def simulate_group(self, group, dt):
        for entity in group.sprites():
            self.simulate_entity(entity, dt)

    def simulate_entities(self, entities, dt):
        for entity in entities:
            self.simulate_entity(entity, dt)

    def simulate_entity(self, entity, dt):
        entity.update(dt)
        self.platform_solver.solve(entity, dt)
        post_physics = getattr(entity, 'post_physics_update', None)
        if post_physics:
            post_physics(dt)

    def dispatch_overlaps(self, dt=None):
        enemy_projectiles = self.game_objects.projectiles.all_enemy()
        friendly_projectiles = self.game_objects.projectiles.all_friendly()
        players_enemies_loot = (
            self.game_objects.players.sprites()
            + self.game_objects.enemies.sprites()
            + self.game_objects.loot.sprites()
        )
        interactables = self.game_objects.interactables.sprites() + self.game_objects.interactables_fg.sprites()

        self.overlap_dispatcher.dispatch_simple(self.game_objects.players, self.game_objects.enemies, callback_name='player_collision')
        self.overlap_dispatcher.dispatch_simple(self.game_objects.players, self.game_objects.bg_fade, callback_name='player_collision')

        self.overlap_dispatcher.dispatch_overlap_events(self.game_objects.players, self.game_objects.loot)
        self.overlap_dispatcher.dispatch_overlap_events(self.game_objects.players, self.game_objects.interactables)#only players
        self.overlap_dispatcher.dispatch_overlap_events(players_enemies_loot, self.game_objects.interactables_fg)
        self.overlap_dispatcher.dispatch_overlap_events(self.game_objects.players, self.game_objects.npcs)

        self.overlap_dispatcher.dispatch_simple(enemy_projectiles, friendly_projectiles, callback_name='collision_projectile')
        self.overlap_dispatcher.dispatch_simple(self.game_objects.enemies, friendly_projectiles, callback_name='collision_enemy')
        self.overlap_dispatcher.dispatch_simple(self.game_objects.players, enemy_projectiles, callback_name='collision_enemy')
        self.overlap_dispatcher.dispatch_simple(self.game_objects.platforms, self.game_objects.projectiles.friendly, callback_name='collision_platform')
        self.overlap_dispatcher.dispatch_simple(self.game_objects.platforms, self.game_objects.projectiles.enemy, callback_name='collision_platform')

        self.overlap_dispatcher.dispatch_simple(interactables, friendly_projectiles, callback_name='collision_interactables')
        self.overlap_dispatcher.dispatch_simple(interactables, enemy_projectiles, callback_name='collision_interactables')
