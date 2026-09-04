from gameplay.ui.components import MenuArrow, ResultStamp, Text

from ..base_loader import BaseLoader


class ControllerMenuLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = "assets/ui_layouts/menus/option_controller/option_controller.json"
        self.load_UI_data(path, "option_controller")
        self.load_data()

    def load_data(self):
        self.option_labels = [
            element for element in self.shared_elements if isinstance(element, Text)
        ]
        self.arrows = [
            element for element in self.shared_elements if isinstance(element, MenuArrow)
        ]
        self.results = [
            stamp.rect.topleft
            for stamp in self.shared_elements
            if isinstance(stamp, ResultStamp)
        ]
