from gameplay.ui.components import InventoryPointer
from gameplay.ui.loaders import RadnaLoader

from .base import BaseUI
from .navigation import find_closest_in_direction


class RadnaUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.radna_UI = RadnaLoader(game_objects)
        self.pointer = InventoryPointer([0, 0], game_objects)
        self.selected_container = self.radna_UI.containers[0]

    def update(self, dt):
        super().update(dt)
        self.radna_UI.items['hand'].animation.update(dt)

        for key in self.game_objects.player.backpack.radna.rings.keys():
            ring = self.game_objects.player.backpack.radna.get_ring(key)
            if not ring.unlocked:
                continue
            ring.animation.update(dt)

    def render(self):
        self.game_objects.ui.backpack.screen.clear(0, 0, 0, 0)
        self.blit_BG()
        self.blit_hand()
        self.blit_containers()
        self.blit_radnas()
        self.blit_rings()
        self.blit_pointer()
        self.blit_description()
        self.blit_screen()

    def blit_BG(self):
        self.game_objects.game.display.render(self.radna_UI.BG, self.game_objects.ui.backpack.screen)

    def blit_containers(self):
        for container in self.radna_UI.containers:
            self.game_objects.game.display.render(
                container.image,
                self.game_objects.ui.backpack.screen,
                position=container.rect.topleft,
            )

        for container in self.radna_UI.equipped_containers.values():
            self.game_objects.game.display.render(
                container.image,
                self.game_objects.ui.backpack.screen,
                position=container.rect.topleft,
            )

    def blit_radnas(self):
        for key in self.game_objects.player.backpack.radna.inventory.keys():
            item = self.game_objects.player.backpack.radna.get_radna(key)
            self.game_objects.shaders['colour']['colour'] = (0, 0, 0, 255)
            self.game_objects.game.display.render(
                item.image,
                self.game_objects.ui.backpack.screen,
                position=self.radna_UI.items[key],
                shader=item.shader,
            )

        for finger in self.game_objects.player.backpack.radna.rings.keys():
            ring = self.game_objects.player.backpack.radna.rings[finger]
            if not ring.attached_radna:
                continue
            self.game_objects.game.display.render(
                ring.attached_radna.image,
                self.game_objects.ui.backpack.screen,
                position=self.radna_UI.equipped_containers[finger].rect.topleft,
            )

    def blit_rings(self):
        for key in self.game_objects.player.backpack.radna.rings.keys():
            ring = self.game_objects.player.backpack.radna.get_ring(key)
            if not ring.unlocked:
                continue
            ring.animation.update(dt=1)
            self.game_objects.game.display.render(
                ring.image,
                self.game_objects.ui.backpack.screen,
                position=self.radna_UI.rings[key],
            )

    def blit_pointer(self):
        pos = self.selected_container.rect.topleft
        self.game_objects.game.display.render(
            self.pointer.image, self.game_objects.ui.backpack.screen, position=pos
        )

    def blit_hand(self):
        self.game_objects.shaders['colour']['colour'] = (0, 0, 0, 255)
        self.game_objects.game.display.render(
            self.radna_UI.items['hand'].image,
            self.game_objects.ui.backpack.screen,
            position=self.radna_UI.items['hand'].rect.topleft,
            shader=self.game_objects.shaders['colour'],
        )

    def blit_description(self):
        item_name = self.selected_container.get_item()
        item = self.game_objects.player.backpack.radna.get_radna(item_name)
        if item:
            self.dark(item)
            self.conv = item.description
            self.game_objects.shaders['colour']['colour'] = (255, 255, 255, 255)
            self.game_objects.font.render(
                self.game_objects.ui.backpack.screen,
                position=(320, 220),
                text=self.conv,
                width=140,
                letter_frame=int(self.letter_frame // 2),
            )

    def dark(self, item):
        if item.equipped_ring is not None:
            return
        slot = self.game_objects.player.backpack.radna.find_compatible_slot(item)
        if not slot:
            return
        self.game_objects.shaders['colour']['colour'] = (0, 0, 0, 255)
        self.game_objects.game.display.render(
            item.image,
            self.game_objects.ui.backpack.screen,
            position=self.radna_UI.equipped_containers[slot].rect.topleft,
            shader=self.game_objects.shaders['colour'],
        )

    def handle_events(self, input):
        input.processed()
        if input.pressed:
            if input.name == 'select':
                self.exit_state()
            elif input.name == 'rb':
                self.next_page(screen_alpha=230)
            elif input.name == 'lb':
                self.previous_page(screen_alpha=230)
            elif input.name == 'a' or input.name == 'return':
                self.use_item()
            elif input.name in ('up', 'down', 'left', 'right'):
                next_container = self.find_closest_position(input.name)
                if next_container:
                    self.selected_container = next_container
                    self.letter_frame = 0

    def find_closest_position(self, direction):
        return find_closest_in_direction(
            self.selected_container,
            self.radna_UI.containers,
            direction,
        )

    def use_item(self):
        item_name = self.selected_container.get_item()
        new_radna = self.game_objects.player.backpack.radna.get_radna(item_name)
        if not new_radna:
            return
        if new_radna.equipped_ring is None:
            self.game_objects.player.backpack.radna.equip_item(new_radna)
        else:
            self.game_objects.player.backpack.radna.remove_item(new_radna)
