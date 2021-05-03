import pygame
from os import listdir, walk
from os.path import isfile, join

class Sprites():
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

        list_of_sprites.sort()
        return [pygame.image.load(file) for file in list_of_sprites]

    def load_single_sprite(self,path_to_sprite):
        #use to load single sprite, full path must be provided

        return pygame.image.load(path_to_sprite)



#class containing sprites for player
class Sprites_player(Sprites):

    player_path = "Sprites/player/"
    def __init__(self):
        super().__init__()
        self.sprite_dict = self.load_all_sprites(self.player_path)
        print(self.sprite_dict['run'])

    def get_image(self, input, timer, dir):
        if dir >= 0:
            return self.sprite_dict[input][timer]
        elif dir < 0:
            return pygame.transform.flip(self.sprite_dict[input][timer],True,False)

    def get_frame_number(self, input):
        return len(self.sprite_dict[input])

class Sprites_evil_knight(Sprites):

    player_path = "Sprites/player/"
    def __init__(self):
        super().__init__()
        self.sprite_dict = self.load_all_sprites(self.player_path)

    def get_image(self, input, timer, dir):
        if dir >= 0:
            return self.sprite_dict[input][timer]
        elif dir < 0:
            return pygame.transformation.flip(self.sprite_dict[input][timer])
