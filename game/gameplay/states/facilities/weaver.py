import pygame, sys
from gameplay.states.base.game_state import GameState
from gameplay.ui.loaders import WeaverLoader
from gameplay.ui.components import InventoryPointer

class Weaver(GameState):
    MAX_PALETTE_SWAP_COLOURS = 32

    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = WeaverLoader(game.game_objects)
        self.category_order = tuple(self.menu_ui.categories.keys())
        self.active_category_index = 0
        dyes = self.game.game_objects.player.backpack.inventory.dyes.values()
        self.menu_ui.assign_dyes(dyes)

    def update(self, dt):
        self.menu_ui.player.update(dt)

    def render(self):                
        self.game.display.render(self.menu_ui.bg, self.game.screen_manager.screen)
        self._render_colour_swap()
        self._render_texts()
        self._render_dye_icons()
        self.game.render_display(self.game.screen_manager.screen.texture)

    def _render_texts(self):
        active_category = self._get_active_category()
        texts = getattr(self.menu_ui, 'texts', [])
        for text in texts:
            text.colour = [255, 255, 0, 255] if text.text == active_category else [255, 255, 255, 255]
            text.render(self.game.screen_manager.screen)
  
    def handle_events(self, input):
        input.processed()
        if input.pressed:
            if input.name in ('start', 'y'):
                self.game.state_manager.exit_state()
            elif input.name == 'up':
                self._move_category(-1)
            elif input.name == 'down':
                self._move_category(1)
            elif input.name == 'left':
                self._move_selection(-1)
            elif input.name == 'right':
                self._move_selection(1)

    def _render_colour_swap(self):
        shader = self.game.game_objects.shaders['palette_swap']

        original_colours = []
        replace_colours = []

        for category in self.category_order:
            dye = self._get_selected_dye(category)
            if dye is None:
                continue
            original_colours.extend(dye.target_colour)
            replace_colours.extend(dye.repalce_colour)

        self._set_palette_swap_uniforms(shader, original_colours, replace_colours)

        self.game.display.render(
            self.menu_ui.player.image,
            self.game.screen_manager.screen,
            position=self.menu_ui.player.rect.topleft,
            shader=shader,
        )

    def _render_dye_icons(self):
        for category in self.category_order:
            entry = self.menu_ui.categories[category]
            container = entry['container']
            pos = container.rect.topleft
            dye = self._get_selected_dye(category)

            if dye is None:
                self.game.display.render_text(
                    self.game.game_objects.font.font_atals,
                    self.game.screen_manager.screen,
                    'default',
                    letter_frame=1000,
                    color=(255, 255, 255, 255),
                    position=pos,
                    width=container.rect.width,
                )
                continue

            self.game.display.render(dye.image, self.game.screen_manager.screen, position=pos)

    def _set_palette_swap_uniforms(self, shader, original_colours, replace_colours):
        colour_count = min(len(original_colours), len(replace_colours), self.MAX_PALETTE_SWAP_COLOURS)
        shader['number_colour'] = colour_count
        shader['original_colors'] = self._format_palette_uniform(original_colours, colour_count)
        shader['replace_colors'] = self._format_palette_uniform(replace_colours, colour_count)

    def _format_palette_uniform(self, colours, colour_count):
        padded = list(colours[:colour_count])
        padded.extend([(0, 0, 0, 0)] * (self.MAX_PALETTE_SWAP_COLOURS - colour_count))
        return tuple(tuple(colour) for colour in padded)

    def _move_selection(self, direction):
        category = self._get_active_category()
        if category is None:
            return

        entry = self.menu_ui.categories[category]
        dyes = entry['dyes']
        if not dyes:
            entry['index'] = 0
            return

        entry['index'] = (entry['index'] + direction) % len(dyes)

    def _get_selected_dye(self, category):
        entry = self.menu_ui.categories.get(category)
        if entry is None:
            return None

        dyes = entry['dyes']
        if not dyes:
            return None

        entry['index'] = max(0, min(entry['index'], len(dyes) - 1))
        return dyes[entry['index']]

    def _move_category(self, direction):
        if not self.category_order:
            return

        self.active_category_index = (self.active_category_index + direction) % len(self.category_order)

    def _get_active_category(self):
        if not self.category_order:
            return None
        return self.category_order[self.active_category_index]
