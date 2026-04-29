from gameplay.ui.components import InventoryPointer
from gameplay.ui.loaders import InventoryLoader

from .base import BaseUI
from .navigation import find_closest_in_direction


class InventoryUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.iventory_UI = InventoryLoader(game_objects)
        self.selected_container = self.iventory_UI.containers[0]

        self.pointer = InventoryPointer([0, 0], game_objects)
        self.define_botton_texts(game_objects)

    def define_botton_texts(self, game_objects):
        self.texts = ['select', 'exit', 'Map', 'Omamori']

    def update(self, dt):
        super().update(dt)
        self.iventory_UI.items['sword'].animation.update(dt)
        for button in self.iventory_UI.buttons.values():
            button.update(dt)

    def render(self):
        self.game_objects.ui.backpack.screen.clear(0, 0, 0, 0)
        self.blit_inventory_BG()
        self.blit_inventory()
        self.blit_sword()
        self.blit_pointer()
        self.blit_description()
        self.blit_bottons()
        self.blit_screen()

    def blit_inventory_BG(self):
        self.game_objects.game.display.render(
            self.iventory_UI.BG, self.game_objects.ui.backpack.screen
        )

    def blit_inventory(self):
        for container in self.iventory_UI.containers:
            self.game_objects.game.display.render(
                container.image,
                self.game_objects.ui.backpack.screen,
                position=container.rect.topleft,
            )

        for key in self.game_objects.player.backpack.inventory.items.keys():
            item = self.game_objects.player.backpack.inventory.get_item(key)
            item.animation.update(dt=1)
            self.game_objects.game.display.render(
                item.image,
                self.game_objects.ui.backpack.screen,
                position=self.iventory_UI.items[key],
            )

            quantity = self.game_objects.player.backpack.inventory.get_quantity(key)
            text = str(quantity)
            topleft = self.iventory_UI.items[key]
            position = [topleft[0] + 50, topleft[1]]
            self.game_objects.font.render(
                self.game_objects.ui.backpack.screen,
                text=text,
                letter_frame=None,
                color=(255, 255, 255, 255),
                position=position,
            )

    def blit_sword(self):
        self.game_objects.game.display.render(
            self.iventory_UI.items['sword'].image,
            self.game_objects.ui.backpack.screen,
            position=self.iventory_UI.items['sword'].rect.topleft,
        )

    def blit_pointer(self):
        pos = self.selected_container.rect.topleft
        self.game_objects.game.display.render(
            self.pointer.image, self.game_objects.ui.backpack.screen, position=pos
        )

    def blit_description(self):
        item_name = self.selected_container.get_item()
        item = self.game_objects.player.backpack.inventory.get_item(item_name)
        if item:
            self.conv = item.description
            self.game_objects.shaders['colour']['colour'] = (255, 255, 255, 255)
            self.game_objects.font.render(
                self.game_objects.ui.backpack.screen,
                position=(420, 150),
                text=self.conv,
                width=140,
                letter_frame=int(self.letter_frame // 2),
            )

    def blit_bottons(self):
        for index, button in enumerate(self.iventory_UI.buttons.values()):
            self.game_objects.game.display.render(
                button.image,
                self.game_objects.ui.backpack.screen,
                position=button.rect.topleft,
            )
            self.game_objects.font.render(
                self.game_objects.ui.backpack.screen,
                self.texts[index],
                position=button.rect.center,
            )

    def handle_events(self, input):
        input.processed()
        if input.pressed:
            if input.name == 'select':
                self.exit_state()
            elif input.name == 'rb':
                self.iventory_UI.buttons['rb'].currentstate.handle_input('press')
                self.next_page(screen_alpha=230)
            elif input.name == 'lb':
                self.iventory_UI.buttons['lb'].currentstate.handle_input('press')
                self.previous_page(screen_alpha=230)
            elif input.name == 'a' or input.name == 'return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('press')
                self.use_item()
            elif input.name in ('up', 'down', 'left', 'right'):
                next_container = self.find_closest_position(input.name)
                if next_container:
                    self.selected_container = next_container
                    self.letter_frame = 0

        if input.released:
            if input.name == 'a' or input.name == 'return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('release')

    def find_closest_position(self, direction):
        return find_closest_in_direction(
            self.selected_container,
            self.iventory_UI.containers,
            direction,
        )

    def use_item(self):
        item_name = self.selected_container.get_item()
        item = self.game_objects.player.backpack.inventory.get_item(item_name)

        if not item:
            return
        if self.game_objects.player.backpack.inventory.get_quantity(item_name) <= 0:
            return
        item.use_item()
