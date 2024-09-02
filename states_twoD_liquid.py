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
        self.game_objects = entity.game_objects#needed for timer
        self.liquid_tint = properties.get('liquid_tint', (0.2, 1, 0.6, 0.5) )#need to save it seperatly to colour the particles
        self.entity.shader['liquid_tint'] = self.liquid_tint
        self.entity.shader['darker_color'] = properties.get('darker_color', (0.2, 1, 0.6, 0.9))
        self.entity.shader['line_color'] = properties.get('line_color',(0.4, 1, 0.7, 1))        

        self.timers = []
        self.collision_timer = General_Timer(self, 100, self.collision_timeout)#if timer runs out, kill player: how long the player can swim
        self.noncollision_timer = General_Timer(self, 30, self.noncollision_timeout)#if this tuns out, remove collision_timer. how long tthe player has to be outside acid before reset

        self.kill_entity = False

    def update(self):
        for timer in self.timers:
            timer.update()        

    def player_collision(self, player):
        self.collision_timer.activate()
        self.noncollision_timer.kill()
        if self.kill_entity:
            self.kill()
 
    def player_noncollision(self):
        self.noncollision_timer.activate()

    def collision_timeout(self):#called when timer tuns out
        self.kill_entity = True
        if self.entity.game_objects.player.hitbox.colliderect(self.entity.hitbox):#if still colliding
            self.kill()

    def kill(self):
        self.entity.hole.player_collision(self.entity.game_objects.player)        
        self.noncollision_timer.kill()  
        self.collision_timer.kill()
        self.entity.hole.interacted = False#reset  
        self.kill_entity = False

    def noncollision_timeout(self):#called when timer tuns out 
        self.collision_timer.kill()  
        self.kill_entity = False  

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

    def kill(self):#when we kill player
        self.entity.game_objects.player.die()#kill player        
        self.noncollision_timer.kill()  
        self.collision_timer.kill()
        self.kill_entity = False

#timer
class Timer():
    def __init__(self, entity, duration):
        self.entity = entity
        self.duration = duration

    def activate(self):#add timer to the entity timer list
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)

    def update(self):
        self.lifetime -= self.entity.game_objects.game.dt*self.entity.game_objects.player.slow_motion
        if self.lifetime < 0:
            self.deactivate()

class General_Timer(Timer):#when lifetime is 0, it calls the timeout of entety
    def __init__(self, entity, duration, function):
        super().__init__(entity, duration)
        self.lifetime = duration
        self.function = function

    def kill(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)           

    def deactivate(self):    
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)          
        self.function()