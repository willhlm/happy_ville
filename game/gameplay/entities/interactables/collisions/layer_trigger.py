import pygame
from gameplay.entities.interactables.base.interactables import Interactables

class LayerTrigger(Interactables):
    def __init__(self, pos, game_objects, size, **kwargs):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()
        self.kwargs = kwargs
        self.interacted = False

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self, dt):
        pass

    def player_collision(self, player):#append some shader to specified screen layers
        self.kwargs['scale'] = [0.5 * max((self.game_objects.player.hitbox.centerx - self.rect.left)/self.rect[2],0)]                
        if not self.interacted: 
            self.interacted = True
            self.game_objects.signals.emit("layer_trigger_in", **self.kwargs)        
        else:
            self.game_objects.signals.emit("layer_trigger_update", **self.kwargs)# 2. emit continuous update

    def player_noncollision(self):#when player doesn't collide        
        if not self.interacted: return
        self.interacted = False
        self.game_objects.signals.emit("layer_trigger_out", **self.kwargs)  

