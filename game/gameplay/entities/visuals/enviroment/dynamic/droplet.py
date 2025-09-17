import pygame
from engine.utils import read_files
from .base_dynamic import BaseDynamic
from gameplay.entities.shared.states import states_shader

class Droplet(BaseDynamic):#cosmetic droplet   
    def __init__(self,pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.sprites = Droplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)        
        self.lifetime = 100

        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead            
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more       
        else:
            self.shader_state = states_shader.Idle(self)              

    def update(self, dt):
        super().update(dt)
        self.update_vel(dt)
        self.destroy(dt)

    def destroy(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0:
            self.kill()

    def update_vel(self, dt):
        self.velocity[1] += dt
        self.velocity[1] = min(7,self.velocity[1])

    def pool(game_objects):
        Droplet.sprites = read_files.load_sprites_dict('assets/sprites/animations/droplet/droplet/', game_objects)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)