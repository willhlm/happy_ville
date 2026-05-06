import sys, math
from engine import constants as C


class MovementManager:
    """
    Two-bucket modifier manager:

    - self.modifiers:           stackable modifiers (can exist while inactive/active)
    - self.authoritative_mods:  authoritative modifiers (ONLY added while active)

    Resolve behavior:
      1) If any authoritative modifiers exist, apply the highest-priority one.
      2) Then apply ONLY stackable modifiers that opt-in via runs_with_authoritative().
      3) If no authoritative modifiers exist, apply the full stackable list as normal.

    This matches your current “add/remove only while active” workflow well.
    """
    def __init__(self, entity):
        self.entity = entity
        self.modifiers = {}             # name -> modifier instance (stackable)
        self.authoritative_mods = {}    # name -> modifier instance (authoritative)

        self._sorted_modifiers = []
        self._sorted_authoritative = []

        self.registry = {
            'up_stream_horizontal': UpStreamHorizontal,
            'up_stream_vertical': UpStreamVertical,
            'two_d_liquid': TwoDLiquid,
            'belt': Belt,
            'wall_glide': WallGlide,
            'dash_jump': DashJump,
            'dash': Dash,
            'up_stream': UpStream,
            'shield_glide': ShieldGlide,
            'air_boost': AirBoost,
            'contained': Contained,
        }

    def add_modifier(self, modifier, priority=0, authoritative=False, **kwarg):
        inst = self.registry[modifier](priority, **kwarg)
        if authoritative:
            self.authoritative_mods[modifier] = inst
        else:
            self.modifiers[modifier] = inst
        self._sort_modifiers()

    def remove_modifier(self, modifier):
        removed = False
        if modifier in self.modifiers:
            del self.modifiers[modifier]
            removed = True
        if modifier in self.authoritative_mods:
            del self.authoritative_mods[modifier]
            removed = True
        if removed:
            self._sort_modifiers()

    def clear_modifiers(self):
        self.modifiers.clear()
        self.authoritative_mods.clear()
        self._sort_modifiers()

    def resolve(self):
        """
        Authoritative-first resolve.
        This assumes authoritative mods are only present while active.
        """
        context = MovementContext(self.entity)
        stackables = self._sorted_modifiers.copy()
        auths = self._sorted_authoritative.copy()

        # 1) Authoritative path (pick highest priority authoritative mod)
        if auths:
            auth = auths[0]
            auth.apply(context)

            # 2) Apply only stackables that opt-in to run with authoritative
            for mod in stackables:
                if mod.runs_with_authoritative():
                    mod.apply(context)

            return context

        # 3) Normal stacking path
        for mod in stackables:
            mod.apply(context)
        return context

    def consume_contact_state(self):
        self._consume_modifier_contact_state()

    def update(self, dt):
        # Update authoritative + stackable mods (some manage internal timers/removal)
        for mod in self._sorted_authoritative.copy():
            mod.update(dt)
        for mod in self._sorted_modifiers.copy():
            mod.update(dt)

    def _sort_modifiers(self):
        self._sorted_modifiers = sorted(
            self.modifiers.values(),
            key=lambda m: m.priority,
            reverse=True
        )
        self._sorted_authoritative = sorted(
            self.authoritative_mods.values(),
            key=lambda m: m.priority,
            reverse=True
        )

    def _consume_modifier_contact_state(self):
        contact_state = self.entity.contact_state
        for mod in self._sorted_authoritative.copy():
            mod.consume_contact_state(contact_state)
        for mod in self._sorted_modifiers.copy():
            mod.consume_contact_state(contact_state)

class MovementContext:
    def __init__(self, entity = None):
        self.gravity = entity.acceleration[1] if entity and hasattr(entity, 'acceleration') else C.acceleration[1]
        self.velocity = [0, 0]
        self.friction = entity.friction.copy() if entity and hasattr(entity, 'friction') else C.friction.copy()
        self.max_vel = entity.max_vel.copy() if entity and hasattr(entity, 'max_vel') else C.max_vel.copy()
        self.lock_support_axes = [False, False]

        self.air_timer = C.air_timer
        self.upstream = 1  # scale for upstream movement: sampled during upstream collision

class MovementModifier:
    def __init__(self, priority, **kwarg):
        self.priority = priority

    def apply(self, context):
        pass

    def update(self, dt):
        pass

    def handle_input(self, input):
        pass

    def consume_contact_state(self, contact_state):
        pass

    def runs_with_authoritative(self) -> bool:
        """
        If an authoritative modifier is active this frame, should this modifier still apply?
        Use this for environment effects like liquid/wind/upstream.
        """
        return False

