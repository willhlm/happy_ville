import sys
import constants as C

class Basic_states():
    def __init__(self,entity):
        self.entity = entity

    def enter_state(self,newstate,**kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity,**kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):#called when animation is finished in reset_timer
        pass

    def player_collision(self, player):
        pass            

    def player_noncollision(self):
        pass    

class Water(Basic_states):
    def __init__(self,entity, **properties):
        super().__init__(entity)
        self.liquid_tint = properties.get('liquid_tint', (0.2, 0.6, 1.0, 0.5) )#need to save it seperatly to colour the particles
        self.entity.shader['liquid_tint'] = self.liquid_tint
        self.entity.shader['darker_color'] = properties.get('darker_color', (0.2, 0.6, 1.0, 0.9))
        self.entity.shader['line_color'] = properties.get('line_color',(0.4, 0.7, 1.0, 1))

class Poison(Basic_states):#idle once
    def __init__(self,entity, **properties):
        super().__init__(entity)
        self.liquid_tint = properties.get('liquid_tint', (0.2, 1, 0.6, 0.5) )#need to save it seperatly to colour the particles
        self.entity.shader['liquid_tint'] = self.liquid_tint
        self.entity.shader['darker_color'] = properties.get('darker_color', (0.2, 1, 0.6, 0.9))
        self.entity.shader['line_color'] = properties.get('line_color',(0.4, 1, 0.7, 1))        
   
    def player_collision(self, player):
        if player.take_dmg(duration = 0):#returns true if damae was taken
            self.entity.hole.player_transport(player)        

class Poison_vertical(Poison):#vertical acid in gold nfields
    def __init__(self,entity, **properties):
        super().__init__(entity)
        self.scroll_speed = properties.get('scroll_speed', 1)

    def update(self):
        super().update()
        self.update_pos()

    def update_pos(self):
        self.entity.true_pos[1] -= self.scroll_speed * self.entity.game_objects.game.dt
        self.entity.rect.topleft = self.entity.true_pos
        self.entity.hitbox.topleft = self.entity.rect.topleft    

    def player_collision(self, player):#when we kill player
        if player.take_dmg(duration = 0):#returns true if damae was taken
            player.die()#kill player        
