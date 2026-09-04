from gameplay.ui.components import MenuArrow, ResultStamp, Slider, Text

from ..base_loader import BaseLoader


class OptionSoundsLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = "assets/ui_layouts/menus/option_sounds/option_sounds.json"
        self.load_UI_data(path, "option_sounds")
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
        self.slider = []
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            page_local_id = self.get_object_local_id(obj, "option_sounds_UI")
            if page_local_id == 8:
                self.slider.append(Slider(self.game_objects, position=topleft_object_position))
