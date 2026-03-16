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
        self.buttons = []
        self.arrows = []
        for obj in self.map_data["elements"]:
            object_size = [int(obj["width"]), int(obj["height"])]
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

            topleft_object_position = self._scale_position(topleft_object_position)
            object_size = self._scale_size(object_size)

            if id == 0:
                button = None
                for property in properties:
                    if property["name"] == "name":
                        button = property["value"]
                self.buttons.append(Button(self.game_objects, text=button, position=topleft_object_position, center=True))
            elif id == 1:
                self.arrows.append(MenuArrow(topleft_object_position, self.game_objects, flip=True))
            elif id == 4:
                self.arrows.append(MenuArrow(topleft_object_position, self.game_objects))
