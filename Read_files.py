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

#if we want static stamps with parallax
def format_tiled_json_group(map_data):
    formatted_map_data = {}
    formatted_map_data['groups'] = {}
    formatted_map_data['tilesets'] = map_data['tilesets']

    for gruop in map_data['layers']:#it will take from lowest position in tiled
    #    if gruop['name'] == 'statics' or gruop['name'] =='collision':#object not in group: static stamps and collision layer
    #        formatted_map_data[gruop['name']] = gruop['objects']
    #        continue
        formatted_map_data['groups'][gruop['name']] = {}
        formatted_map_data['groups'][gruop['name']]['layers'] = {}
        formatted_map_data['groups'][gruop['name']]['objects'] = {}
        formatted_map_data['groups'][gruop['name']]['parallaxx'] = gruop.get('parallaxx',1)#get value, if not present, pass 1
        formatted_map_data['groups'][gruop['name']]['parallaxy'] = gruop.get('parallaxy',1)#get value, if not present, pass 1
        formatted_map_data['groups'][gruop['name']]['offsetx'] = gruop.get('offsetx',0)#get value, if not present, pass 0
        formatted_map_data['groups'][gruop['name']]['offsety'] = gruop.get('offsety',0)#get value, if not present, pass 0
        for layer in gruop['layers']:#inside group stuff
            if 'objects' in layer.keys():#objects in group
                formatted_map_data['groups'][gruop['name']]['objects'][layer['name']] = layer
            else:#tile layer in gorup
                formatted_map_data['groups'][gruop['name']]['layers'][layer['name']] = layer

    return formatted_map_data

def format_tiled_json(map_data):
    formatted_map_data = {}
    formatted_map_data['tile_layers'] = {}
    formatted_map_data['tilesets'] = map_data['tilesets']

    for layer in map_data['layers']:
        if 'data' in layer.keys():#tile layers
            formatted_map_data['tile_layers'][layer['name']] = layer
        elif 'objects' in layer.keys():#object: static stamps, collision
            formatted_map_data[layer['name']] = layer['objects']

    return formatted_map_data

def get_folder(file_path):
    for n in range(len(file_path)):
        if file_path[-(n+1)] == '/':
            return file_path[:-n]

def generic_sheet_reader(self, path_to_sheet, w, h, r, c):
#width, height, no o sprites in row, no o sprites in column
#loads all sprites from a sheet,
#this method requires all sprites to have the same dimension in the sheet
    sprite_dict = {}
    sheet = pygame.image.load(path_to_sheet).convert_alpha()
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

def load_sprites(path_to_folder):
    #use this to load multiple sprites in a path_to_folder
    list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
    if join(path_to_folder,'.DS_Store') in list_of_sprites:
        list_of_sprites.remove(join(path_to_folder,'.DS_Store'))
    if join(path_to_folder,'.gitkeep') in list_of_sprites:#sp that we can push empty folders
        list_of_sprites.remove(join(path_to_folder,'.gitkeep'))
    list_of_sprites.sort()
    return [pygame.image.load(file).convert_alpha() for file in list_of_sprites]

class Sounds():#read in SFX sounds, dorsn't have to be a class
    def __init__(self,path):
        super().__init__()
        self.SFX = self.load_all(path)

    @staticmethod
    def load_all(base_path):
        #loads all sprites in all sub directories in base_path, stores list of sprites with keys corresponding to folder name
        sprite_dict = {}
        for subdir in [d[0] for d in walk(base_path)]:
            if subdir == base_path:
                pass
            sprite_dict[subdir.split("/")[-1]] = Sounds.load_sounds(subdir)
        return sprite_dict

    @staticmethod
    def load_sounds(path_to_folder):
        #use this to load multiple sprites in a path_to_folder
        for f in listdir(path_to_folder):
            if not isfile(join(path_to_folder, f)): continue#skip the folders
            if '.DS_Store' in join(path_to_folder, f): continue#skip this file
            if '.gitkeep' in join(path_to_folder, f): continue#skip this file
            return pygame.mixer.Sound(join(path_to_folder, f))

