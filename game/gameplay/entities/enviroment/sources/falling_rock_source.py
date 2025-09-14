import pygame
from gameplay.entities.enviroment.base.layered_objects import LayeredObjects
from gameplay.entities.states import states_droplet_source

class FallingRockSource(LayeredObjects):
    animations = {}    
    def __init__(self, pos, game_objects, parallax,layer_name, live_blur = False):
        super().__init__(pos, game_objects, parallax, layer_name,live_blur)
        self.init_sprites('assets/sprites/animations/falling_rock/source/')#blur or lead from memory
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(0,0,self.image.width,self.image.height)
        self.rect.topleft = pos
        self.currentstate = states_droplet_source.Idle(self)

    def drop(self):#called from states
        if self.parallax == [1,1]:#TODO need to check for bg and fg etc. I guess fg should not go into eprojectiles
            obj = entities.Falling_rock(self.rect.bottomleft, self.game_objects)
            self.game_objects.eprojectiles.add(obj)
        else:#TODO need to put in all_bgs or all_gfs
            sprites = self.game_objects.all_bgs.sprites()
            bg = self.game_objects.all_bgs.reference[tuple(self.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located
            obj = Falling_rock(self.rect.topleft, self.game_objects, self.parallax)
            self.game_objects.all_bgs.spritedict[obj] = self.game_objects.all_bgs._init_rect#in add internal
            self.game_objects.all_bgs._spritelayers[obj] = 0
            self.game_objects.all_bgs._spritelist.insert(index,obj)#it goes behind the static layer of reference
            obj.add_internal(self.game_objects.all_bgs)