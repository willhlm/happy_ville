from engine.utils import read_files
from gameplay.ui.components import Button, MenuArrow

from ..base_loader import BaseLoader


class TitleMenuLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        self.sprites = read_files.load_sprites_dict("assets/sprites/ui/menus/title_menu/", game_objects)
        self.sounds = read_files.load_sounds_dict("assets/audio/music/load_screen/")
        path = "assets/ui_layouts/menus/title_menu/title_menu.json"
        self.load_UI_data(path, "title_menu")
        self.load_data()

    def load_data(self):
        self.menu_buttons = [
            element for element in self.shared_elements if isinstance(element, Button)
        ]
        self.arrows = [
            element for element in self.shared_elements if isinstance(element, MenuArrow)
        ]
