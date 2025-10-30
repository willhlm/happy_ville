import pygame, random
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.platforms import Bubble

class BubbleSource(Interactables):#the thng that spits out bubbles in cave HAWK TUAH!
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/sources/bubble/', game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/interactables/sources/bubble/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.center = pos
        self.hitbox = self.rect.copy()
        self.spawn_timer = prop.get('spawnrate', 180)
        #self.spawn_timer = 180

        self.prop = prop
        #self.time = random.randint(0, 10)
        self.time = -1 * prop.get('init_delay', random.randint(0, 50))

    def group_distance(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        super().update(dt)
        self.time += dt
        if self.time > self.spawn_timer:
            self.game_objects.sound.play_sfx(self.sounds['spawn'][random.randint(0, 1)], vol = 0.3)
            bubble = Bubble([self.rect.centerx, self.rect.top], self.game_objects, **self.prop)
            #self.game_objects.dynamic_platforms.add(bubble)
            self.game_objects.platforms.add(bubble)
            #self.time = random.randint(0, 10)
            self.time = 0