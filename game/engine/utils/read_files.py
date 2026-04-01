from dataclasses import dataclass, field

import pygame, json
from os import listdir, walk, makedirs
from os.path import isfile, join, basename, isdir, dirname

@dataclass
class SpriteSet:
    textures: object
    normal_maps: object = field(default_factory=dict)

    def __getitem__(self, key):
        return self.textures[key]

    def __setitem__(self, key, value):
        self.textures[key] = value

    def __len__(self):
        return len(self.textures)

    def __iter__(self):
        return iter(self.textures)

    def __contains__(self, item):
        return item in self.textures

    def get(self, key, default = None):
        return self.textures.get(key, default)

    def keys(self):
        return self.textures.keys()

    def values(self):
        return self.textures.values()

    def items(self):
        return self.textures.items()

def default(dict):
    if hasattr(dict, 'to_json'):
        return dict.to_json()

def save_json(dict, name):#used to save game
    jsonStr=json.dumps(dict, default=default)
    path="save/" + name + ".json"
    with open(path, "w") as outfile:
        outfile.write(jsonStr)

def load_json(name):#used to load game
    path='save/' + name + '.json'
    return read_json(path)

def read_json(path):
    with open(path) as f:
        text = json.load(f)
    return text

def write_json(dict, name):
    jsonStr=json.dumps(dict, default=default)
    with open(name, "w") as outfile:
        outfile.write(jsonStr)

def get_folder(file_path):#used when reading sprites for map loader
    for n in range(len(file_path)):
        if file_path[-(n+1)] == '/':
            return file_path[:-n]

def format_tiled_json_group(map_data):#if we want static stamps with parallax -> called from maploader
    formatted_map_data = {}
    formatted_map_data['groups'] = {}
    formatted_map_data['tilesets'] = map_data['tilesets']

    for gruop in map_data['layers']:#it will take from lowest position in tiled
        formatted_map_data['groups'][gruop['name']] = {}
        formatted_map_data['groups'][gruop['name']]['layers'] = {}
        formatted_map_data['groups'][gruop['name']]['objects'] = {}
        formatted_map_data['groups'][gruop['name']]['parallaxx'] = gruop.get('parallaxx',1)#get value, if not present, pass 1
        formatted_map_data['groups'][gruop['name']]['parallaxy'] = gruop.get('parallaxy',1)#get value, if not present, pass 1
        formatted_map_data['groups'][gruop['name']]['offsetx'] = gruop.get('offsetx',0)#get value, if not present, pass 0
        formatted_map_data['groups'][gruop['name']]['offsety'] = gruop.get('offsety',0)#get value, if not present, pass 0
        for layer in gruop['layers']:#inside group stuff
            if 'objects' in layer.keys():#objects in group
                layer['offsetx'] = layer.get('offsetx',0)
                layer['offsety'] = layer.get('offsety',0)
                formatted_map_data['groups'][gruop['name']]['objects'][layer['name']] = layer
            else:#tile layer in gorup
                layer['offsetx'] = layer.get('offsetx',0)
                layer['offsety'] = layer.get('offsety',0)
                formatted_map_data['groups'][gruop['name']]['layers'][layer['name']] = layer
    return formatted_map_data

def format_tiled_json(map_data):#used from UI loader
    formatted_map_data = {}
    formatted_map_data['tile_layers'] = {}
    formatted_map_data['tilesets'] = map_data['tilesets']

    for layer in map_data['layers']:
        if 'data' in layer.keys():#tile layers
            formatted_map_data['tile_layers'][layer['name']] = layer
        elif 'objects' in layer.keys():#object: static stamps, collision
            formatted_map_data[layer['name']] = layer['objects']

    return formatted_map_data

'shader loader'
def load_shaders_dict(game_objects):#returns a dicy with "state" as key and shader program as value
    shader_dict = {}
    base_path = 'engine/render/shaders/'
    for subdir in [d[0] for d in walk(base_path) if d[0] != base_path]:
        if '_old' in subdir: continue  # skip _old folder        
        subdirs_in_current = [d for d in listdir(subdir) if isdir(join(subdir, d))]# Only process leaf directories (folders with no subdirectories)
        if len(subdirs_in_current) > 0:continue  # Skip folders that contain other folders: to support subfold structure                  
        shader_dict[basename(subdir)] = load_shader_list(subdir, game_objects)        
    return shader_dict

