import pygame


class OverlapDispatcher:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self._collision_state = {}

    def dispatch_overlap_events(self, entities, target_group):
        collided = self.game_objects.physics.collision_queries.collided

        for target in target_group:
            previous = self._collision_state.get(target, set())
            current = set()

            for entity in entities:
                if collided(entity, target):
                    if entity not in previous:
                        target.on_collision(entity)
                    target.collision(entity)
                    current.add(entity)

            exited = previous - current
            for entity in exited:
                target.on_noncollision(entity)

            if current:
                self._collision_state[target] = current
            elif target in self._collision_state:
                del self._collision_state[target]

    def dispatch_simple(self, entities, target_group, callback_name="collision"):
        collided = self.game_objects.physics.collision_queries.collided

        for entity in entities:
            collision_targets = pygame.sprite.spritecollide(entity, target_group, dokill=False, collided=collided)
            for target in collision_targets:
                getattr(target, callback_name)(entity)

    def clear_state(self):
        self._collision_state.clear()
