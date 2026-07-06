import pygame
from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class PlayerSpawnEffect(AnimatedEntity):  # the effect shown when Aila respawns
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict(
            'assets/sprites/entities/visuals/cosmetics/spawn_effect/',
            game_objects,
        )
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

    def reset_timer(self):
        self.game_objects.signals.emit('finish_spawn_effect')
        self.kill()
