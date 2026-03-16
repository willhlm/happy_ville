from gameplay.ui.components import Button, MenuArrow

from ..base_loader import BaseLoader


class PauseMenuLoader(BaseLoader):
    def __init__(self, game_objects):
        super().__init__(game_objects)
        path = "assets/ui_layouts/menus/pause_menu/pause_menu.json"
        self.load_UI_data(path, "pause_menu")
        self.load_data()

    def load_data(self):
        self.buttons = []
        self.arrows = []
        for obj in self.map_data["elements"]:
            topleft_object_position = [int(obj["x"]), int(obj["y"]) - int(obj["height"])]
            properties = obj.get("properties", [])
            id = obj["gid"] - self.map_data["UI_firstgid"]

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
