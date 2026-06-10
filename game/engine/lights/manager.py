from itertools import chain
from engine.render.blur_kernel import build_gaussian_kernel
from engine.lights.source import LightSource

class LightManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.set_ambient_light([0, 0, 0, 0])
        # Policy:
        # - only active lights count against max_light_sources
        # - sleeping lights stay registered under their owner and can wake later
        # - if the active pool is full, waking lights remain paused
        self.active_lights = []
        self.paused_lights = []
        self.owner_lights = {}
        self.shaders = {
            'light': game_objects.shaders['light'],
            'blur': game_objects.shaders['blur_fast'],
            'blend': game_objects.shaders['blend'],
        }

        self.shaders['light']['resolution'] = self.game_objects.game.window_size

        self.layer1 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer2 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer3 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.screen_copy = game_objects.game.display.make_layer(game_objects.game.display_size)

        self.normal_map = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.max_light_sources = 20
        self.max_occluder_rectangles = 20
        self.blur_radius = 2.0
        self._blur_r_int = 0
        self._blur_weights = None
        self._point_capacity = self.max_occluder_rectangles * 4
        self._init_render_buffers()
        self._rebuild_blur_kernel()
        self.update_render(0)

    def set_ambient_light(self, colour):
        self.ambient = colour

    def new_map(self):
        self.clear_lights()
        self.set_ambient_light([0, 0, 0, 0])

    def clear_normal_map(self):
        self.normal_map.clear(0, 0, 0, 0)

    def _rebuild_blur_kernel(self):
        self._blur_r_int, self._blur_weights = build_gaussian_kernel(self.blur_radius)

    def _init_render_buffers(self):
        self.normal_interact = [0] * self.max_light_sources
        self.num_rectangle = [0] * self.max_light_sources
        self.occluder_start_index = [0] * self.max_light_sources
        self.positions = [[0, 0] for _ in range(self.max_light_sources)]
        self.radius = [0] * self.max_light_sources
        self.colour = [[0, 0, 0, 0] for _ in range(self.max_light_sources)]
        self.start_angle = [0] * self.max_light_sources
        self.end_angle = [0] * self.max_light_sources
        self.min_radius = [0] * self.max_light_sources
        self.points = [[0, 0] for _ in range(self._point_capacity)]

    def _reset_render_buffers(self):
        for index in range(self.max_light_sources):
            self.normal_interact[index] = 0
            self.num_rectangle[index] = 0
            self.occluder_start_index[index] = 0
            self.positions[index][0] = 0
            self.positions[index][1] = 0
            self.radius[index] = 0
            self.colour[index][0] = 0
            self.colour[index][1] = 0
            self.colour[index][2] = 0
            self.colour[index][3] = 0
            self.start_angle[index] = 0
            self.end_angle[index] = 0
            self.min_radius[index] = 0

        for index in range(self._point_capacity):
            self.points[index][0] = 0
            self.points[index][1] = 0

    def update_render(self, dt):
        self._reset_render_buffers()
        rectangle_cursor = 0
        active_light_count = 0

        for light in self.active_lights[:]:
            light.update(dt)
            if light not in self.active_lights:
                continue
            if not self._should_render_light(light):
                continue

            self.positions[active_light_count][0] = light.position[0]
            self.positions[active_light_count][1] = self.game_objects.game.window_size[1] - light.position[1]
            self.radius[active_light_count] = light.radius
            self.colour[active_light_count][0] = light.colour[0]
            self.colour[active_light_count][1] = light.colour[1]
            self.colour[active_light_count][2] = light.colour[2]
            self.colour[active_light_count][3] = light.colour[3]
            self.start_angle[active_light_count] = light.start_angle
            self.end_angle[active_light_count] = light.end_angle
            self.min_radius[active_light_count] = light.min_radius
            self.normal_interact[active_light_count] = light.normal_interact
            rectangle_cursor = self.list_points(light, active_light_count, rectangle_cursor)
            active_light_count += 1

        self.active_light_count = active_light_count
        self.shaders['light']['num_lights'] = active_light_count

    def _should_render_light(self, light):
        if light.radius <= 0:
            return False
        if light.colour[-1] <= 0.01:
            return False

        window_w, window_h = self.game_objects.game.window_size
        left = light.position[0] - light.radius
        right = light.position[0] + light.radius
        top = light.position[1] - light.radius
        bottom = light.position[1] + light.radius

        return not (
            right < 0
            or left > window_w
            or bottom < 0
            or top > window_h
        )

    def list_points(self, light, index, rectangle_cursor):
        if not light.platform_interact:
            self.num_rectangle[index] = 0
            self.occluder_start_index[index] = rectangle_cursor
            return rectangle_cursor

        platforms = self._get_light_platforms(light)
        available = max(self.max_occluder_rectangles - rectangle_cursor, 0)
        platforms = platforms[:available]
        self.occluder_start_index[index] = rectangle_cursor
        self.num_rectangle[index] = len(platforms)
        self._write_platform_points(platforms, rectangle_cursor)
        return rectangle_cursor + len(platforms)

    def _get_light_platforms(self, light):
        if light.cache_platforms and light._cached_platforms is not None:
            return light._cached_platforms

        platforms = self.game_objects.physics.platform_spatial_index.query_rect(light.hitbox)
        if light.cache_platforms:
            light._cached_platforms = platforms
        return platforms

    def _write_platform_points(self, platforms, rectangle_cursor):
        scroll = self.game_objects.camera_manager.camera.scroll
        point_index = rectangle_cursor * 4
        for rec in platforms:
            self.points[point_index][0] = rec.hitbox.topleft[0] - scroll[0]
            self.points[point_index][1] = rec.hitbox.topleft[1] - scroll[1]
            self.points[point_index + 1][0] = rec.hitbox.topright[0] - scroll[0]
            self.points[point_index + 1][1] = rec.hitbox.topright[1] - scroll[1]
            self.points[point_index + 2][0] = rec.hitbox.bottomright[0] - scroll[0]
            self.points[point_index + 2][1] = rec.hitbox.bottomright[1] - scroll[1]
            self.points[point_index + 3][0] = rec.hitbox.bottomleft[0] - scroll[0]
            self.points[point_index + 3][1] = rec.hitbox.bottomleft[1] - scroll[1]
            point_index += 4

    def clear_lights(self):
        self.active_lights = []
        self.paused_lights = []
        self.owner_lights = {}
        self.shaders['light']['num_lights'] = 0

    def iter_active_lights(self):
        return iter(self.active_lights)

    def iter_lights(self):
        return chain(self.active_lights, self.paused_lights)

    def create(self, target, *, components=None, **properties):
        light = LightSource(self.game_objects, target, components=components, **properties)
        owner = self._get_managed_owner(target)
        light.owner = owner
        if owner is None:
            if not self._has_active_capacity():
                return None
            self.active_lights.append(light)
        else:
            self.owner_lights.setdefault(owner, []).append(light)
            # Managed owners can create lights while sleeping; those lights stay paused
            # until the owner wakes and there is active capacity available.
            target_list = self.paused_lights if owner.pause_group in owner.groups() else self.active_lights
            if target_list is self.active_lights and not self._has_active_capacity():
                self._remove_from_list(self.owner_lights[owner], light)
                if not self.owner_lights[owner]:
                    self.owner_lights.pop(owner, None)
                return None
            target_list.append(light)
        self.shaders['light']['num_lights'] = len(self.active_lights)
        return light

    def remove(self, light):
        self._remove_light(light, promote=True)

    def _remove_light(self, light, *, promote):
        self._remove_from_list(self.active_lights, light)
        self._remove_from_list(self.paused_lights, light)
        owner = light.owner
        if owner is not None:
            lights = self.owner_lights.get(owner, [])
            self._remove_from_list(lights, light)
            if not lights:
                self.owner_lights.pop(owner, None)
        light.owner = None
        if promote:
            self._promote_paused_lights()
        self.shaders['light']['num_lights'] = len(self.active_lights)

    def detach_from_owner(self, light):
        owner = light.owner
        if owner is None:
            return

        lights = self.owner_lights.get(owner, [])
        self._remove_from_list(lights, light)
        if not lights:
            self.owner_lights.pop(owner, None)
        light.owner = None

        if light in self.paused_lights:
            # Detached lights become free-floating effects, but they still respect
            # the active-light cap instead of bypassing it.
            if self._has_active_capacity():
                self.paused_lights.remove(light)
                self.active_lights.append(light)
            else:
                self._promote_paused_lights()

        self.shaders['light']['num_lights'] = len(self.active_lights)

    def on_owner_slept(self, owner):
        for light in self.owner_lights.get(owner, []):
            if light in self.active_lights:
                self.active_lights.remove(light)
                self.paused_lights.append(light)
        self._promote_paused_lights()
        self.shaders['light']['num_lights'] = len(self.active_lights)

    def on_owner_woke(self, owner):
        for light in self.owner_lights.get(owner, []):
            # Waking is best-effort: the owner may wake without recovering all of
            # its lights if the active pool is already full.
            if not self._has_active_capacity():
                break
            if light in self.paused_lights:
                self.paused_lights.remove(light)
                self.active_lights.append(light)
        self.shaders['light']['num_lights'] = len(self.active_lights)

    def remove_owner_lights(self, owner):
        for light in list(self.owner_lights.get(owner, [])):
            self._remove_light(light, promote=False)
        self._promote_paused_lights()
        self.shaders['light']['num_lights'] = len(self.active_lights)

    def _get_managed_owner(self, target):
        if getattr(target, 'always_active', False):
            return None
        if not hasattr(target, 'group') or not hasattr(target, 'pause_group'):
            return None
        return target

    @staticmethod
    def _remove_from_list(items, light):
        if light in items:
            items.remove(light)

    def _has_active_capacity(self):
        return len(self.active_lights) < self.max_light_sources

    def _promote_paused_lights(self):
        if not self._has_active_capacity():
            return

        for light in list(self.paused_lights):
            if not self._has_active_capacity():
                break
            if not self._is_wake_eligible(light):
                continue
            self.paused_lights.remove(light)
            self.active_lights.append(light)

    @staticmethod
    def _is_wake_eligible(light):
        owner = light.owner
        if owner is None:
            return False
        return owner.pause_group not in owner.groups()

    def draw(self, target):
        self.layer1.clear(0, 0, 0, 0)
        self.layer2.clear(0, 0, 0, 0)
        self.layer3.clear(0, 0, 0, 0)
        self.screen_copy.clear(0, 0, 0, 0)

        self.shaders['light']['rectangleCorners'] = self.points
        self.shaders['light']['occluder_start_index'] = self.occluder_start_index
        self.shaders['light']['lightPositions'] = self.positions
        self.shaders['light']['lightRadii'] = self.radius
        self.shaders['light']['colour'] = self.colour
        self.shaders['light']['ambient'] = self.ambient
        self.shaders['light']['angleStart'] = self.start_angle
        self.shaders['light']['angleEnd'] = self.end_angle
        self.shaders['light']['min_radius'] = self.min_radius
        self.shaders['light']['num_rectangle'] = self.num_rectangle
        self.shaders['light']['normal_interact'] = self.normal_interact
        self.shaders['light']['normal_map'] = self.normal_map.texture

        self.game_objects.game.display.render(target.texture, self.screen_copy)
        self.shaders['blend']['background'] = self.screen_copy.texture
        self.shaders['blur']['r'] = self._blur_r_int
        self.shaders['blur']['weights'] = self._blur_weights


        self.game_objects.game.display.use_alpha_blending(False)
        self.game_objects.game.display.render(self.layer1.texture, self.layer2, shader=self.shaders['light'])
        self.game_objects.game.display.render(self.layer2.texture, self.layer3, shader=self.shaders['blur'])
        self.game_objects.game.display.use_alpha_blending(True)
        self.game_objects.game.display.render(self.layer3.texture, target, scale=self.game_objects.game.scale, shader=self.shaders['blend'])
