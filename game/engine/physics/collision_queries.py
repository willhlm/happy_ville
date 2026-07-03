import pygame


class CollisionQueries:
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def check_ground(self, point):
        return self.game_objects.physics.platform_spatial_index.query_point(point) is not None

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
