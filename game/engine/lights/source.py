import pygame

from engine.lights.components import FollowTargetSync, StaticPositionSync, build_component
from engine.lights.helpers import iter_behaviour_specs, normalize_rgba255, resolve_center_getter


class LightSource:
    def __init__(self, game_objects, target, *, components=None, **properties):
        self.game_objects = game_objects
        self.manager = game_objects.lights
        self.target = target

        radius = float(properties.get('radius', 150))
        self.init_radius = radius
        self.radius = radius
        self.colour = normalize_rgba255(properties.get('colour', [255, 255, 255, 255]))
        self.start_angle = properties.get('start_angle', 0)
        self.end_angle = properties.get('end_angle', 360)
        self.min_radius = float(properties.get('min_radius', 0))
        self.max_radius = float(properties.get('max_radius', 300))
        self.expand_speed = float(properties.get('expand_speed', 100))
        self.parallax = properties.get('parallax', [1, 1])

        self.platform_interact = properties.get('platform_interact', False)
        self.normal_interact = float(properties.get('normal_interact', True))
        self.shadow_interact = properties.get('shadow_interact', False)

        center_getter = resolve_center_getter(target)
        center = center_getter()
        self.hitbox = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.hitbox.center = center
        self.rect = self.hitbox.copy()
        self.position = [0, 0]
        self.components = []
        self.sync = FollowTargetSync(center_getter) if properties.get('follow_target', True) else StaticPositionSync(center_getter)

        self.add_components(components)
        self.sync_render_position()

    def add_components(self, components):
        for name, cfg in iter_behaviour_specs(components):
            self.add_component(name, **cfg)

    def add_component(self, component_type, **kwargs):
        component = build_component(component_type, **kwargs)
        self.components.append(component)
        return component

    def remove_component(self, component_type):
        self.components = [c for c in self.components if c.component_type != component_type]

    def detach(self):
        self.sync = StaticPositionSync(lambda: self.hitbox.center)

    def kill(self):
        self.manager.remove(self)

    def set_radius(self, radius):
        center = self.hitbox.center
        self.radius = radius
        self.hitbox.width = radius * 2
        self.hitbox.height = radius * 2
        self.hitbox.center = center
        self.rect = self.hitbox.copy()

    def set_alpha(self, alpha):
        self.colour[-1] = max(0.0, min(1.0, alpha / 255))

    def sync_render_position(self):
        scroll = self.game_objects.camera_manager.camera.scroll
        self.position = [
            self.hitbox.centerx - self.parallax[0] * scroll[0],
            self.hitbox.centery - self.parallax[1] * scroll[1],
        ]

    def update(self, dt):
        self.sync.update(self)
        for component in list(self.components):
            component.update(self, dt)
