import pygame

class Group(pygame.sprite.Group):#normal
    def __init__(self):
        super().__init__()

    def update_render(self, dt):
        for s in self.sprites():
            s.update_render(dt)

    def update(self, dt):
        for s in self.sprites():
            s.update(dt)

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
        pos = [s.true_pos[0] - s.parallax[0]*s.game_objects.camera_manager.camera.scroll[0], s.true_pos[1] - s.parallax[1]*s.game_objects.camera_manager.camera.scroll[1]]
        if pos[0] < s.bounds[0] or pos[0] > s.bounds[1] or pos[1] < s.bounds[2] or pos[1] > s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass
        else:#manually add to a specific layer
            sprites = s.game_objects.all_bgs.sprites()
            bg = s.game_objects.all_bgs.reference[tuple(s.parallax)]
            index = sprites.index(bg)#find the index in which the static layer is located

            s.game_objects.all_bgs.spritedict[s] = s.game_objects.all_bgs._init_rect#in add internal
            s.game_objects.all_bgs._spritelayers[s] = 0
            s.game_objects.all_bgs._spritelist.insert(index,s)#it goes behind the static layer of reference
            s.add_internal(s.game_objects.all_bgs)
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
        s.blit_pos = [s.true_pos[0] - s.game_objects.camera_manager.camera.scroll[0], s.true_pos[1] - s.game_objects.camera_manager.camera.scroll[1]]
        if s.blit_pos[0] < s.bounds[0] or s.blit_pos[0] > s.bounds[1] or s.blit_pos[1] < s.bounds[2] or s.blit_pos[1] > s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass#s.update_pos(pos)
        else:
            s.add(s.group)#add to group
            s.remove(s.pause_group)#remove from pause
