import pygame

class Shader_layered_group(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super().__init__()
        self.surface = pygame.Surface([640,360], pygame.SRCALPHA, 32)

    def draw(self, screen):
        for s in self.sprites():
            surface = self.surface.copy()#make an empty surface

            surface.blit(s.image, s.rect.topleft)#blit the rellavant portion onto it
            #newrect = surface.blit(s.image, s.rect)
            s.shader.render(surface)#blit the rellacvant portion onto display via OPENGL framework

class Shader_group(pygame.sprite.Group):
    def __init__(self):
        super().__init__()

    def draw(self,screen):
        for s in self.sprites():
            s.shader.render(s.image)

class Specialdraw_Group(pygame.sprite.Group):#a group for the reflection object which need a special draw method
    def __init__(self):
        super().__init__()

    def draw(self):
        for s in self.sprites():
            s.draw()

class PauseLayer(pygame.sprite.Group):#the pause group when parallax objects are outside the boundaries: almst works with LayeredUpdates group (when they come back, it is in fron of grass, so the posoition is not 100 % preserved)
    def __init__(self):
        super().__init__()

    def update(self, pos):
        for s in self.sprites():
            self.group_distance(s,pos)

    @staticmethod
    def group_distance(s,pos):
        if s.rect[0]<s.bounds[0] or s.rect[0]>s.bounds[1] or s.rect[1]<s.bounds[2] or s.rect[1]>s.bounds[3]:#this means it is outside of screen
            s.update_pos(pos)
        else:
            #manuall add to a specific layer
            sprites = s.game_objects.all_bgs.sprites()
            bg = s.game_objects.all_bgs.reference[tuple(s.parallax)]
            index = sprites.index(bg)#fine the index in which the static layer is located

            s.game_objects.all_bgs.spritedict[s] = s.game_objects.all_bgs._init_rect#in add internal
            s.game_objects.all_bgs._spritelayers[s] = 0
            s.game_objects.all_bgs._spritelist.insert(index,s)#it goes behind the static layer of reference
            s.add_internal(s.game_objects.all_bgs)
            s.remove(s.pause_group)#remove from pause

class PauseGroup(pygame.sprite.Group):#the pause group when enteties are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self, pos):
        for s in self.sprites():
            self.group_distance(s,pos)

    @staticmethod
    def group_distance(s,pos):
        if s.rect[0]<s.bounds[0] or s.rect[0]>s.bounds[1] or s.rect[1]<s.bounds[2] or s.rect[1]>s.bounds[3]:#this means it is outside of screen
            s.update_pos(pos)
        else:
            s.add(s.group)#add to group
            s.remove(s.pause_group)#remove from pause