def load_shader_list(path_to_folder, game_objects):#use this to load multiple sprites in a path_to_folder           
    vertex_path = None
    fragment_path = None

    for f in listdir(path_to_folder):
        if not isfile(join(path_to_folder, f)): continue#skip the folders
        if '.DS_Store' in f or '.gitkeep' in f: continue#skip this file

        shader_path = join(path_to_folder, f)
        file_name = f.lower()
        if 'vertex' in file_name:
            vertex_path = shader_path
        elif 'fragment' in file_name:
            fragment_path = shader_path

    if fragment_path is None:
        raise FileNotFoundError(f"No fragment shader found in '{path_to_folder}'")

    return game_objects.game.display.load_shader_from_path(vertex_path, fragment_path)

'sound loader'
def load_sounds_dict(base_path):#returns a dict with "stae" as key, the sound file as value
    sound_dict = {}
    for subdir in [d[0] for d in walk(base_path)]:
        if subdir == base_path:
            pass        
        sound_dict[subdir.split("/")[-1]] = load_sounds_list(subdir)
    return sound_dict

def load_sounds_list(path_to_folder):
    #use this to load multiple sprites in a path_to_folder
    list_of_sounds = []
    for f in listdir(path_to_folder):
        if not isfile(join(path_to_folder, f)): continue#skip the folders
        if '.DS_Store' in join(path_to_folder, f): continue#skip this file
        if '.gitkeep' in join(path_to_folder, f): continue#skip this file
        list_of_sounds.append(load_single_sfx(join(path_to_folder, f)))
    return list_of_sounds

def load_single_sfx(path):
    return pygame.mixer.Sound(path)

'sprite loader'
def load_sprites_dict(base_path, game_objects, flip_x = False, normal_map = False):#returns a dict with "state" as key and list of sprites as value
    sprite_dict = {}
    normal_dict = {}

    if normal_map:
        for subdir in [d[0] for d in walk(base_path)]:
            if subdir == base_path:
                pass
            state = subdir.split("/")[-1]
            sprite_set = load_sprites_list(subdir, game_objects, flip_x, normal_map)
            sprite_dict[state] = sprite_set.textures
            normal_dict[state] = sprite_set.normal_maps
        return SpriteSet(sprite_dict, normal_dict)

    for subdir in [d[0] for d in walk(base_path)]:
        if subdir == base_path:
            pass
        sprite_dict[subdir.split("/")[-1]] = load_sprites_list(subdir, game_objects, flip_x, normal_map).textures
    return SpriteSet(sprite_dict)

def load_sprites_list(path_to_folder, game_objects, flip_x = False, normal_map = False):#returns a list of sprites
    list_of_sprites = _list_sprite_files(path_to_folder)
    if normal_map:
        sprites = []
        normal_maps = []
        for file in list_of_sprites:
            sprite_surface = load_sprite(file, flip_x)
            sprites.append(game_objects.game.display.surface_to_texture(sprite_surface))
            normal_maps.append(_load_or_generate_normal_texture(file, game_objects, sprite_surface))
        return SpriteSet(sprites, normal_maps)
    return SpriteSet([game_objects.game.display.surface_to_texture(load_sprite(file, flip_x)) for file in list_of_sprites])

'normal map'
def load_generated_normal_sprites_dict(texture_base_path, game_objects, flip_x = False):
    return load_sprites_dict(texture_base_path, game_objects, flip_x, normal_map = True).normal_maps

def load_generated_normal_sprites_list(texture_folder, game_objects, flip_x = False):
    return load_sprites_list(texture_folder, game_objects, flip_x, normal_map = True).normal_maps

