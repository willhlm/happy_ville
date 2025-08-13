import pygame

class LayeredGroup():#costum layered rendering group: all_bgs and all_fgs
    def __init__(self):
        self.group_dict = {}#a dict of groups for each layer

    def add(self, layer_name, obj, layer = None):#add a object to a specific layer
        self.group_dict[layer_name].add(obj, layer = layer)

    def new_group(self, layer_name, pygame_group):
        self.group_dict[layer_name] = pygame_group

    def draw(self, target):
        for (layer, group) in self.group_dict.items():
            group.draw(target[layer].layer)               

    def empty(self):    
        for group in self.group_dict.values():
            group.empty()
        self.group_dict = {}   

    def update(self):
        for group in self.group_dict.values():
            group.update()
    
    def get_topmost_screen(self):# Gets the last key that was inserted
        return next(reversed(self.group_dict))

    def remove_from_layer(self, layer_name, obj):
        self.group_dict[layer_name].remove(obj)

class Group(pygame.sprite.Group):#normal
    def __init__(self):
        super().__init__()

    def draw(self, target):
        for spr in self.sprites():
            spr.draw(target)

    def empty(self):    
        for spr in self.sprites():
            spr.release_texture()   
        super().empty()

class LayeredUpdates(pygame.sprite.LayeredUpdates):#layered rendering
    def __init__(self):
        super().__init__()

    def draw(self, target):
        for spr in self.sprites():
            spr.draw(target)

    def empty(self):
        for spr in self.sprites():
            spr.release_texture()       
        super().empty()        

class PauseLayer(pygame.sprite.Group):#the pause group when parallax objects are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self):
        for s in self.sprites():
            self.group_distance(s)

    def empty(self):
        for spr in self.sprites():
            spr.release_texture()      
        super().empty()

    @staticmethod
    def group_distance(s):
        pos = [s.true_pos[0] - s.parallax[0]*s.game_objects.camera_manager.camera.scroll[0], s.true_pos[1] - s.parallax[1]*s.game_objects.camera_manager.camera.scroll[1]]
        if pos[0] < s.bounds[0] or pos[0] > s.bounds[1] or pos[1] < s.bounds[2] or pos[1] > s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass
        else:#manually add to a specific layer
            #s.remove(s.pause_group)#remove from pause  
            #s.game_objects.all_bgs.add(s.layer_name, s, layer = 0)
            #return
            
            s.game_objects.all_bgs.group_dict[s.layer_name].spritedict[s] = s.game_objects.all_bgs.group_dict[s.layer_name]._init_rect#in add internal
            s.game_objects.all_bgs.group_dict[s.layer_name]._spritelayers[s] = 0
            s.game_objects.all_bgs.group_dict[s.layer_name]._spritelist.insert(0, s)#add it behind everything
            s.add_internal(s.game_objects.all_bgs.group_dict[s.layer_name])
            s.remove(s.pause_group)#remove from pause

class PauseGroup(pygame.sprite.Group):#the pause group when enteties are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self):
        for s in self.sprites():
            self.group_distance(s)

    def empty(self):
        for spr in self.sprites():
            spr.release_texture()
        super().empty()

    @staticmethod
    def group_distance(s):
        s.blit_pos = [s.true_pos[0] - s.game_objects.camera_manager.camera.scroll[0], s.true_pos[1] - s.game_objects.camera_manager.camera.scroll[1]]
        if s.blit_pos[0] < s.bounds[0] or s.blit_pos[0] > s.bounds[1] or s.blit_pos[1] < s.bounds[2] or s.blit_pos[1] > s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass#s.update_pos(pos)
        else:
            s.add(s.group)#add to group
            s.remove(s.pause_group)#remove from pause
