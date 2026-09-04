from engine.utils import read_files
from os.path import basename, splitext
from gameplay.ui.components import (
    Button,
    Controllers,
    InventoryContainer,
    MenuArrow,
    ResultStamp,
    Text,
)

class BaseLoader():
    # Tiled convention for UI loaders:
    # - assets/ui_layouts/shared.tsx defines reusable UI component types.
    # - Use an object layer named "shared" to place instances of those types for
    #   this screen. The layer is part of the screen layout; it is not a global
    #   layout shared by every screen.
    # - Use an object layer named "objects" for screen-specific objects.
    # - Keep screen-specific tiles in that screen's own ..._UI.tsx tileset.
    DEFAULT_SHARED_LAYER = "shared"
    DEFAULT_SHARED_TILESET = "shared"
    SHARED_OBJECT_LAYER = DEFAULT_SHARED_LAYER
    SHARED_TILESET = DEFAULT_SHARED_TILESET

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.base_resolution = game_objects.game.window_size.copy()
        self.images = []
        self.controller_prompts = {}
        self.text_fields = {}
        self.shared_elements = []
        self.page_elements = []

    def load_UI_data(self, path, name):
        map_data = read_files.read_json(path)
        self.raw_map_data = map_data
        self.map_data = read_files.format_tiled_json(map_data)
        self.map_data['tileset_firstgids'] = {}
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                source_name = splitext(basename(tileset['source']))[0]
                self.map_data['tileset_firstgids'][source_name] = tileset['firstgid']
                if name + '_UI' in tileset['source']:#the name of the tmx file
                    self.map_data['UI_firstgid'] =  tileset['firstgid']
        self.load_shared_elements()

    def load_data(self):
        pass

    def register_text_field(self, text_obj, text_key=None):
        if text_key is None:
            return
        self.text_fields.setdefault(text_key, []).append(text_obj)

    def assign_text_field(self, text_key, text):
        fields = self.text_fields.get(text_key, [])
        if not fields:
            return False
        for field in fields:
            field.text = text
        return True

    def properties_to_dict(self, properties):
        return {prop["name"]: prop["value"] for prop in properties}

    def get_object_properties(self, obj):
        return self.properties_to_dict(obj.get("properties", []))

    def get_tileset_firstgid(self, tileset_name, default=None):
        return self.map_data.get("tileset_firstgids", {}).get(tileset_name, default)

    def get_object_topleft(self, obj):
        return [int(obj["x"]), int(obj["y"]) - int(obj["height"])]

    def get_object_local_id(self, obj, tileset_name):
        firstgid = self.get_tileset_firstgid(tileset_name)
        if firstgid is None:
            return None

        object_gid = obj.get("gid")
        if object_gid is None:
            return None

        return object_gid - firstgid

    def load_shared_elements(self, objects=None):
        """Load this layout's instances of components from ``shared.tsx``.

        Components are kept in layout order in ``shared_elements``. Semantic
        indexes, such as ``controller_prompts`` and ``text_fields``, are kept
        only where callers need lookup rather than rendering.
        """
        if objects is None:
            objects = self.map_data.get(self.SHARED_OBJECT_LAYER, [])

        for obj in objects:
            local_id = self.get_object_local_id(obj, self.SHARED_TILESET)
            if local_id is None: continue
                

            topleft = self.get_object_topleft(obj)
            properties = self.get_object_properties(obj)
            object_size = [int(obj["width"]), int(obj["height"])]

            if local_id == 0:#a button
                button = Controllers(topleft, self.game_objects, 'a')
                self.controller_prompts['a'] = button
                self.shared_elements.append(button)

            elif local_id == 1:#b button
                button = Controllers(topleft, self.game_objects, 'b')
                self.controller_prompts['b'] = button
                self.shared_elements.append(button)

            elif local_id == 3:#y button
                button = Controllers(topleft, self.game_objects, 'y')
                self.controller_prompts['y'] = button
                self.shared_elements.append(button)

            elif local_id == 4:#x button
                button = Controllers(topleft, self.game_objects, 'x')
                self.controller_prompts['x'] = button
                self.shared_elements.append(button)

            elif local_id == 5:#rb button
                button = Controllers(topleft, self.game_objects, 'rb')
                self.controller_prompts['rb'] = button
                self.shared_elements.append(button)

            elif local_id == 6:#lb button
                button = Controllers(topleft, self.game_objects, 'lb')
                self.controller_prompts['lb'] = button
                self.shared_elements.append(button)

            elif local_id == 12:#rt
                button = Controllers(topleft, self.game_objects, 'rt')
                self.controller_prompts['rt'] = button
                self.shared_elements.append(button)

            elif local_id == 13:#lt
                button = Controllers(topleft, self.game_objects, 'lt')
                self.controller_prompts['lt'] = button
                self.shared_elements.append(button)

            elif local_id == 14:#start
                button = Controllers(topleft, self.game_objects, 'start')
                self.controller_prompts['start'] = button
                self.shared_elements.append(button)

            elif local_id == 15:#select
                button = Controllers(topleft, self.game_objects, 'select')
                self.controller_prompts['select'] = button
                self.shared_elements.append(button)

            elif local_id == 16:#ls
                button = Controllers(topleft, self.game_objects, 'ls')
                self.controller_prompts['ls'] = button
                self.shared_elements.append(button)

            elif local_id == 17:#rs
                button = Controllers(topleft, self.game_objects, 'rs')
                self.controller_prompts['rs'] = button
                self.shared_elements.append(button)

            elif local_id == 7:#             
                font_style = properties.get("font_style", "text")
                text_key = properties.get("text_key")
                text_obj = Text(
                    self.game_objects,
                    text=properties.get('text', ''),
                    position=topleft,
                    size=object_size,
                    font_style=font_style,
                )
                self.shared_elements.append(text_obj)
                self.register_text_field(text_obj, text_key=text_key)

            elif local_id == 8:           
                item = properties.get("item", str(obj["id"]))                
                container = InventoryContainer(topleft, self.game_objects, item)
                self.shared_elements.append(container)

            elif local_id == 9:
                text = properties.get("name", str(obj["id"]))
                self.shared_elements.append(Button(self.game_objects, text=text, position=topleft, center=True))

            elif local_id == 10:
                self.shared_elements.append(MenuArrow(topleft, self.game_objects, flip=True))

            elif local_id == 11:
                self.shared_elements.append(MenuArrow(topleft, self.game_objects))

            elif local_id == 18:
                self.shared_elements.append(ResultStamp(topleft, object_size))

    def _scale_position(self, pos):
        """Scale a position from base resolution to current resolution"""
        current_res = self.game_objects.game.window_size
        scale_x = current_res[0] / self.base_resolution[0]
        scale_y = current_res[1] / self.base_resolution[1]
        return (int(pos[0] * scale_x), int(pos[1] * scale_y))
    
    def _scale_size(self, size):
        """Scale a size from base resolution to current resolution"""
        current_res = self.game_objects.game.window_size
        scale_x = current_res[0] / self.base_resolution[0]
        scale_y = current_res[1] / self.base_resolution[1]
        return (int(size[0] * scale_x), int(size[1] * scale_y))   
