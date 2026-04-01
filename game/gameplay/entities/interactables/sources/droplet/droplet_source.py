import pygame
from gameplay.entities.visuals.environments.base.layered_objects import LayeredObjects
from . import states_droplet_source
from gameplay.entities.projectiles import ProjectileDroplet
from gameplay.entities.visuals.environments import BackgroundDroplet
from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager

class DropletSource(LayeredObjects):
    animations = {}    
    def __init__(self,pos,game_objects, parallax, layer_name, group, live_blur = False):
        super().__init__(pos,game_objects, parallax, layer_name, live_blur)
        self.init_sprites('assets/sprites/entities/interactables/sources/droplet/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.currentstate = states_droplet_source.Idle(self)
        self.shader_state = EntityShaderManager(self)
    
        if game_objects.world_state.narrative.events.get('tjasolmai', False):#if water boss (golden fields) is dead            
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more       
            self.shader_state.enter_state('palette_swap')

    def drop(self):#called from states                
        if self.parallax == [1,1]:#TODO need to check for bg and fg etc if fg should not go into eprojectiles?
            obj = ProjectileDroplet(self.rect.topleft, self.game_objects)       
            self.game_objects.projectiles.add_enemy(obj)
        else:#TODO need to put in all_bgs or all_gfs
            sprites = self.group.sprites()
            bg = self.group.reference[tuple(self.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located
            obj = BackgroundDroplet(self.rect.topleft, self.game_objects, self.parallax)       
            self.group.spritedict[obj] = self.group._init_rect#in add internal
            self.group._spritelayers[obj] = 0
            self.group._spritelist.insert(index,obj)#it goes behind the static layer of reference
            obj.add_internal(self.group)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def draw(self,target):
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.shader_state.draw(self.image, target, pos, flip = self.dir[0] > 0)
