import sys
import constants as C

class Movement_manager():
    def __init__(self):
        self.modifiers = {}
        self._sorted_modifiers = []        

    def add_modifier(self, modifier, priority = 0, **kwarg):
        new_modifier = getattr(sys.modules[__name__], modifier)(priority, **kwarg)
        self.modifiers[modifier] = new_modifier
        self._sort_modifiers()

    def remove_modifier(self, modifier):
        del self.modifiers[modifier]
        self._sort_modifiers()

    def clear_modifiers(self):
        self.modifiers.clear()

    def resolve(self):
        context = Movement_context()  # Default values
        for mod in self.modifiers.values():
            mod.apply(context)
        return context

    def update(self):
        modifiers = self._sorted_modifiers.copy()
        for mod in modifiers:
            mod.update()

    def _sort_modifiers(self):#sort modifiers by priority
        self._sorted_modifiers = sorted(self.modifiers.values(), key = lambda m: m.priority, reverse = True)        

class Movement_context():
    def __init__(self):
        self.gravity = C.acceleration[1]#not used yet
        self.friction = C.friction_player.copy()#firction is sampled evey frame
        self.air_timer = C.air_timer
        self.upstream = 1#a scale for upstream movement: sampled during upsteram collision

class Movement_modifier():
    def __init__(self, priority, **kwarg):
        self.priority = priority

    def apply(self, context):
        pass      

    def update(self):#called from aila update
        pass  

class Wall_glide(Movement_modifier):#should it instead be a general driction modifier?
    def __init__(self, priority):
        super().__init__(priority)

    def apply(self, context):
        context.friction[1] = 0.4

class TwoD_liquid(Movement_modifier):#should it instead be a general driction modifier?
    def __init__(self, priority):
        super().__init__(priority)

    def apply(self, context):
        context.friction[0] *= 2
        context.friction[1] *= 2

class Dash_jump(Movement_modifier):#should it instead be a general driction modifier?
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.friction = 0.15  
        self.target = Movement_context().friction[0]

    def set_friction(self, friction):
        self.friction = friction

    def apply(self, context):
        context.friction[0] = self.friction

    def update(self):
        self.friction += self.entity.game_objects.game.dt * 0.001
        if abs(self.friction - self.target) < 0.01:
            self.entity.movement_manager.remove_modifier('Dash_jump')        

class Tjasolmais_embrace(Movement_modifier):#added from ability
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']

    def apply(self, context):
        if self.entity.velocity[1] > 0:#only apply when falling
            context.friction[1] = 0.2              
        context.air_timer *= 2
        context.upstream = 2
        #context.acceleration *= 1.2        