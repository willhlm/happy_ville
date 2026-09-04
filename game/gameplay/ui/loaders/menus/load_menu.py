from gameplay.ui.components import Button, MenuArrow

from ..base_loader import BaseLoader


class LoadMenuLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = "assets/ui_layouts/menus/load_menu/load_menu.json"
        self.load_UI_data(path, "load_menu")
        self.load_data()

    def load_data(self):
        self.menu_buttons = [
            element for element in self.shared_elements if isinstance(element, Button)
        ]
        self.arrows = [
            element for element in self.shared_elements if isinstance(element, MenuArrow)
        ]
