import pygame, json
from os import listdir, walk
from os.path import isfile, join

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

def write_json():
    pass

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
def load_shaders_dict(shaders, game_objects):#returns a dicy with "state" as key and shader program as value
    all_shaders = ['idle','hurt','invincible','blur']#all shaders need to be listed here
    shader_dict = {}
    for shader in all_shaders:
        base_path = 'shaders/' + shader
        list_of_shader = [base_path +'/'+ f for f in listdir(base_path)]
        list_of_shader.sort(reverse=True)
        shader_dict[shader] = game_objects.game.display.load_shader_from_path(list_of_shader[0],list_of_shader[1])#vertex first
    return shader_dict

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
    for f in listdir(path_to_folder):
        if not isfile(join(path_to_folder, f)): continue#skip the folders
        if '.DS_Store' in join(path_to_folder, f): continue#skip this file
        if '.gitkeep' in join(path_to_folder, f): continue#skip this file
        return load_single_sfx(join(path_to_folder, f))

def load_single_sfx(path):
    return pygame.mixer.Sound(path)

'sprite loader'
def load_sprites_dict(base_path, game_objects):#returns a dict with "state" as key and list of sprites as value
    sprite_dict = {}
    for subdir in [d[0] for d in walk(base_path)]:
        if subdir == base_path:
            pass
        sprite_dict[subdir.split("/")[-1]] = load_sprites_list(subdir, game_objects)
    return sprite_dict

def load_sprites_list(path_to_folder, game_objects):#returns a list of sprites
    list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
    if join(path_to_folder,'.DS_Store') in list_of_sprites:
        list_of_sprites.remove(join(path_to_folder,'.DS_Store'))
    if join(path_to_folder,'.gitkeep') in list_of_sprites:#sp that we can push empty folders
        list_of_sprites.remove(join(path_to_folder,'.gitkeep'))
    list_of_sprites.sort()
    return [game_objects.game.display.surface_to_texture(load_sprite(file)) for file in list_of_sprites]

def load_sprite(path_to_sprite):#use to load single sprite, full path must be provided
    return pygame.image.load(path_to_sprite).convert_alpha()

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

#class for reading and rendering fonts
class Alphabet():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.char_size = (4,6)
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9',',','.','\'','!','?','_']
        self.character_lower = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        self.text_bg_dict = generic_sheet_reader("Sprites/utils/text_bg4.png",16,16,3,3)
        sheet = generic_sheet_reader("Sprites/utils/alphabet_low.png",self.char_size[0],self.char_size[1],1,len(self.character_order))

        self.characters={}
        #map sprites to charactersin dict
        for i, c in enumerate(self.character_order):
            self.characters[c] = sheet[i]

        #map lower case to same sprites (change __init__ incase lower case sprites are desired)
        for i, c in enumerate(self.character_lower):
            self.characters[c] = sheet[i]

    #returns a surface with size of input, and input text. Automatic line change
    def render(self, surface_size = False, text = "", limit = 1000, inverse_color = False):
        if not surface_size:
            surface_size = (4*(len(text)+1),5)
        text_surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()
        x, y = 0, 0
        x_max = int(surface_size[0]/self.char_size[0])
        y_max = int(surface_size[1]/self.char_size[1])
        text_l = text.split(" ")
        for word in text_l:
            #check if we need to switch line
            if len(word) + x > x_max:
                x = 0
                y += 1

            for c in word:
                pos = (x*self.char_size[0],y*self.char_size[1])
                if not inverse_color:
                    text_surface.blit(self.characters[c],pos)
                else:
                    text_surface.blit(self.characters[c],pos)
                x += 1
                if x_max * y + x > limit: return self.game_objects.game.display.surface_to_texture(text_surface) #spot printing at limit

            x += 1      #add space after each word

        if inverse_color:
            color_surface = pygame.Surface(text_surface.get_size()).convert_alpha()
            color_surface.fill((255,255,255))
            text_surface.blit(color_surface, (0,0), special_flags = pygame.BLEND_RGB_MAX)

        return self.game_objects.game.display.surface_to_texture(text_surface)

    #returns a surface with menu/text background as per size input.
    #dimensions should be divisble with 16 (unless base png is changed)
    def fill_text_bg(self, surface_size):
        col = int(surface_size[0]/16)
        row = int(surface_size[1]/16)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()

        for r in range(0,row):
            for c in range(0,col):
                if r==0:
                    if c==0:
                        surface.blit(self.text_bg_dict[0],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[2],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[1],(c*16,r*16))
                elif r==row-1:
                    if c==0:
                        surface.blit(self.text_bg_dict[6],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[8],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[7],(c*16,r*16))
                else:
                    if c==0:
                        surface.blit(self.text_bg_dict[3],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[5],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[4],(c*16,r*16))
        return self.game_objects.game.display.surface_to_texture(surface)
