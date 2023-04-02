import pygame, math

class Screen():
    def __init__(self,layer):
        self.layer = layer
        self.blank_surface = pygame.Surface(layer.game_objects.game.WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()
        layer.game_objects.game.new_screen(self)
        self.true_offset = [0,0]
        self.game_objects = layer.game_objects

    def update_pos(self,pos):
        self.surface = self.blank_surface.copy()
        fracx, whole = math.modf(self.layer.parallax[0]*self.game_objects.camera.true_scroll[0])
        fracy, whole = math.modf(self.layer.parallax[1]*self.game_objects.camera.true_scroll[1])
        self.offset = [fracx, fracy]#the fractional coordinate

class Player_screen():
    def __init__(self,layer):
        self.layer = layer
        self.blank_surface = pygame.Surface(layer.game_objects.game.WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()
        self.surface = self.blank_surface.copy()
        layer.game_objects.game.player_screen(self)
        self.offset = [0,0]
        self.game_objects = layer.game_objects

    def update_pos(self):
        self.surface = self.blank_surface.copy()
        fracx, whole = math.modf(self.game_objects.camera.true_scroll[0])
        fracy, whole = math.modf(self.game_objects.camera.true_scroll[1])
        self.offset = [fracx, fracy]#the fractional coordinate
