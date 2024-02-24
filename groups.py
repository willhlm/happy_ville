import pygame

class Specialdraw_Group(pygame.sprite.Group):#a group for the reflection and platofrm object which need a special draw method
    def __init__(self):
        super().__init__()

    def draw(self):
        for s in self.sprites():
            s.draw()

class Group_player(pygame.sprite.Group):#playergroup
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects

    def draw(self):
        for spr in self.sprites():
            spr.draw_shader()#has to be just before the draw
            pos = (round(spr.true_pos[0]-self.game_objects.camera.true_scroll[0]),round(spr.true_pos[1]-self.game_objects.camera.true_scroll[1]))
            self.game_objects.game.display.render(spr.image, self.game_objects.game.screen, position = pos, flip = bool(max(spr.dir[0],0)), shader = spr.shader)#shader render

class Group(pygame.sprite.Group):#the rest
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects

    def draw(self):
        for spr in self.sprites():
            spr.draw_shader()#has to be just before the draw
            pos = (int(spr.rect[0]-self.game_objects.camera.scroll[0]),int(spr.rect[1]-self.game_objects.camera.scroll[1]))
            self.game_objects.game.display.render(spr.image, self.game_objects.game.screen, position = pos, flip = bool(max(spr.dir[0],0)), shader = spr.shader)#shader render

class LayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self,game_objects):
        super().__init__()
        self.game_objects = game_objects

    def draw(self):
        for spr in self.sprites():
            spr.draw_shader()#has to be just before the draw
            pos = (int(spr.true_pos[0]-spr.parallax[0]*self.game_objects.camera.scroll[0]),int(spr.true_pos[1]-spr.parallax[0]*self.game_objects.camera.scroll[1]))            
            self.game_objects.game.display.render(spr.image, self.game_objects.game.screen, position = pos, shader = spr.shader)#shader render

class PauseLayer(pygame.sprite.Group):#the pause group when parallax objects are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self):
        for s in self.sprites():
            self.group_distance(s)

    @staticmethod
    def group_distance(s):
        pos = [s.true_pos[0] - s.parallax[0]*s.game_objects.camera.scroll[0], s.true_pos[1] - s.parallax[1]*s.game_objects.camera.scroll[1]]
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

    def update(self):
        for s in self.sprites():
            self.group_distance(s)

    @staticmethod
    def group_distance(s):
        pos = [s.true_pos[0] - s.game_objects.camera.scroll[0], s.true_pos[1] - s.game_objects.camera.scroll[1]]
        if pos[0] < s.bounds[0] or pos[0] > s.bounds[1] or pos[1] < s.bounds[2] or pos[1] > s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            pass#s.update_pos(pos)
        else:
            s.add(s.group)#add to group
            s.remove(s.pause_group)#remove from pause
