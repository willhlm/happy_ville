from gameplay.ui.components import Button, MenuArrow, ResultStamp, Text

from ..base_loader import BaseLoader


class OptionControllerLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = "assets/ui_layouts/menus/option_controller/option_controller.json"
        self.load_UI_data(path, "option_controller")
        self.load_data()

    def load_data(self):
        self.option_labels = [
            element for element in self.shared_elements if isinstance(element, Text)
        ]
        self.option_labels.sort(key=lambda label: (label.rect.y, label.rect.x))
        self.menu_buttons = [
            element for element in self.shared_elements if isinstance(element, Button)
        ]
        self.menu_buttons.sort(key=lambda button: (button.rect.y, button.rect.x))
        self.navigation_items = sorted(
            [*self.option_labels, *self.menu_buttons],
            key=lambda item: (item.rect.y, item.rect.x),
        )
        self.arrows = [
            element for element in self.shared_elements if isinstance(element, MenuArrow)
        ]
        result_stamps = [
            stamp for stamp in self.shared_elements if isinstance(stamp, ResultStamp)
        ]
        result_stamps.sort(key=lambda stamp: (stamp.rect.y, stamp.rect.x))
        self.results = [stamp.rect.topleft for stamp in result_stamps]