def _list_sprite_files(path_to_folder):
    if not isdir(path_to_folder):
        return []

    list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
    ignored_files = {join(path_to_folder, '.DS_Store'), join(path_to_folder, '.gitkeep')}
    list_of_sprites = [path for path in list_of_sprites if path not in ignored_files]
    list_of_sprites.sort()
    return list_of_sprites

def _load_or_generate_normal_texture(texture_path, game_objects, sprite_surface = None):
    normal_path = _normal_map_path(texture_path)

    if isfile(normal_path):
        return game_objects.game.display.surface_to_texture(load_sprite(normal_path))

    if sprite_surface is None:
        sprite_surface = load_sprite(texture_path)

    generated_surface = game_objects.normal_map_generator.generate_surface(sprite_surface)
    _save_generated_normal_map(generated_surface, normal_path)
    return game_objects.game.display.surface_to_texture(generated_surface)

def _normal_map_path(texture_path):
    if texture_path.startswith('assets/sprites/'):
        return texture_path.replace('assets/sprites/', 'assets/normal_maps/', 1)
    return join('assets/normal_maps', texture_path)

def _save_generated_normal_map(surface, output_path):
    makedirs(dirname(output_path), exist_ok = True)
    pygame.image.save(surface, output_path)

'simple load'
def load_sprite(path_to_sprite, flip_x = False):#use to load single sprite, full path must be provided
    temp = pygame.image.load(path_to_sprite).convert_alpha()
    if flip_x:
        temp = pygame.transform.flip(temp, True, False)#flip(surface, flip_x, flip_y)
    return temp

def generic_sheet_reader(path_to_sheet, w, h, r, c):
#width, height, no o sprites in row, no o sprites in column
#loads all sprites from a sheet,
#this method requires all sprites to have the same dimension in the sheet
    sprite_dict = {}
    sheet = load_sprite(path_to_sheet)
    sprite_size = (w,h) #[width, height] of sprite in sheet
    sprite_count = [r,c] # nomber of sprites per [row,column]
    n = 0

    for i in range(sprite_count[0]):
        for j in range(sprite_count[1]):
            rect = pygame.Rect(j*sprite_size[0], i*sprite_size[1], j*sprite_size[0] + sprite_size[0], i*sprite_size[1] + sprite_size[1])
            image = pygame.Surface(sprite_size,pygame.SRCALPHA,32).convert_alpha()
            image.blit(sheet,(0,0),rect)
            sprite_dict[n] = image
            n+=1
    return sprite_dict

def alphabet_reader(path_to_sheet, h, num):
    """
    Reads sprites from a sheet, where red dots seperate the sprites in the sheet. Currently only made to read from sprites in a single line.
    takes, path, height of sprite and number of sprites as input.
    """
    sprite_dict = {}
    sheet = load_sprite(path_to_sheet)

    pxarray = pygame.PixelArray(sheet)
    row_t = list(pxarray.extract(pygame.Color(255, 0 ,0))[:,0])
    row_h1 = list(pxarray.extract(pygame.Color(0, 255 ,0))[:,-2])
    row_h2 = list(pxarray.extract(pygame.Color(0, 255 ,0))[:,-1])
    pxarray.close()

    mask = [-1, 4294967295]

    indecies = [i for i in range(len(row_t)) if row_t[i] in mask]
    indecies_h1 = [i for i in range(len(row_h1)) if row_h1[i] in mask]
    indecies_h2 = [i for i in range(len(row_h2)) if row_h2[i] in mask]

    for i, val in enumerate(indecies):
        try:
            val2 = indecies[i+1]
        except IndexError:
            continue
        if val in indecies_h1:
            height = 8
        elif val in indecies_h2:
            height = 9
        else:
            height = h
        width = val2 - val - 1
        rect = pygame.Rect(val+1, 0, width, height)
        #rect = pygame.Rect(j*sprite_size[0], i*sprite_size[1], j*sprite_size[0] + sprite_size[0], i*sprite_size[1] + sprite_size[1])
        image = pygame.Surface((width, height),pygame.SRCALPHA,32).convert_alpha()
        image.blit(sheet,(0,0),rect)
        sprite_dict[i] = image
    return sprite_dict
