import pygame

from gameplay.ui.loaders import DomainMapLoader, ScrollableWorldMapLoader

from .base import BaseUI
from .navigation import find_closest_in_direction


class MapUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.map_UIs = {}
        self.local_map_UIs = {}
        self.map_name = None
        self.map_UI = None
        self.selected_container = None
        self.scroll = [0, 0]
        self.pos = [0, 0]
        assumed_map_size = (640 * 2, 360 * 2)
        self.map_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.mask_view = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.mask = game_objects.game.display.make_layer(assumed_map_size)
        self.mask_surface = pygame.Surface(
            assumed_map_size, pygame.SRCALPHA, 32
        ).convert_alpha()
        self.has_mask = False
        self.world_map_name = 'worldmap'

    def on_enter(self, **kwarg):
        super().on_enter(**kwarg)
        self.map_name = kwarg.get('map', self.game_objects.map.biome_mgr.current_biome_name)
        self.map_UI = self.resolve_map_loader(self.map_name)
        self.selected_container = self.find_initial_selection()
        self.center_on_selection()
        self.refresh_objects_scroll()
        self.rebuild_mask()

    def update(self, dt):
        super().update(dt)
        if self.selected_container in self.map_UI.markers:
            self.selected_container.update(dt)
        self.continious_input()
        self.update_pos(self.scroll)
        self.limit_pos()
        self.refresh_objects_scroll()

    def render(self):
        self.game_objects.ui.backpack.screen.clear(0, 0, 0, 0)
        self.map_layer.clear(0, 0, 0, 255)
        self.game_objects.game.display.render(
            self.map_UI.BG, self.map_layer, position=self.pos
        )
        self.render_map_objects(self.map_UI.markers, target=self.map_layer)

        if self.has_mask:
            self.mask_view.clear(0, 0, 0, 0)
            self.game_objects.shaders['blur']['blurRadius'] = 5
            self.game_objects.game.display.render(
                self.mask.texture,
                self.mask_view,
                position=self.pos,
                shader=self.game_objects.shaders['blur'],
            )
            shader = self.game_objects.shaders['mask']
            shader['maskTexture'] = self.mask_view.texture
            shader['maskColour'] = (0.0, 0.0, 0.0, 1.0)
            self.game_objects.game.display.render(
                self.map_layer.texture,
                self.game_objects.ui.backpack.screen,
                shader=shader,
            )
        else:
            self.game_objects.game.display.render(
                self.map_layer.texture, self.game_objects.ui.backpack.screen
            )

        self.render_map_objects(
            self.get_map_ui_elements(),
            target=self.game_objects.ui.backpack.screen,
        )
        self.render_map_objects(
            self.get_map_ui_buttons(),
            target=self.game_objects.ui.backpack.screen,
        )
        self.blit_screen()

    def handle_events(self, input):
        input.processed()

        if input.pressed:
            if input.name == 'select':
                self.exit_state()
            elif input.name == 'rb':
                self.next_page(screen_alpha=230)
            elif input.name == 'a':
                pass
            elif input.name == 'x':
                if self.map_name == self.world_map_name:
                    map_name = self.game_objects.map.biome_mgr.current_biome_name
                else:
                    map_name = self.world_map_name
                self.game_objects.ui.backpack.set_page('map', screen_alpha=230, map=map_name)
            elif input.name in ('up', 'down', 'left', 'right'):
                next_container = self.find_closest_position(input.name)
                if next_container:
                    self.reset_selected()
                    self.selected_container = next_container
                    self.calculate_position()

    def find_closest_position(self, direction):
        return find_closest_in_direction(
            self.selected_container,
            self.map_UI.markers,
            direction,
        )

    def continious_input(self):
        value = self.game_objects.controller.frame.axes.look
        self.scroll = [-2 * value[0], -2 * value[1]]

    def update_pos(self, scroll):
        self.pos = [self.pos[0] + scroll[0], self.pos[1] + scroll[1]]

    def limit_pos(self):
        if self.pos[0] > 0:
            self.pos[0] = 0
            self.scroll[0] = 0
        elif self.pos[0] < self.game_objects.game.window_size[0] - self.map_UI.BG.width:
            self.pos[0] = self.game_objects.game.window_size[0] - self.map_UI.BG.width
            self.scroll[0] = 0

        if self.pos[1] > 0:
            self.pos[1] = 0
            self.scroll[1] = 0
        elif self.pos[1] < self.game_objects.game.window_size[1] - self.map_UI.BG.height:
            self.pos[1] = self.game_objects.game.window_size[1] - self.map_UI.BG.height
            self.scroll[1] = 0

    def calculate_position(self):
        if not self.selected_container:
            return
        world_center = self.selected_container.get_world_center()
        self.pos = [
            -world_center[0] + self.game_objects.game.window_size[0] * 0.5,
            -world_center[1] + self.game_objects.game.window_size[1] * 0.5,
        ]
        self.limit_pos()
        self.refresh_objects_scroll()

    def center_on_selection(self):
        if self.selected_container:
            self.calculate_position()
            return

        self.pos = [
            -0.5 * (self.map_UI.BG.width - self.game_objects.game.window_size[0]),
            -0.5 * (self.map_UI.BG.height - self.game_objects.game.window_size[1]),
        ]
        self.limit_pos()

    def refresh_objects_scroll(self):
        for object in self.map_UI.markers:
            object.update_scroll(self.pos)
        for object in self.get_map_ui_elements():
            object.update_scroll(self.pos)

    def reset_selected(self):
        if self.selected_container and hasattr(self.selected_container, 'reset'):
            self.selected_container.reset()

    def find_initial_selection(self):
        if not self.map_UI.markers:
            return None

        current_biome = self.game_objects.map.biome_mgr.current_biome_name
        for object in self.map_UI.markers:
            if getattr(object, 'map_text', None) == current_biome:
                return object
        return self.map_UI.markers[0]

    def rebuild_mask(self):
        reveal_areas = self.map_UI.reveal_areas
        state_map_name = self.get_state_map_name()
        revealed = self.game_objects.world_state.map_state.get_revealed_areas(state_map_name)

        if not reveal_areas or not revealed:
            self.has_mask = False
            return

        self.has_mask = True
        self.mask_surface.fill((0, 0, 0, 255))

        for area_id in revealed:
            for points in reveal_areas.get(area_id, []):
                if len(points) >= 3:
                    pygame.draw.polygon(
                        self.mask_surface,
                        (0, 0, 0, 0),
                        points,
                    )

        mask_texture = self.game_objects.game.display.surface_to_texture(
            self.mask_surface
        )
        self.mask.clear(0, 0, 0, 0)
        self.game_objects.game.display.render(mask_texture, self.mask)
        mask_texture.release()

    def resolve_map_loader(self, map_name):
        if map_name == self.world_map_name:
            if map_name not in self.map_UIs:
                self.map_UIs[map_name] = ScrollableWorldMapLoader(self.game_objects)
            return self.map_UIs[map_name]

        if map_name not in self.local_map_UIs:
            self.local_map_UIs[map_name] = DomainMapLoader(self.game_objects)
        return self.local_map_UIs[map_name]

    def get_state_map_name(self):
        if self.map_name == self.world_map_name:
            return self.world_map_name
        return self.map_name

    def render_map_objects(self, objects, target):
        for object in objects:
            if hasattr(object, 'draw'):
                object.draw(target)
            else:
                self.game_objects.game.display.render(
                    object.image,
                    target,
                    position=object.rect.topleft,
                )

    def get_map_ui_elements(self):
        return [object for object in self.map_UI.ui_elements if not hasattr(object, 'button')]

    def get_map_ui_buttons(self):
        return list(self.map_UI.buttons.values())
