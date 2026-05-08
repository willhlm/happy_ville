import pygame

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables


class EnemyCocoon(Interactables):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict(
            'assets/sprites/entities/interactables/cocoon/',
            game_objects,
        )
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()
        self.health = kwargs.get('health', 3)

        self.enemy_type = kwargs.get('enemy_type', 'maggot')
        self.enemy_kwargs = dict(kwargs.get('enemy_kwargs', {}))
        self.spawn_anchor = kwargs.get('spawn_anchor', 'midtop')
        self.spawn_offset = list(kwargs.get('spawn_offset', [0, -20]))
        self.occupant = self._create_occupant()

    def update(self, dt):
        super().update(dt)
        if self.occupant is None:
            return

        self.occupant.update(dt)
        self.occupant.post_physics_update(dt)

    def update_render(self, dt):
        super().update_render(dt)
        if self.occupant is None:
            return

        self.occupant.update_render(dt)

    def take_dmg(self, effect):
        self.health -= 1

        if self.health > 0:
            self.currentstate.handle_input('Once', animation_name='hurt', next_state='Idle')
        else:
            self.currentstate.handle_input('Once', animation_name='interact', next_state='Interacted')
            self._release_occupant()
            self.occupant = None

        return effect

    def draw(self, target):
        if self.occupant is not None:
            self.occupant.draw(target)
        super().draw(target)

    def _create_occupant(self):
        enemy_cls = self.game_objects.registry.fetch('enemies', self.enemy_type)
        anchor_pos = [
            self.rect.midbottom[0] + self.spawn_offset[0],
            self.rect.midbottom[1] + self.spawn_offset[1],
        ]
        enemy = enemy_cls(
            anchor_pos,
            self.game_objects,
            initial_state='contained',
            anchor_pos=anchor_pos,
            spawn_anchor=self.spawn_anchor,
            **self.enemy_kwargs,
        )
        return enemy

    def _release_occupant(self):
        self.occupant.release_from_container()
        self.game_objects.enemies.add(self.occupant)
