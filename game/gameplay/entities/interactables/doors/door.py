import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Door(Interactables):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/interactables/door/')
        self.sprites=read_files.load_sprites_dict('assets/sprites/entities/interactables/doors/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        self.game_objects.sound.play_sfx(self.sounds['open'][0], vol = 0.2)
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

