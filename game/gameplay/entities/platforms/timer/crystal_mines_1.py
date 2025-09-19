import pygame
from engine.utils import read_files
from gameplay.entities.platforms.timer.base_timer import BaseTimer

class CrystalMines_1(BaseTimer):
    def __init__(self, game_objects, pos):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/timer/crystal_mines_1/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = pygame.Rect(pos[0], pos[1], self.rect[2], self.rect[3]*0.4)
        self.hitbox.center = self.rect.center

    def deactivate(self):#called when timer_disappear runs out
        self.hitbox[2], self.hitbox[3] = 0, 0
        self.game_objects.timer_manager.start_timer(60, self.activate)
        self.currentstate.handle_input('Transition_1')

    def activate(self):#called when timer_appear runs out
        self.hitbox[2], self.hitbox[3] = self.rect[2], self.rect[3]*0.4
        self.currentstate.handle_input('Transition_2')
