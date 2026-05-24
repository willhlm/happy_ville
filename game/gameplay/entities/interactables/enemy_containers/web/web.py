import pygame

from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

from . import states


class EnemyWeb(Interactables):
    def __init__(self, pos, game_objects, **kwargs):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/larv_web/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.currentstate = states.Idle(self)

        trigger_distance = kwargs.get('trigger_distance', (90, 110))

        self.anchor_pos = self.rect.center
        self.trigger_distance = list(trigger_distance)
        enemy_type = kwargs.get('enemy_type', 'larv')
        enemy_cls = self.game_objects.registry.fetch('enemies', enemy_type)

        enemy_pos = [self.anchor_pos[0], self.anchor_pos[1]]
        self.enemy = enemy_cls(
            enemy_pos,
            game_objects,
            initial_state='hanging',
            anchor_pos=self.anchor_pos,
        )
        self.game_objects.enemies.add(self.enemy)

        self.hit_component.set_invincibility(True)

    def on_collision(self, entity):
        pass

    def on_noncollision(self, entity):
        pass
