import pygame, json
from os import listdir, walk
from os.path import isfile, join
#from posixpath import join

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
    base_path = 'shaders/'
    for subdir in [d[0] for d in walk(base_path) if d[0] != base_path]:
        shader_dict[subdir.split("/")[-1]] = load_shader_list(subdir,game_objects)
    return shader_dict

def load_shader_list(path_to_folder, game_objects):#use this to load multiple sprites in a path_to_folder
    list_of_shader = []
    for f in listdir(path_to_folder):
        if not isfile(join(path_to_folder, f)): continue#skip the folders
        if '.DS_Store' in join(path_to_folder, f): continue#skip this file
        if '.gitkeep' in join(path_to_folder, f): continue#skip this file
        list_of_shader.append(join(path_to_folder, f))
    list_of_shader.sort(reverse = True)
    return game_objects.game.display.load_shader_from_path(list_of_shader[0],list_of_shader[1])#vertex first

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
def load_sprites_dict(base_path, game_objects, flip_x = False):#returns a dict with "state" as key and list of sprites as value
    sprite_dict = {}
    for subdir in [d[0] for d in walk(base_path)]:
        if subdir == base_path:
            pass
        sprite_dict[subdir.split("/")[-1]] = load_sprites_list(subdir, game_objects, flip_x)
    return sprite_dict

def load_sprites_list(path_to_folder, game_objects, flip_x = False):#returns a list of sprites
    list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
    if join(path_to_folder,'.DS_Store') in list_of_sprites:
        list_of_sprites.remove(join(path_to_folder,'.DS_Store'))
    if join(path_to_folder,'.gitkeep') in list_of_sprites:#sp that we can push empty folders
        list_of_sprites.remove(join(path_to_folder,'.gitkeep'))
    list_of_sprites.sort()
    return [game_objects.game.display.surface_to_texture(load_sprite(file, flip_x)) for file in list_of_sprites]

def load_sprite(path_to_sprite, flip_x = False):#use to load single sprite, full path must be provided
    temp = pygame.image.load(path_to_sprite).convert_alpha()
    temp = pygame.transform.flip(temp, flip_x, False)
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