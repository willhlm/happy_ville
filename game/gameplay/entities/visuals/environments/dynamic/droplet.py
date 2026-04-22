import pygame
from engine.utils import read_files
from .base_dynamic import BaseDynamic
from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager

class BackgroundDroplet(BaseDynamic):#cosmetic droplet   
    def __init__(self,pos, game_objects, parallax, layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name, live_blur)
        self.sprites = BackgroundDroplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)        
        self.lifetime = 100
        self.shader_state = EntityShaderManager(self)

        if game_objects.world_state.narrative.events.get('tjasolmai', False):#if water boss (golden fields) is dead            
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more       
            self.shader_state.enter_state('palette_swap')

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
        BackgroundDroplet.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/environments/droplet/droplet/', game_objects)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def draw(self,target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.shader_state.draw(self.image, target, pos, flip = self.dir[0] > 0)
