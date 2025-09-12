import pygame
from gameplay.entities.interactables.base.interactables import Interactables

class Shade_trigger(Interactables):#it changes the colourof shade screen to a new colour specified by self.new_colour
    def __init__(self, pos, game_objects, size, colour = pygame.Color(0,0,0,0)):
        super().__init__(pos, game_objects)
        self.new_colour = [colour.g,colour.b,colour.a]
        self.light_colour = self.game_objects.lights.ambient[0:3]
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self, dt):
        pass

    def player_collision(self, player):#player collision
        self.game_objects.lights.ambient = self.new_colour + [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]
        for layer in self.layers:
            layer.shader_state.handle_input('mix_colour')

    def player_noncollision(self):#when player doesn't collide
        self.game_objects.lights.ambient = self.light_colour + [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]
        for layer in self.layers:
            layer.shader_state.handle_input('idle')

    def add_shade_layers(self, layers):#called from map loader
        self.layers = layers
        for layer in layers:
            layer.new_colour = self.new_colour + [layer.colour[-1]]
            layer.bounds = self.rect