#sprires and fonts
class Sprites():
    #use for animation sprites
    def __init__(self):
        # Add lists for each sprite animation here, in sub classes
        pass

    def load_all_sprites(self,base_path):
        #loads all sprites in all sub directories in base_path, stores list of sprites with keys corresponding to folder name
        sprite_dict = {}
        for subdir in [d[0] for d in walk(base_path)]:
            if subdir == base_path:
                pass
            sprite_dict[subdir.split("/")[-1]] = self.load_sprites(subdir)
        return sprite_dict

    def load_sprites(self,path_to_folder):
        #use this to load multiple sprites in a path_to_folder
        list_of_sprites = [join(path_to_folder, f) for f in listdir(path_to_folder) if isfile(join(path_to_folder, f))]
        if join(path_to_folder,'.DS_Store') in list_of_sprites:
            list_of_sprites.remove(join(path_to_folder,'.DS_Store'))
        if join(path_to_folder,'.gitkeep') in list_of_sprites:#sp that we can push empty folders
            list_of_sprites.remove(join(path_to_folder,'.gitkeep'))
        list_of_sprites.sort()
        return [self.load_sprite(file) for file in list_of_sprites]

    @staticmethod
    def load_sprite(path_to_sprite):
        #use to load single sprite, full path must be provided
        return pygame.image.load(path_to_sprite).convert_alpha()

    #TO DO: put this method outside of class!
    def generic_sheet_reader(self, path_to_sheet, w, h, r, c):
    #width, height, no o sprites in row, no o sprites in column
    #loads all sprites from a sheet,
    #this method requires all sprites to have the same dimension in the sheet
        sprite_dict = {}
        sheet = self.load_sprite(path_to_sheet)
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

#class containing sprites for players
class Sprites_Player(Sprites):
    def __init__(self,path):
        super().__init__()
        self.sprite_dict = self.load_all_sprites(path)

    def get_image(self, input, timer, dir):#input = state,timer=frame, dir
        if dir[0] > 0:
            return pygame.transform.flip(self.sprite_dict[input][timer],True,False)
        elif dir[0] <= 0:#else
            return self.sprite_dict[input][timer]

class Sprites_wallslime(Sprites_Player):
    def __init__(self,path):
        super().__init__(path)

    def get_image(self, input, timer, dir):#phase pre, main, post, input=action,timer=frame
        if dir[0] > 0:
            return self.sprite_dict[input][timer]
        elif dir[0] < 0:
            return pygame.transform.rotate(self.sprite_dict[input][timer],-180)
        elif dir[1] > 0:
            return pygame.transform.rotate(self.sprite_dict[input][timer],-270)
        elif dir[1] < 0:
            return pygame.transform.rotate(self.sprite_dict[input][timer],-90)

class Sprite_sheet():#don't need it?

    def __init__(self, filename):
        try:
            self.sheet =  pygame.image.load(filename).convert_alpha()
        except:
            #print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey = None):
        #Loads image from x, y, x+tilesize, y+tilesize.

        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert_alpha()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        #returns list of all images in sheet
        return [self.image_at(rect, colorkey) for rect in rects]

#class for reading and rendering fonts
class Alphabet():
    def __init__(self):

        self.char_size = (4,6)
        self.character_order=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9',',','.','\'','!','?','_']
        self.character_lower=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        self.text_bg_dict = Sprites().generic_sheet_reader("Sprites/utils/text_bg4.png",16,16,3,3)
        sheet=Sprites().generic_sheet_reader("Sprites/utils/alphabet_low.png",self.char_size[0],self.char_size[1],1,len(self.character_order))

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
            surface_size = (4*len(text),5)
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
                if x_max * y + x > limit: return text_surface #spot printing at limit

            x += 1      #add space after each word

        if inverse_color:
            color_surface = pygame.Surface(text_surface.get_size()).convert_alpha()
            color_surface.fill((255,255,255))
            text_surface.blit(color_surface, (0,0), special_flags = pygame.BLEND_RGB_MAX)

        return text_surface

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
        return surface

