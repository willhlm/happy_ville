import pygame

def apply_activation(sprite):
    if not hasattr(sprite, 'pause_group'):
        return
    if sprite.game_objects.activation_manager.is_active(sprite):
        return
    sprite.game_objects.activation_manager.sleep(sprite)

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

    def update(self, dt):
        for group in self.group_dict.values():
            group.update(dt)
    
    def update_render(self, dt):
        for group in self.group_dict.values():
            group.update_render(dt)

    def get_topmost_screen(self):# Gets the last key that was inserted
        return next(reversed(self.group_dict))

    def remove_from_layer(self, layer_name, obj):
        self.group_dict[layer_name].remove(obj)

class Group(pygame.sprite.Group):#normal
    def __init__(self):
        super().__init__()

    def update_render(self, dt):
        for s in self.sprites():
            s.update_render(dt)

    def update(self, dt):
        for s in self.sprites():
            s.update(dt)
            apply_activation(s)

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

    def update_render(self, dt):
        for s in self.sprites():
            s.update_render(dt)

    def update(self, dt):
        for s in self.sprites():
            s.update(dt)
            apply_activation(s)

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

    def update(self, dt):
        for s in self.sprites():
            self.group_distance(s)

    def empty(self):
        for spr in self.sprites():
            spr.release_texture()      
        super().empty()

    @staticmethod
    def group_distance(s):
        if not s.game_objects.activation_manager.is_active(s):
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

    def update(self, dt):
        for s in self.sprites():
            self.group_distance(s)

    def empty(self):
        for spr in self.sprites():
            spr.release_texture()
        super().empty()

    @staticmethod
    def group_distance(s):
        if not s.game_objects.activation_manager.is_active(s):
            pass#s.update_pos(pos)
        else:
            s.game_objects.activation_manager.wake(s)
