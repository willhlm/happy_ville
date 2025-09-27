import pygame, math
from engine.utils import read_files

class MenuArrow():
    def __init__(self, pos, game_objects, flip = False):
        self.game_objects = game_objects
        self.image = MenuArrow.image
        self.sounds = MenuArrow.sounds              
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.true_pos = self.rect.topleft
        
        self.time = 0
        self.flip = flip  

        if flip: self.phase = math.pi             
        else: self.phase = 0        

    def pool(game_objects):
        MenuArrow.sounds = read_files.load_sounds_dict('assets/audio/sfx/ui/elements/arrow/')
        img = pygame.image.load("assets/sprites/ui/elements/arrow/arrow_right.png").convert_alpha()
        MenuArrow.image = game_objects.game.display.surface_to_texture(img)

    def update(self, dt):#note: sets pos to input, doesn't update with an increment of pos like other entities
        self.time += dt * 0.1
        self.update_pos()

    def update_pos(self):                
        shift = 0.5 * math.sin(self.time + self.phase)
        self.true_pos = [self.true_pos[0] + shift, self.true_pos[1]]

    def play_SFX(self, state = 'idle', frame = 0, vol = 0.8):        
        self.game_objects.sound.play_sfx(self.sounds[state][frame], vol = vol)

    def set_pos(self, pos):
        self.rect.topleft = pos
        self.true_pos = list(pos)

    def pressed(self, state = 'select'):#when pressing a button
        self.play_SFX(state)

