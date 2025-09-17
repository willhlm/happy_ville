import pygame
from gameplay.entities.visuals.enviroment.base.layered_objects import LayeredObjects
from . import states_droplet_source

class DropletSource(LayeredObjects):
    animations = {}    
    def __init__(self,pos,game_objects, parallax, layer_name, group, live_blur = False):
        super().__init__(pos,game_objects, parallax, layer_name, live_blur)
        self.init_sprites('assets/sprites/animations/droplet/source/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.droplet = Droplet
        self.currentstate = states_droplet_source.Idle(self)
    
        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead            
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more       
        else:
            self.shader_state = states_shader.Idle(self)

    def drop(self):#called from states                
        if self.parallax == [1,1]:#TODO need to check for bg and fg etc if fg should not go into eprojectiles?
            obj = entities.Droplet(self.rect.topleft, self.game_objects)       
            self.game_objects.eprojectiles.add(obj)
        else:#TODO need to put in all_bgs or all_gfs
            sprites = self.group.sprites()
            bg = self.group.reference[tuple(self.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located
            obj = Droplet(self.rect.topleft, self.game_objects, self.parallax)       
            self.group.spritedict[obj] = self.group._init_rect#in add internal
            self.group._spritelayers[obj] = 0
            self.group._spritelist.insert(index,obj)#it goes behind the static layer of reference
            obj.add_internal(self.group)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)