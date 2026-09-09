import math
from copy import copy

import pygame


class CollisionQueries:
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def check_ground(self, point):
        return self.game_objects.physics.platform_spatial_index.query_point(point) is not None

    def has_floor_below(self, entity, distance):
        if distance <= 0:
            return False

        probe = entity.hitbox.copy()
        probe.y += 1
        probe.height += distance

        platforms = self.game_objects.physics.platform_spatial_index.query_rect(probe)
        for platform in platforms:
            for sample in platform.get_floor_samples(entity):
                target_y = sample.position
                if entity.hitbox.bottom <= target_y <= entity.hitbox.bottom + distance:
                    return True
        return False

    def find_surface_in_direction(self, entity, direction, distance):
        """Probe the player's swept hitbox using the platforms' collision surfaces.

        Return the first blocking sample and travel distance. A private probe
        keeps one-way ramp acceptance checks from changing the real entity.
        """
        length = math.hypot(*direction)
        if length == 0 or distance <= 0:
            return None
        dx, dy = direction[0] / length, direction[1] / length
        probe = copy(entity)
        probe.go_through = entity.go_through.copy()
        probe.velocity = [dx, dy]
        start = entity.hitbox.copy()
        previous = start
        for step in range(1, math.ceil(distance) + 1):
            travel = min(step, distance)
            probe.hitbox = start.move(round(dx * travel), round(dy * travel))
            probe.old_hitbox = previous
            bounds = previous.union(probe.hitbox).inflate(2, 2)
            for platform in self.game_objects.physics.platform_spatial_index.query_rect(bounds):
                if dy > 0:
                    for sample in platform.get_floor_samples(probe):
                        if (previous.bottom <= sample.position <= probe.hitbox.bottom
                                and sample.source.accepts_floor_contact(
                                    probe, previous, probe.hitbox, sample.position, 0)):
                            return sample, travel
                if dy < 0:
                    for sample in platform.get_ceiling_samples(probe):
                        if (probe.hitbox.top <= sample.position <= previous.top
                                and sample.source.accepts_ceiling_contact(
                                    probe, previous, probe.hitbox, sample.position, 0)):
                            return sample, travel
                for sample in platform.get_wall_samples(probe):
                    if (dx > 0 and sample.side == 'right'
                            and previous.right <= sample.position <= probe.hitbox.right):
                        return sample, travel
                    if (dx < 0 and sample.side == 'left'
                            and probe.hitbox.left <= sample.position <= previous.left):
                        return sample, travel
            previous = probe.hitbox
        return None

    def request_pass_through(self, entity):
        platform_collider = getattr(entity, "platform_collider", None)
        if platform_collider is None:
            return False
        probe = entity.hitbox.copy()
        probe.bottom += 1
        colliders = self.game_objects.physics.platform_spatial_index.query_rect(probe)
        return platform_collider.request_drop_through(colliders)

    def check_player_interaction(self):
        player = self.game_objects.player
        npc = pygame.sprite.spritecollideany(player, self.game_objects.npcs, self.collided)
        interactable = pygame.sprite.spritecollideany(player, self.game_objects.interactables, self.collided)
        loot = pygame.sprite.spritecollideany(player, self.game_objects.loot, self.collided)

        if npc:
            npc.interact(player)
            return npc
        if interactable:
            interactable.interact(player)
            return interactable
        if loot:
            loot.interact(player)
            return loot
        return None

    def sprite_collide(self, sprite, group):
        return pygame.sprite.spritecollide(sprite, group, False, self.collided)

    def sprite_collide_any(self, sprite, group):
        return pygame.sprite.spritecollideany(sprite, group, self.collided)

    @staticmethod
    def collided(dynamic_entity, static_entity):
        return dynamic_entity.hitbox.colliderect(static_entity.hitbox)

    @staticmethod
    def collided_point(dynamic_entity, static_entity):
        return static_entity.hitbox.collidepoint(dynamic_entity.hitbox.midbottom)
