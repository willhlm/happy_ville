import pygame
from engine.utils import read_files
from engine import constants as C
from gameplay.entities.interactables.base.interactables import Interactables
from .states import Idle

class AbilityBall(Interactables):
    def __init__(self, pos, game_objects, ability):
        super().__init__(pos, game_objects)        
        self.rect = pygame.Rect(0, 0, self.image.width, self.image.height)
        self.rect.center = pos
        self.hitbox = pygame.Rect(0, 0, 32, 32)
        self.hitbox.center = self.rect.center
        self.true_pos = self.rect.topleft

        self.currentstate = Idle(self)#start with grow
        self.health = 3
        self.ability = ability

        self.flags = {'invincibility': False}
        
        self.explosion = 0        
        self.time = 0
        self.radius = 0#TODO

    def pool(game_objects):
        AbilityBall.size = (300,120)
        AbilityBall.image = game_objects.game.display.make_layer(AbilityBall.size).texture

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False

    def take_dmg(self, dmg = 1):
        if self.flags['invincibility']: return
        self.health -= dmg#take damage
        self.flags['invincibility'] = True

        if self.health > 0:#check if dead
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)            
            self.shader_state.handle_input('hurt')#turn white and shake
            self.currentstate.handle_input('hurt')#handle if we shoudl go to hurt state
            self.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 15, scale = 0.9)
        else:#if dead
            self.ability_ball_pickup()
        return True#return truw to show that damage was taken

    def update_render(self, dt):        
        self.time += dt * 0.1  
        self.currentstate.update_render(dt)

    def update(self, dt):
        self.currentstate.update(dt)

    def draw(self, target):
        #self.game_objects.shaders['ability_ball']['radius'] = self.radius
        self.game_objects.shaders['ability_ball']['TIME'] = self.time
        self.game_objects.shaders['ability_ball']['resolution'] = self.size
        self.game_objects.shaders['ability_ball']['explosionProgress'] = self.explosion#stats ticking in death state

        pos = (int(self.true_pos[0]-self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1]-self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.game_objects.shaders['ability_ball'])#shader render        

    def ability_ball_pickup(self):#call when player pick this up
        self.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
        self.currentstate.enter_state('death')#overrite any state and go to deat

        self.game_objects.signals.emit('ability_ball')
        self.game_objects.player.currentstate.unlock_state(self.ability)#append the ability