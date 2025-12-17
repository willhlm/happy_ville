import pygame
from gameplay.entities.interactables.base.interactables import Interactables
from engine import constants as C

class PathCollision(Interactables):
    def __init__(self, pos, game_objects, size, destination, spawn):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update_render(self, dt):
        pass

    def update(self, dt):
        pass
        #self.group_distance()

    def player_movement(self, player):#the movement aila does when colliding
        if self.rect[3] > self.rect[2]:#if player was trvelling horizontally, enforce running in that direction
            player.currentstate.enter_state('Run_main')#infstaed of idle, should make her move a little dependeing on the direction
            player.acceleration[0] = C.acceleration[0]
        else:#vertical travelling
            if player.velocity[1] < 0:#up
                player.velocity[1] = -10
            else:#down
                pass

    def collision(self, player):
        self.player_movement(player)
        self.game_objects.load_map(self.game_objects.game.state_manager.state_stack[-1], self.destination, self.spawn)#nned to send previous state so that we can update and render for exampe gameplay or title screeen while fading
        self.kill()#so that aila only collides once

