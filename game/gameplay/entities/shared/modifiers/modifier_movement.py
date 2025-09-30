import sys, math
from engine import constants as C

class MovementManager():
    def __init__(self):
        self.modifiers = {}
        self._sorted_modifiers = []
        self.registry = {'up_stream_horizontal': UpStreamHorizontal, 'up_stream_vertical': UpStreamVertical, 'two_d_liquid': TwoDLiquid, 'wall_glide' : WallGlide, 'dash_jump': DashJump, 'dash': Dash,'up_stream': UpStream, 'tjasolmais_embrace': TjasolmaisEmbrace }

    def add_modifier(self, modifier, priority = 0, **kwarg):
        self.modifiers[modifier] = self.registry[modifier](priority, **kwarg)
        self._sort_modifiers()

    def remove_modifier(self, modifier):
        del self.modifiers[modifier]
        self._sort_modifiers()

    def clear_modifiers(self): 
        self.modifiers.clear()
        self._sort_modifiers()

    def resolve(self):
        context = MovementContext()  # Default values
        modifiers = self._sorted_modifiers.copy()
        for mod in modifiers:
            mod.apply(context)
        return context

    def handle_input(self, direction):
        modifiers = self._sorted_modifiers.copy()
        for mod in modifiers:
            mod.handle_input(direction)

    def update(self, dt):
        modifiers = self._sorted_modifiers.copy()
        for mod in modifiers:
            mod.update(dt)

    def _sort_modifiers(self):#sort modifiers by priority
        self._sorted_modifiers = sorted(self.modifiers.values(), key = lambda m: m.priority, reverse = True)

class MovementContext():
    def __init__(self):
        self.gravity = C.acceleration[1]
        self.velocity = [0, 0]
        self.friction = C.friction_player.copy()#firction is sampled evey frame
        
        self.air_timer = C.air_timer
        self.upstream = 1#a scale for upstream movement: sampled during upsteram collision

class MovementModifier():
    def __init__(self, priority, **kwarg):
        self.priority = priority

    def apply(self, context):
        pass

    def update(self, dt):#called from aila update
        pass

    def handle_input(self, input):
        pass

class WallGlide(MovementModifier):#should it instead be a general driction modifier?
    def __init__(self, priority):
        super().__init__(priority)

    def apply(self, context):
        context.friction[1] = 0.4

class TwoDLiquid(MovementModifier):#should it instead be a general driction modifier?
    def __init__(self, priority):
        super().__init__(priority)

    def apply(self, context):
        context.friction[0] *= 2
        context.friction[1] *= 2

class DashJump(MovementModifier):#should it instead be a general driction modifier?
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.target = MovementContext().friction[0]
        self.friction_x = 0.15
        self.friction_y = 0.00
        self.ref_y = self.friction_y * (0.0001  + 1)
        self.ref_x = self.friction_x * (1 - 0.000000005 )
        self.inc_fric = False

    def set_friction_x(self, friction):
        self.friction_x = friction

    def set_fritction_y(self, friction):
        self.friction_y = friction

    def increase_friction(self):
        self.inc_fric = True

    def apply(self, context):
        context.friction[0] = self.friction_x
        context.friction[1] = self.friction_y

    def handle_input(self, input):
        if input in ['ground', 'wall']:
            self.entity.movement_manager.remove_modifier('dash_jump')

    def update(self, dt):
        if self.inc_fric:
            self.friction_x += dt * 0.0008 #this is probably the best one
            #self.friction_x += self.entity.game_objects.game.dt * 0.002 * math.pow(self.friction_x/self.target, 2)
            #self.friction_x = self.friction_x * math.pow((2 - (self.target-self.friction_x)/(self.target-self.ref_x)), 0.5)

        self.friction_y -= dt * 0.0015
        self.friction_y = max(0, self.friction_y)
        if self.target - self.friction_x < 0.0003:
            self.entity.movement_manager.remove_modifier('dash_jump')

class Dash(MovementModifier):#should it instead be a general driction modifier?
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.dash_speed = C.dash_vel * 0.5

    def apply(self, context):
        context.gravity = 0
        context.velocity[0] += self.dash_speed * self.entity.dir[0]

class UpStream(MovementModifier):
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.speed = kwarg.get('speed', [0, 0])  # Default force if not provided

    def apply(self, context):
        # Push as extra acceleration
        context.velocity[0] += self.speed[0]
        context.velocity[1] += self.speed[1]

class UpStreamVertical(UpStream):
    """Vertical"""

class UpStreamHorizontal(UpStream):
    """Horizontal"""


class TjasolmaisEmbrace(MovementModifier):#added from ability
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']

    def apply(self, context):
        if self.entity.velocity[1] > 0:#only apply when falling
            context.friction[1] = 0.2
        context.air_timer *= 2
        context.upstream = 2
        #context.acceleration *= 1.2
