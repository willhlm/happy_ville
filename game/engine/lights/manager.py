from engine.render.blur_kernel import build_gaussian_kernel

from engine.lights.source import LightSource


class LightManager:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.set_ambient_light([0, 0, 0, 0])
        self.light_sources = []
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

    def update_render(self, dt):
        self.normal_interact = [0] * self.max_light_sources
        self.num_rectangle = [0] * self.max_light_sources
        self.occluder_start_index = [0] * self.max_light_sources
        self.points = []
        self.positions = [(0, 0)] * self.max_light_sources
        self.radius = [0] * self.max_light_sources
        self.colour = [[0, 0, 0, 0] for _ in range(self.max_light_sources)]
        self.start_angle = [0] * self.max_light_sources
        self.end_angle = [0] * self.max_light_sources
        self.min_radius = [0] * self.max_light_sources
        rectangle_cursor = 0
        active_light_count = 0

        for light in self.light_sources[:]:
            light.update(dt)
            if not self._should_render_light(light):
                continue

            self.positions[active_light_count] = (
                light.position[0],
                self.game_objects.game.window_size[1] - light.position[1],
            )
            self.radius[active_light_count] = light.radius
            self.colour[active_light_count] = light.colour
            self.start_angle[active_light_count] = light.start_angle
            self.end_angle[active_light_count] = light.end_angle
            self.min_radius[active_light_count] = light.min_radius
            self.normal_interact[active_light_count] = light.normal_interact
            rectangle_cursor = self.list_points(light, active_light_count, rectangle_cursor)
            active_light_count += 1

        self.points.extend([(0, 0)] * (self.max_occluder_rectangles * 4 - len(self.points)))
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

        platforms = self.game_objects.physics.platform_spatial_index.query_rect(light.hitbox)
        available = max(self.max_occluder_rectangles - rectangle_cursor, 0)
        platforms = platforms[:available]
        self.occluder_start_index[index] = rectangle_cursor
        self.num_rectangle[index] = len(platforms)
        self.points.extend(self.get_points(platforms))
        return rectangle_cursor + len(platforms)

    def get_points(self, platforms):
        points = []
        scroll = self.game_objects.camera_manager.camera.scroll
        for rec in platforms:
            points += [
                (rec.hitbox.topleft[0] - scroll[0], rec.hitbox.topleft[1] - scroll[1]),
                (rec.hitbox.topright[0] - scroll[0], rec.hitbox.topright[1] - scroll[1]),
                (rec.hitbox.bottomright[0] - scroll[0], rec.hitbox.bottomright[1] - scroll[1]),
                (rec.hitbox.bottomleft[0] - scroll[0], rec.hitbox.bottomleft[1] - scroll[1]),
            ]
        return points

    def clear_lights(self):
        self.light_sources = []
        self.shaders['light']['num_lights'] = 0

    def create(self, target, *, components=None, **properties):
        if len(self.light_sources) >= self.max_light_sources:
            return None

        light = LightSource(self.game_objects, target, components=components, **properties)
        self.light_sources.append(light)
        self.shaders['light']['num_lights'] = len(self.light_sources)
        return light

    def remove(self, light):
        if light in self.light_sources:
            self.light_sources.remove(light)
            self.shaders['light']['num_lights'] = len(self.light_sources)

    def draw(self, target):
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
        self.layer2.clear(0, 0, 0, 0)
        self.layer3.clear(0, 0, 0, 0)

        self.game_objects.game.display.use_alpha_blending(False)
        self.game_objects.game.display.render(self.layer1.texture, self.layer2, shader=self.shaders['light'])
        self.game_objects.game.display.render(self.layer2.texture, self.layer3, shader=self.shaders['blur'])
        self.game_objects.game.display.use_alpha_blending(True)
        self.game_objects.game.display.render(self.layer3.texture, target, scale=self.game_objects.game.scale, shader=self.shaders['blend'])
