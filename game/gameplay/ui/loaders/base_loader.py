from engine.utils import read_files
from os.path import basename, splitext
from gameplay.ui.components import Controllers, InventoryContainer, Text

class BaseLoader():
    # Tiled convention for UI loaders:
    # - Use an object layer named "shared" for UI objects reused across screens.
    # - Place those shared objects in assets/ui_layouts/shared.tsx.
    # - Use an object layer named "objects" for screen-specific objects.
    # - Keep screen-specific tiles in that screen's own ..._UI.tsx tileset.
    DEFAULT_SHARED_LAYER = "shared"
    DEFAULT_SHARED_TILESET = "shared"
    SHARED_OBJECT_LAYER = DEFAULT_SHARED_LAYER
    SHARED_TILESET = DEFAULT_SHARED_TILESET

    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.base_resolution = game_objects.game.window_size.copy()
        self.buttons = {}
        self.shared_objects = []
        self.containers = []
        self.texts = []

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
        self.load_shared_objects()

    def load_data(self):
        pass

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

    def load_shared_objects(self, objects=None):
        if objects is None:
            objects = self.map_data.get(self.SHARED_OBJECT_LAYER, [])

        for obj in objects:
            local_id = self.get_object_local_id(obj, self.SHARED_TILESET)
            if local_id is None: continue
                

            topleft = self.get_object_topleft(obj)
            properties = self.get_object_properties(obj)
            object_size = [int(obj["width"]), int(obj["height"])]

            if local_id == 0:#a button
                button = Controllers(topleft, self.game_objects, 'a', self.game_objects.controller.controller_type[-1])
                #self.shared_objects.append(button)
                self.buttons['a'] = button

            elif local_id == 1:#b button
                button = Controllers(topleft, self.game_objects, 'b', self.game_objects.controller.controller_type[-1])
                #self.shared_objects.append(button)
                self.buttons['b'] = button

            elif local_id == 3:#y button
                button = Controllers(topleft, self.game_objects, 'y', self.game_objects.controller.controller_type[-1])
                #self.shared_objects.append(button)
                self.buttons['y'] = button 

            elif local_id == 4:#x button
                button = Controllers(topleft, self.game_objects, 'x', self.game_objects.controller.controller_type[-1])
                #self.shared_objects.append(button)
                self.buttons['x'] = button                                 

            elif local_id == 5:#lb button
                button = Controllers(topleft, self.game_objects, 'lb', self.game_objects.controller.controller_type[-1])
                #self.shared_objects.append(button)
                self.buttons['lb'] = button 

            elif local_id == 6:#rb button
                button = Controllers(topleft, self.game_objects, 'rb', self.game_objects.controller.controller_type[-1])
                #self.shared_objects.append(button)
                self.buttons['rb'] = button                    

            elif local_id == 7:#             
                self.texts.append(Text(self.game_objects, text=properties['text'], position=topleft, size=object_size))

            elif local_id == 8:                
                item = properties.get("item", str(obj["id"]))
                self.containers.append(InventoryContainer(topleft, self.game_objects, item))                

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
