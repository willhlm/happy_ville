from gameplay.ui.components import MenuArrow, Slider, Text

from ..base_loader import BaseLoader


class OptionSoundsLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = "assets/ui_layouts/menus/option_sounds/option_sounds.json"
        self.load_UI_data(path, "option_sounds")
        self.load_data()

    def load_data(self):
        self.arrows = []
        self.buttons = []
        self.results = []
        self.slider = []
        for obj in self.map_data["elements"]:
            object_size = [int(obj["width"]), int(obj["height"])]
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

            if id == 1:
                self.arrows.append(MenuArrow(topleft_object_position, self.game_objects, flip=True))
            elif id == 4:
                self.arrows.append(MenuArrow(topleft_object_position, self.game_objects))
            elif id == 5:
                button = None
                for property in properties:
                    if property["name"] == "text":
                        button = property["value"]
                self.buttons.append(Text(self.game_objects, text=button, position=topleft_object_position, size=object_size))
            elif id == 6:
                self.results.append(topleft_object_position)
            elif id == 8:
                self.slider.append(Slider(self.game_objects, position=topleft_object_position))