class Controller():
    def __init__(self, controller_type = False):
        self.controller_type = controller_type
        self.keydown = False
        self.keyup = False
        self.value = {'l_stick':[0,0],'r_stick':[0,0],'d_pad':[0,0]}#movement (left analog, arrow keys), right analog, d_pad
        self.key = False
        self.outputs = [self.keydown,self.keyup,self.value,self.key]
        self.map_keyboard()
        self.methods = [self.keybord]#joystick may be appended

        pygame.joystick.init()#initialise joystick module
        self.initiate_controls()#initialise joysticks and add to list
        self.buttonmapping()#read in controler configuration file

    def initiate_controls(self):
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]#save and initialise the controlers.

    def rumble(self):#doesn't rumble...
        for joystick in self.joysticks:
            joystick.rumble(0,0.7,1000)#low fre, high fre, duration

    def buttonmapping(self):
        if not self.controller_type: return
        #self.methods.append(self.joystick)
        file = self.controller_type+'keys.json'
        with open(join(file),'r+') as file:
            mapping=json.load(file)
            self.buttons=mapping['buttons']
            self.analogs=mapping['analogs']

    def get_controllertype(self):#called when a device is added
        for joy in self.joysticks:
            if 'xbox' in joy.get_name().lower():
                self.controller_type = 'xbox'
            elif 'playsation' in joy.get_name().lower():
                self.controller_type = 'ps4'

    def map_keyboard(self):
        self.keyboard_map = {pygame.K_ESCAPE: 'start',
                                pygame.K_RIGHT: 'right',
                                pygame.K_LEFT: 'left',
                                pygame.K_UP: 'up',
                                pygame.K_DOWN: 'down',
                                pygame.K_TAB: 'rb',
                                pygame.K_SPACE: 'a',     #jump, should be X on PS4
                                pygame.K_t: 'y',
                                pygame.K_e: 'b',
                                pygame.K_f: 'x',
                                pygame.K_g: 'y',
                                pygame.K_i: 'select',
                                pygame.K_LSHIFT: 'lb',
                                pygame.K_RETURN: 'return',
                                pygame.K_k: 'rt'
                                }

    def map_inputs(self,event):
        self.keyup=False
        self.keydown=False
        self.key = None
        for method in self.methods:#check for keyboard and controller
            method(event)
        #self.methods[-1](event)

    def keybord(self,event):
        if event.type == pygame.KEYDOWN:
            self.keydown=True
            self.key = self.keyboard_map.get(event.key, '')

            if self.key=='right':
                self.value['l_stick'][0]=1
            elif self.key=='left':
                self.value['l_stick'][0]=-1
            elif self.key=='up':
                self.value['l_stick'][1]=-1
            elif self.key=='down':
                self.value['l_stick'][1]=1

        elif event.type == pygame.KEYUP:#lift bottom
            self.keyup=True
            self.key = self.keyboard_map.get(event.key, '')

            if self.key=='right':
                keys_pressed=pygame.key.get_pressed()
                if keys_pressed[pygame.K_LEFT]:
                    self.value['l_stick'][0]=-1
                else:
                    self.value['l_stick'][0]=0
            elif self.key=='left':
                keys_pressed=pygame.key.get_pressed()
                if keys_pressed[pygame.K_RIGHT]:
                    self.value['l_stick'][0]=1
                else:
                    self.value['l_stick'][0]=0

            elif self.key=='up' or self.key=='down':
                self.value['l_stick'][1]=0

        if event.type==pygame.JOYDEVICEADDED:#if a controller is added while playing
            self.initiate_controls()
            self.methods.append(self.joystick)
            self.get_controllertype()
            self.buttonmapping()#read in controler configuration file

    def joystick(self,event):
        if event.type==pygame.JOYDEVICEREMOVED:#if a controller is removed wile playing
            self.initiate_controls()
            self.methods.pop()

        if event.type==pygame.JOYBUTTONDOWN:#press a button
            self.keydown=True
            self.key=self.buttons[str(event.button)]

        elif event.type==pygame.JOYBUTTONUP:#release a button
            self.keyup=True
            self.key=self.buttons[str(event.button)]

        if event.type==pygame.JOYAXISMOTION:#analog stick

            if event.axis==self.analogs['lh']:#left horizontal
                self.value['l_stick'][0] = event.value
                if abs(event.value) < 0.2:
                    self.value['l_stick'][0] = 0

            if event.axis==self.analogs['lv']:#left vertical
                self.value['l_stick'][1] = event.value
                if abs(event.value) < 0.2:
                    self.value['l_stick'][1] = 0

            if event.axis==self.analogs['rh']:#right horizontal
                self.value['r_stick'][0] = event.value
                if abs(event.value) < 0.2:
                    self.value['r_stick'][0] = 0

            if event.axis==self.analogs['rv']:#right vertical
                self.value['r_stick'][1] = event.value
                if abs(event.value) < 0.2:
                    self.value['r_stick'][1] = 0

        if event.type == pygame.JOYHATMOTION:
            self.keydown = True
            self.value['d_pad'] = [event.value[0],event.value[1]]

    def output(self):
        return [self.keydown,self.keyup,self.value,self.key]
