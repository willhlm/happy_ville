from .contact_resolver import PlatformContactResolver
from .crush_resolver import PlatformCrushResolver
from .motion_rules import PlatformMotionRules


class PlatformCollider:
    def __init__(self, entity):
        self.entity = entity
        self.enabled = True
        self.contact_resolver = PlatformContactResolver(entity)
        self.crush_resolver = PlatformCrushResolver(entity)
        self.motion_rules = PlatformMotionRules(entity, self.contact_resolver)

    def can_collide(self):
        return self.enabled

    def is_crushed(self, block, side):
        return self.crush_resolver.is_crushed(block, side)

    def handle_crush(self, block, side=None):
        return self.crush_resolver.handle_crush(block, side=side)

    def resolve_horizontal(self, block, collision_type='Wall'):
        return self.contact_resolver.resolve_horizontal(block, collision_type=collision_type)

    def resolve_vertical(self, block, clamp_floor=False):
        return self.contact_resolver.resolve_vertical(block, clamp_floor=clamp_floor)

    def resolve_horizontal_strict(self, block, collision_type='Wall', eps=1):
        return self.contact_resolver.resolve_horizontal_strict(block, collision_type=collision_type, eps=eps)

    def resolve_vertical_strict(self, block, clamp_floor=False, eps=1):
        return self.contact_resolver.resolve_vertical_strict(block, clamp_floor=clamp_floor, eps=eps)

    def get_support_motion(self, block):
        return self.motion_rules.get_support_motion(block)

    def resolve_one_way_up(self, block):
        return self.motion_rules.resolve_one_way_up(block)

    def resolve_right_angle_ramp(self, ramp):
        return self.motion_rules.resolve_right_angle_ramp(ramp)

    def request_drop_through(self, colliders, offset=1):
        return self.motion_rules.request_drop_through(colliders, offset=offset)

    def request_ramp_drop(self, ramps_group, offset=1):
        return self.request_drop_through(ramps_group, offset=offset)

    def resolve_polygon(self, polygon, overlap, axis):
        return self.contact_resolver.resolve_polygon(polygon, overlap, axis)

    def push_ramp(self, ramp, side):
        self.contact_resolver.push_ramp(ramp, side)

    def push_horizontal(self, block, side, collision_type='Wall'):
        self.contact_resolver.push_horizontal(block, side, collision_type=collision_type)

    def push_vertical(self, block, side):
        self.contact_resolver.push_vertical(block, side)

    def push_vertical_sample(self, sample):
        self.contact_resolver.push_vertical_sample(sample)

    def push_horizontal_sample(self, sample):
        self.contact_resolver.push_horizontal_sample(sample)

    def clamp_vertical_velocity(self):
        self.contact_resolver.clamp_vertical_velocity()
