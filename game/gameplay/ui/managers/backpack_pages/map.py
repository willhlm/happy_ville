import pygame

from gameplay.ui.components import MapCursor, PlayerMapMarker
from gameplay.ui.loaders import DomainMapLoader, ScrollableWorldMapLoader

from .base import BaseUI
from .navigation import find_closest_in_direction


class MapUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.world_map_UI = None
        self.local_map_UI = None
        self.map_name = None
        self.map_UI = None
        self.selected_container = None
        self.visible_markers = []
        self.scroll = [0, 0]
        self.pos = [0, 0]
        self.map_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.mask_view = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.mask = None
        self.mask_surface = None
        self.mask_size = None
        self.has_mask = False
        self.player_marker = PlayerMapMarker(game_objects)
        self.cursor = MapCursor(game_objects)
        self.world_map_name = 'worldmap'

    def on_enter(self, **kwarg):
        super().on_enter(**kwarg)
        self.map_name = kwarg.get('map', self.game_objects.map.biome_mgr.current_biome_name)
        self.map_UI = self.resolve_map_loader(self.map_name)
        self.ensure_mask_resources()
        self.rebuild_mask()
        self.update_player_marker()
        self.visible_markers = self.get_visible_markers()
        self.selected_container = self.find_initial_selection()
        self.cursor.select(self.selected_container)
        self.center_on_selection()
        self.refresh_objects_scroll()

    def update(self, dt):
        super().update(dt)
        self.visible_markers = self.get_visible_markers()
        if self.selected_container in self.visible_markers:
            self.selected_container.update(dt)
        self.cursor.update(dt)
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
        self.render_map_objects(self.visible_markers, target=self.map_layer)

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

        self.cursor.draw(self.game_objects.ui.backpack.screen)
        self.player_marker.draw(self.game_objects.ui.backpack.screen)

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
                self.activate_selected_marker()
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
                    self.cursor.select(next_container)
                    self.calculate_position()

    def activate_selected_marker(self):
        if self.selected_container not in self.get_selectable_markers():
            return

        if self.map_name != self.world_map_name:
            self.travel_to_selected_marker()
            return

        destination = getattr(self.selected_container, 'destination_map', None)
        if not destination and hasattr(self.selected_container, 'activate'):
            destination = self.selected_container.activate()
        if not destination:
            return

        self.game_objects.ui.backpack.set_page(
            'map',
            screen_alpha=230,
            map=destination,
        )

    def travel_to_selected_marker(self):
        marker = self.selected_container
        unlock_data = getattr(marker, 'unlock_data', {})
        if not unlock_data.get('fast_travel', False):
            return

        destination = unlock_data.get('room_id') or getattr(marker, 'room_id', None)
        spawn_position = (
            unlock_data.get('spawn_position')
            or getattr(marker, 'spawn_position', None)
        )
        if not destination or spawn_position is None:
            return

        state_manager = self.game_objects.game.state_manager
        state_manager.exit_state()
        previous_state = state_manager.state_stack[-1]
        self.game_objects.sequence_manager.start_sequence(
            'sejte_travel',
            destination=destination,
            spawn=spawn_position,
            previous_state=previous_state,
        )

    def find_closest_position(self, direction):
        return find_closest_in_direction(
            self.selected_container,
            self.get_selectable_markers(),
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
        self.center_on_world_position(self.selected_container.get_world_center())

    def center_on_world_position(self, world_center):
        self.pos = [
            -world_center[0] + self.game_objects.game.window_size[0] * 0.5,
            -world_center[1] + self.game_objects.game.window_size[1] * 0.5,
        ]
        self.limit_pos()
        self.refresh_objects_scroll()

    def center_on_selection(self):
        if self.map_name != self.world_map_name and self.player_marker.visible:
            self.center_on_world_position(self.player_marker.get_world_center())
            return

        if self.selected_container:
            self.calculate_position()
            return

        self.pos = [
            -0.5 * (self.map_UI.BG.width - self.game_objects.game.window_size[0]),
            -0.5 * (self.map_UI.BG.height - self.game_objects.game.window_size[1]),
        ]
        self.limit_pos()

    def refresh_objects_scroll(self):
        for object in self.visible_markers:
            object.update_scroll(self.pos)
        for object in self.get_map_ui_elements():
            if hasattr(object, 'update_scroll'):
                object.update_scroll(self.pos)
        self.player_marker.update_scroll(self.pos)

    def reset_selected(self):
        if self.selected_container and hasattr(self.selected_container, 'reset'):
            self.selected_container.reset()

    def find_initial_selection(self):
        selectable_markers = self.get_selectable_markers()
        if not selectable_markers:
            return None

        current_biome = self.game_objects.map.biome_mgr.current_biome_name
        for object in selectable_markers:
            if getattr(object, 'map_text', None) == current_biome:
                return object
        return selectable_markers[0]

    def ensure_mask_resources(self):
        map_size = (self.map_UI.BG.width, self.map_UI.BG.height)
        if self.mask_size == map_size:
            return

        if self.mask is not None:
            self.mask.release()

        self.mask_size = map_size
        self.mask = self.game_objects.game.display.make_layer(map_size)
        self.mask_surface = pygame.Surface(
            map_size, pygame.SRCALPHA, 32
        ).convert_alpha()

    def rebuild_mask(self):
        reveal_areas = self.map_UI.reveal_areas
        revealed = self.get_revealed_areas()

        # A map with no reveal geometry is intentionally always visible. Once reveal
        # geometry exists, an empty discovery set must leave the geographical art hidden.
        if not reveal_areas:
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

    def update_player_marker(self):
        self.player_marker.hide()
        if self.map_name == self.world_map_name:
            return

        room_id = self.get_current_room_id()
        locator = self.map_UI.locator_areas.get(room_id)
        map_definition = self.game_objects.map.map_def
        if locator is None or map_definition is None:
            return

        room_data = map_definition.map_data
        room_width = room_data.get('width', 0) * room_data.get('tilewidth', 0)
        room_height = room_data.get('height', 0) * room_data.get('tileheight', 0)
        if room_width <= 0 or room_height <= 0:
            return

        player_x, player_y = self.game_objects.player.hitbox.center
        normalized_x = max(0.0, min(1.0, player_x / room_width))
        normalized_y = max(0.0, min(1.0, player_y / room_height))
        self.player_marker.set_world_center((
            locator.left + normalized_x * locator.width,
            locator.top + normalized_y * locator.height,
        ))

    def resolve_map_loader(self, map_name):
        if map_name == self.world_map_name:
            if self.world_map_UI is None:
                self.world_map_UI = ScrollableWorldMapLoader(self.game_objects)
            return self.world_map_UI

        # The detailed local map contains every domain, so all domain names resolve
        # to the same loader and the same illustrated map.
        if self.local_map_UI is None:
            self.local_map_UI = DomainMapLoader(self.game_objects)
        return self.local_map_UI

    def get_revealed_areas(self):
        map_state = self.game_objects.world_state.map_state
        if self.map_name == self.world_map_name:
            return map_state.get_revealed_areas(self.world_map_name)
        return map_state.get_all_revealed_areas(exclude=(self.world_map_name,))

    def get_visited_areas(self):
        map_state = self.game_objects.world_state.map_state
        if self.map_name == self.world_map_name:
            return map_state.get_visited_areas(self.world_map_name)
        return map_state.get_all_visited_areas(exclude=(self.world_map_name,))

    def get_unlocked_markers(self):
        map_state = self.game_objects.world_state.map_state
        if self.map_name == self.world_map_name:
            return map_state.get_unlocked_markers(self.world_map_name)
        return map_state.get_all_unlocked_markers(exclude=(self.world_map_name,))

    def get_current_room_id(self):
        map_definition = self.game_objects.map.map_def
        if map_definition is None:
            return ""
        return map_definition.biome_room_name

    def get_visible_markers(self):
        revealed = self.get_revealed_areas()
        visited = self.get_visited_areas()
        unlocked_markers = self.get_unlocked_markers()
        visible_markers = []
        for marker in self.map_UI.markers:
            visibility = getattr(marker, 'visibility', 'always')
            area_id = getattr(marker, 'room_id', None)

            if visibility == 'always':
                visible = True
            elif visibility in ('revealed', 'discovered'):
                visible = area_id is not None and str(area_id) in revealed
            elif visibility == 'visited':
                visible = area_id is not None and str(area_id) in visited
            elif visibility == 'unlocked':
                marker_id = getattr(marker, 'marker_id', None)
                visible = (
                    marker_id is not None
                    and str(marker_id) in unlocked_markers
                ) or bool(getattr(marker, 'unlocked', False))
                if visible and marker_id is not None:
                    marker.unlock_data = unlocked_markers.get(str(marker_id), {})
                    marker.spawn_position = (
                        marker.spawn_position
                        or marker.unlock_data.get('spawn_position')
                    )
                    normalized_position = marker.unlock_data.get(
                        'normalized_room_position'
                    )
                    locator = self.map_UI.locator_areas.get(str(area_id))
                    if (
                        normalized_position
                        and locator is not None
                        and hasattr(marker, 'set_world_center')
                    ):
                        marker.set_world_center((
                            locator.left + normalized_position[0] * locator.width,
                            locator.top + normalized_position[1] * locator.height,
                        ))
            else:
                visible = False

            if visible:
                visible_markers.append(marker)
        return visible_markers

    def get_selectable_markers(self):
        return [
            marker
            for marker in self.visible_markers
            if getattr(marker, 'selectable', True)
        ]

    def render_map_objects(self, objects, target):
        for object in objects:
            if hasattr(object, 'draw'):
                object.draw(target)
            elif hasattr(object, 'render'):
                object.render(target)
            else:
                self.game_objects.game.display.render(
                    object.image,
                    target,
                    position=object.rect.topleft,
                )

    def get_map_ui_elements(self):
        return self.map_UI.ui_elements

    def get_map_ui_buttons(self):
        return list(self.map_UI.controller_prompts.values())