class TwoDLiquid(MovementModifier):
    def __init__(self, priority):
        super().__init__(priority)

    def runs_with_authoritative(self) -> bool:
        # Environment effect: keep it during dash/wallglide/etc
        return True

    def apply(self, context):
        context.friction[0] *= 2
        context.friction[1] *= 2

class Belt(MovementModifier):
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.direction = kwarg['direction']
        self.axis = kwarg['axis']
        self.side = kwarg['side']

    def runs_with_authoritative(self) -> bool:
        return True

    def apply(self, context):
        if self.axis == 'x':
            context.velocity[1] += self.direction[1] if self.side == 'right' else -self.direction[1]
            return

        if self.axis != 'y':
            return

        context.velocity[0] += self.direction[0] * 0.1

        if hasattr(self.entity, 'dir') and hasattr(self.entity, 'friction'):
            context.friction[0] = C.friction_player[0] - 0.1 * self.direction[0] * self.entity.dir[0]

class AirBoost(MovementModifier):
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.target = MovementContext().friction[0]
        self.friction_x = kwarg.get('friction_x', 0.14)
        self.friction_y = 0.00
        self.ref_y = self.friction_y * (0.0001 + 1)
        self.ref_x = self.friction_x * (1 - 0.000000005)
        self.inc_fric = False

    def set_friction_x(self, friction):
        self.friction_x = friction

    def set_fritction_y(self, friction):
        self.friction_y = friction

    def apply(self, context):
        context.friction[0] = self.friction_x
        context.friction[1] = self.friction_y

    def consume_contact_state(self, contact_state):
        if contact_state.is_on_floor() or contact_state.is_on_wall():
            self.entity.movement_manager.remove_modifier('air_boost')

    def update(self, dt):
        self.friction_x += dt * 0.0005
        self.friction_y -= dt * 0.0015
        self.friction_y = max(0, self.friction_y)
        if self.target - self.friction_x < 0.0003:
            self.entity.movement_manager.remove_modifier('air_boost')

class UpStream(MovementModifier):
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.speed = kwarg.get('speed', [0, 0])
        self.max_speed = kwarg.get('max_speed', 7)

    def runs_with_authoritative(self) -> bool:
        # Environment effect: keep it during dash/wallglide/etc
        return True

    def apply(self, context):
        context.velocity[0] += self.speed[0]
        context.velocity[1] += self.speed[1]

class UpStreamVertical(UpStream):
    """Vertical"""
    def apply(self, context):
        context.velocity[1] += self.speed[1]
        context.max_vel[1] = self.max_speed

class UpStreamHorizontal(UpStream):
    """Horizontal"""
    pass

class ShieldGlide(MovementModifier):
    def __init__(self, priority, **kwargs):
        super().__init__(priority)
        self.gravity_scale = kwargs.get('gravity_scale', 0.2)
        self.fall_friction = kwargs.get('fall_friction', 0.12)

    def apply(self, context):
        context.gravity *= self.gravity_scale
        context.friction[1] = max(context.friction[1], self.fall_friction)

#authorivie ones.
class WallGlide(MovementModifier):
    def __init__(self, priority):
        super().__init__(priority)
        self.end_friction = 0.1
        self.friction = 0.5

    def apply(self, context):
        self.friction -= 0.011
        context.friction[1] = max(self.friction, self.end_friction)

class Dash(MovementModifier):
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.dash_vel = C.dash_vel

    def apply(self, context):
        context.gravity = 0
        context.lock_support_axes[0] = True
        context.velocity[0] += self.dash_vel * self.entity.dir[0]

class DashJump(MovementModifier):
    def __init__(self, priority, **kwarg):
        super().__init__(priority)
        self.entity = kwarg['entity']
        self.dash_vel = C.dash_vel
        self.dash_jump_vel = C.dash_jump_vel
        self.g_constant = 1

    def apply(self, context):
        self.dash_jump_vel += 0.6
        self.dash_jump_vel = min(self.dash_jump_vel, 0)
        context.gravity = C.acceleration[1] / self.g_constant
        context.lock_support_axes[0] = True
        context.velocity[0] += self.dash_vel * self.entity.dir[0]
        context.velocity[1] += self.dash_jump_vel        

class Contained(MovementModifier):
    def apply(self, context):
        context.gravity = 0
        context.velocity = [0, 0]
        context.max_vel = [0, 0]
