import pygame, json
from os import listdir, walk
from os.path import isfile, join


def read_json(path):
    with open(path) as f:
        text = json.load(f)
    return text

def write_json():
    pass

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
        return [pygame.image.load(file) for file in list_of_sprites]

    def load_single_sprite(self,path_to_sprite):
        #use to load single sprite, full path must be provided
        return pygame.image.load(path_to_sprite)

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
                image = pygame.Surface(sprite_size,pygame.SRCALPHA,32)
                image.blit(sheet,(0,0),rect)
                sprite_dict[n] = image
                n+=1
        return sprite_dict

#class containing sprites for players (pre,post,main charge)
class Sprites_Player(Sprites):

    def __init__(self,path,charge=False):
        super().__init__()

        pre_dict = self.load_all_sprites(path+'pre/')
        main_dict = self.load_all_sprites(path+'main/')
        post_dict = self.load_all_sprites(path+'post/')
        charge_dict = self.load_all_sprites(path+'charge/')

        if charge:#if there is charge
            charge_dict = self.load_all_sprites(path+'charge/')
            self.sprite_dict={'pre':pre_dict,'main':main_dict,'post':post_dict,'charge':charge_dict}
        else:
            self.sprite_dict={'pre':pre_dict,'main':main_dict,'post':post_dict}

    def get_image(self, input, timer, dir,phase):#phase pre, main, post
        if input=='sword' and dir[1]>0:
            input=input+'_up'
        elif input=='sword' and dir[1]<0:
            input=input+'_down'

        if dir[0] <= 0:
            return self.sprite_dict[phase][input][timer]
        elif dir[0] > 0:
            return pygame.transform.flip(self.sprite_dict[phase][input][timer],True,False)

    def get_frame_number(self, input,dir,phase):
        if input=='sword' and dir[1]>0:
            input=input+'_up'
        elif input=='sword' and dir[1]<0:
            input=input+'_down'

        return len(self.sprite_dict[phase][input])

#class containing sprites for enemies and NPC (no charge, pre, post or main)
class Sprites_enteties(Sprites):

    def __init__(self,path):
        super().__init__()
        self.sprite_dict = self.load_all_sprites(path)

    def get_image(self, input, timer, dir):
        if input=='sword' and dir[1]>0:
            input=input+'_up'
        elif input=='sword' and dir[1]<0:
            input=input+'_down'

        if dir[0] <= 0:
            return self.sprite_dict[input][timer]
        elif dir[0] > 0:
            return pygame.transform.flip(self.sprite_dict[input][timer],True,False)

    def get_frame_number(self, input,dir):
        if input=='sword' and dir[1]>0:
            input=input+'_up'
        elif input=='sword' and dir[1]<0:
            input=input+'_down'

        return len(self.sprite_dict[input])

#class for reading and rendering fonts
class Alphabet():
    def __init__(self, path):

        self.char_size = (4,6)
        self.character_order=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','0','1','2','3','4','5','6','7','8','9',',','.','\'','!','?']
        self.character_lower=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        sheet=Sprites().generic_sheet_reader("Sprites/utils/alphabet_low.png",self.char_size[0],self.char_size[1],1,len(self.character_order))

        self.characters={}
        #map sprites to charactersin dict
        for i, c in enumerate(self.character_order):
            self.characters[c] = sheet[i]

        #map lower case to same sprites (change __init__ incase lower case sprites are desired)
        for i, c in enumerate(self.character_lower):
            self.characters[c] = sheet[i]

    #returns a surface with size of input, and input text. Automatic line change
    def render(self, surface_size, text, limit = 1000):
        text_surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32)
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
                text_surface.blit(self.characters[c],pos)
                x += 1
                if x_max * y + x > limit: return text_surface #spot printing at limit

            x += 1      #add space after each word

        return text_surface

class Controller():
    def __init__(self,type):

        pygame.joystick.init()#initialise joystick module
        self.update_controlls()#initialise joysticks and add to list

        self.buttonmapping(type)

    def update_controlls(self):
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]#save and initialise the controllers.

    def buttonmapping(self,type):
        file=type+'_keys.jason'
        with open(join(file),'r+') as file:
            self.bottons=json.load(file)

        #xbox
        #left hori:1, left vert:0, right hori: 3, right vert: 2, left trigger:5, right trigger:4
        self.analogs={'lv':1,'lh':0,'rv':3,'rh':2,'lt':5,'rt':4}

    def inputs(self):
        pass
