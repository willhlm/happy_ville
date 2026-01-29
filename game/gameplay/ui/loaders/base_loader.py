from engine.utils import read_files

class BaseLoader():#for map, omamori, ability, journal etc: json file should have same name as class and folder, tsx file should end with _UI
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.base_resolution = game_objects.game.window_size.copy()

    def load_UI_data(self, path, name):
        map_data = read_files.read_json(path)
        self.map_data = read_files.format_tiled_json(map_data)
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if name + '_UI' in tileset['source']:#the name of the tmx file
                    self.map_data['UI_firstgid'] =  tileset['firstgid']

    def load_data(self):
        pass

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