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

#class for reading and rendering fonts
class Alphabet2():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.char_size = (5,7)
        self.max_height = 9
        self.character_order = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                                'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                                '1','2','3','4','5','6','7','8','9','0','!','?','_','.',',',"'",'(',')','[',']']
        self.text_bg_dict = {'default':generic_sheet_reader("Sprites/utils/text_bg5.png",16,16,3,3), 'text_bubble':generic_sheet_reader("Sprites/utils/text_bg6.png",16,16,3,3)}
        sheet = alphabet_reader("Sprites/utils/alpha_new.png", self.char_size[1], len(self.character_order))

        self.characters={}
        #map sprites to charactersin dict
        for i, c in enumerate(self.character_order):
            self.characters[c] = sheet[i]

    #returns a surface with size of input, and input text. Automatic line change
    def render(self, surface_size = False, text="", letter_frame = 1000, alignment='left'):
        if not surface_size:
            total_width = sum(self.characters[c].get_width() + 1 for c in text if c in self.characters)
            total_width += text.count(" ") * 4  # Adjusting for spaces
            surface_size = (total_width, self.max_height + 2)

        text_surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()
        #pygame.draw.rect(text_surface, [200, 200, 200, 100], (0, 0, surface_size[0], surface_size[1]))

        h = self.max_height
        s = 3  # Space between words
        visible_text = text[:letter_frame]
        words = visible_text.split(" ")

        lines = []
        current_line = []
        line_width = 0
        max_width = surface_size[0]
        x, y = 0, 0

        for word in words:
            word_width = 0
            for c in word:
                if c in self.characters:
                    word_width += self.characters[c].get_width() + 1
            #word_width = sum(self.characters[c].get_width() + 1 for c in word if c in self.characters)

            if line_width + word_width > max_width:
                lines.append((current_line, line_width - 1))
                current_line = []
                line_width = 0
                y += h
                if y > surface_size[1] - h:
                    break

            current_line.append(word)
            line_width += word_width + s

        if current_line:
            lines.append((current_line, line_width - s))

        y = 0
        for line, line_width in lines:
            if alignment == 'center':
                x = (surface_size[0] - line_width) // 2
            else:
                x = 0

            for word in line:
                for c in word:
                    if c in self.characters:
                        text_surface.blit(self.characters[c], (x, y))
                        x += self.characters[c].get_width() + 1
                x += s
            y += h

        return self.game_objects.game.display.surface_to_texture(text_surface)

    #returns a surface with menu/text background as per size input.
    #dimensions should be divisble with 16 (unless base png is changed)
    def fill_text_bg(self, surface_size, type = 'default'):
        col = int(surface_size[0]/16)
        row = int(surface_size[1]/16)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()

        for r in range(0,row):
            for c in range(0,col):
                if r==0:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][0],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][2],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][1],(c*16,r*16))
                elif r==row-1:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][6],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][8],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][7],(c*16,r*16))
                else:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][3],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][5],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][4],(c*16,r*16))
        return self.game_objects.game.display.surface_to_texture(surface)

class Alphabet():
    def __init__(self, game_objects, font_name = None, font_size = 12):
        self.game_objects = game_objects
        pygame.font.init()
        self.font = pygame.font.Font('Sprites/utils/fonts/8BitSnobbery' + '.ttf', font_size)
        self.text_bg_dict = {'default':generic_sheet_reader("Sprites/utils/text_bg5.png",16,16,3,3), 'text_bubble':generic_sheet_reader("Sprites/utils/text_bg6.png",16,16,3,3)}

    def get_height(self):
        return self.font.get_height()

    def render(self, surface_size=False, text='', letter_frame=1000, color=(255, 255, 255), alignment='left'):
        # Limit text to `letter_frame`
        visible_text = text[:letter_frame]

        # **If text is empty or only spaces, return an empty transparent texture**
        if not visible_text.strip():
            empty_surface = pygame.Surface(surface_size if surface_size else (1, 1), pygame.SRCALPHA, 32).convert_alpha()
            empty_surface.fill((0, 0, 0, 0))  # Transparent
            return self.game_objects.game.display.surface_to_texture(empty_surface)

        # Initialize
        words = visible_text.split(" ")
        max_width = surface_size[0] if surface_size else self.font.size(visible_text)[0]
        line_height = self.font.get_height()
        lines, line_widths = [], []
        current_line = ""
        x, y = 0, 0

        # Word wrapping based on visible text
        for word in words:
            test_line = (current_line + " " + word).strip()

            # If new word exceeds width, wrap it
            if self.font.size(test_line)[0] > max_width and current_line:
                lines.append(current_line)
                line_widths.append(self.font.size(current_line)[0])
                current_line = word  # Start new line
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)
            line_widths.append(self.font.size(current_line)[0])

        # **Ensure surface is large enough**
        total_height = len(lines) * line_height
        surface_size = (max_width, total_height) if not surface_size else surface_size

        # Create transparent surface
        text_surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()
        text_surface.fill((0, 0, 0, 0))  # Transparent background

        # Render each line correctly
        for i, line in enumerate(lines):
            rendered_text = self.font.render(line, False, color)
            if alignment == 'center':
                x = (surface_size[0] - line_widths[i]) // 2  # Centering
            else:
                x = 0  # Left alignment

            text_surface.blit(rendered_text, (x, y))
            y += line_height  # Move to next line

        return self.game_objects.game.display.surface_to_texture(text_surface)

    def fill_text_bg(self, surface_size, type = 'default'):
        col = int(surface_size[0]/16)
        row = int(surface_size[1]/16)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()

        for r in range(0,row):
            for c in range(0,col):
                if r==0:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][0],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][2],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][1],(c*16,r*16))
                elif r==row-1:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][6],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][8],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][7],(c*16,r*16))
                else:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][3],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][5],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][4],(c*16,r*16))

        return self.game_objects.game.display.surface_to_texture(surface)
