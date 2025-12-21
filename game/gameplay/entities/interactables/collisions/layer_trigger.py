import pygame
from gameplay.entities.interactables.base.interactables import Interactables

'append some shader to specified screen layers'

class LayerTrigger(Interactables):
    def __init__(self, pos, game_objects, size, **kwargs):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.hitbox = self.rect.copy()
        self.kwargs = kwargs

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self, dt):
        pass

    def collision(self, entity):#append some shader to specified screen layers
        self.kwargs['scale'] = [0.5 * max((entity.hitbox.centerx - self.rect.left)/self.rect[2],0)]                
        self.game_objects.signals.emit("layer_trigger_update", **self.kwargs)# 2. emit continuous update

    def on_collision(self, entity):
        self.game_objects.signals.emit("layer_trigger_in", **self.kwargs)            

    def on_noncollision(self, entity):#when player doesn't collide        
        self.game_objects.signals.emit("layer_trigger_out", **self.kwargs)  

