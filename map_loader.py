import pygame, csv, Entities, math, random, json

class Level():
    def __init__(self, level, player_center, screen_size):
        self.PLAYER_CENTER = player_center
        self.SCREEN_SIZE = screen_size
        self.tile_size=16
        self.level_name = level
        self.platforms = pygame.sprite.Group()
        self.platforms_pause=pygame.sprite.Group()
        self.npc_collision = pygame.sprite.Group()
        self.init_player_pos = (0,0)
        self.cameras = [Auto(self.player_center),Auto_CapX(self.player_center),Auto_CapY(self.player_center),Fixed()]
        self.camera = self.cameras[0]
        self.load_map_data()

    def load_map_data(self):


    def set_camera(self, camera_number):
        self.camera = self.cameras[camera_number]

    def scrolling(self,player,shake):
        self.camera.scrolling(player,shake)


    def read_spritesheet(self, path):
        sprites = {}

        sheet = pygame.image.load(path).convert_alpha()
        rows = int(sheet.get_rect().h/self.tile_size)
        columns = int(sheet.get_rect().w/self.tile_size)
        n = 0

        for row in range(rows):
            for column in range(columns):
                y = row * self.tile_size
                x = column * self.tile_size
                rect = pygame.Rect(x, y, x + self.tile_size, y + self.tile_size)
                image = pygame.Surface((self.tile_size,self.tile_size),pygame.SRCALPHA,32)
                image.blit(sheet,(0,0),rect)
                sprites[n] = image
                n += 1

        return sprites

    def load_bg_music(self):
        return pygame.mixer.Sound("Audio/" + self.level_name + "/default.wav")

    def load_statics(self, map_state,eprojectile,loot):
    #load Entities that shouldn't despawn with chunks, npc, enemies, interactables etc
        map_statics = self.read_csv("Tiled/" + self.level_name + "_statics.csv")

        pathways = map_state["pathways"]
        chests = map_state["chests"]

        npcs = pygame.sprite.Group()
        interactables = pygame.sprite.Group()
        enemies = Entities.ExtendedGroup()#pygame.sprite.Group()
        camera_blocks = pygame.sprite.Group()
        triggers = pygame.sprite.Group()

        row_index = 0
        col_index = 0

        path_index = 0
        chest_index = 0

        for row in map_statics:
            for tile in row:
                if tile == '-1':
                    col_index += 1
                    continue
                elif tile == '0':
                    new_chest = Entities.Chest((col_index * self.tile_size, row_index * self.tile_size),str(chest_index),chests[str(chest_index)][0],chests[str(chest_index)][1])
                    interactables.add(new_chest)
                    chest_index += 1
                elif tile == '1':
                    new_chest = Entities.Chest_Big((col_index * self.tile_size, row_index * self.tile_size),str(chest_index),chests[str(chest_index)][0],chests[str(chest_index)][1])
                    interactables.add(new_chest)
                    chest_index += 1
                elif tile == '8':
                    new_path = Entities.Door((col_index * self.tile_size, row_index * self.tile_size),pathways[str(path_index)])
                    interactables.add(new_path)
                    path_index += 1
                elif tile == '13':
                    new_path = Entities.Path_Col_v((col_index * self.tile_size, row_index * self.tile_size),pathways[str(path_index)])
                    triggers.add(new_path)
                    path_index += 1
                elif tile == '14':
                    new_path = Entities.Path_Col_h((col_index * self.tile_size, row_index * self.tile_size),pathways[str(path_index)])
                    triggers.add(new_path)
                    path_index += 1
                elif tile == '16':
                    player = (col_index * self.tile_size, row_index * self.tile_size)
                    self.init_player_pos = (col_index * self.tile_size, row_index * self.tile_size)
                elif tile == '17':
                    new_npc = Entities.Aslat((col_index * self.tile_size, row_index * self.tile_size))
                    npcs.add(new_npc)
                elif tile == '25':
                    new_enemy = Entities.Woopie((col_index * self.tile_size, row_index * self.tile_size),eprojectile,loot)
                    enemies.add(new_enemy)
                elif tile == '26':
                    new_enemy = Entities.Larv((col_index * self.tile_size, row_index * self.tile_size),eprojectile,loot)
                    enemies.add(new_enemy)
                elif tile == '27':
                    new_enemy = Entities.Vatt((col_index * self.tile_size, row_index * self.tile_size),eprojectile,loot)
                    enemies.add(new_enemy)
                elif tile == '24':
                    new_enemy = Entities.Flowy((col_index * self.tile_size, row_index * self.tile_size),eprojectile,loot)
                    enemies.add(new_enemy)
                elif tile == '33':
                    new_stop = Entities.Camera_Stop((col_index * self.tile_size, row_index * self.tile_size),'right')
                    camera_blocks.add(new_stop)
                elif tile == '34':
                    new_stop = Entities.Camera_Stop((col_index * self.tile_size, row_index * self.tile_size),'top')
                    camera_blocks.add(new_stop)
                elif tile == '35':
                    new_stop = Entities.Camera_Stop((col_index * self.tile_size, row_index * self.tile_size),'left')
                    camera_blocks.add(new_stop)
                elif tile == '36':
                    new_stop = Entities.Camera_Stop((col_index * self.tile_size, row_index * self.tile_size),'bottom')
                    camera_blocks.add(new_stop)
                elif tile == '40':
                    new_enemy = Entities.Reindeer((col_index * self.tile_size, row_index * self.tile_size),eprojectile,loot)
                    enemies.add(new_enemy)
                col_index += 1
            row_index += 1
            col_index = 0 #reset column

        return player, npcs, enemies, interactables, triggers, camera_blocks

    def load_bg(self):
    #returns one surface with all backround images blitted onto it, for each bg/fg layer
        bg_list = ['bg_fixed','bg_far','bg_mid','bg_near','fg_fixed','fg_paralex','bg_fixed_deco','bg_far_deco','bg_mid_deco','bg_near_deco','fg_fixed_deco','fg_paralex_deco']
        deco_list = ['bg_fixed','bg_far','bg_mid','bg_near','fg_fixed','fg_paralex']
        top_left = {}
        bg_flags = {}
        for bg in bg_list:
            bg_flags[bg] = True

        #all these figures below should be passed and not hardcoded, will break if we change UI etc.
        screen_center = self.player_center
        new_map_diff = (self.init_player_pos[0] - screen_center[0], self.init_player_pos[1] - screen_center[1])

        map_bg = self.read_csv("Tiled/" + self.level_name + "_bg_fixed.csv")
        cols = len(map_bg[0])
        rows = len(map_bg)


        blit_surfaces = {}
        for bg in bg_list:
            blit_surfaces[bg] = pygame.Surface((cols*self.tile_size,rows*self.tile_size), pygame.SRCALPHA, 32).convert_alpha()

        bg_sheets = {}
        bg_maps = {}

        #try loading all paralex backgrounds
        for bg in bg_list:
            try:
                bg_sheets[bg] = self.read_spritesheet("Sprites/level_sheets/" + self.level_name + "/%s.png" % bg)
                bg_maps[bg] = self.read_csv("Tiled/" + self.level_name + "_%s.csv" % bg)
                top_left[bg] = (0,0)
            except:
                bg_flags[bg] = False
                #print("Failed to read %s" % bg)

        for bg in bg_list:
            if bg_flags[bg]:
                for row in range(rows):
                    for col in range(cols):
                        if not bg_maps[bg][row][col] == '-1':
                            #print(bg + " " + bg_maps[bg][row][col])
                            blit_surfaces[bg].blit(bg_sheets[bg][int(bg_maps[bg][row][col])], (col * self.tile_size, row * self.tile_size))
                            if top_left[bg] == (0,0):
                                #get inital position for blit
                                top_left[bg] = (col * self.tile_size, row * self.tile_size)




        #blit deco over corresponding layer
        for bg in deco_list:
            if bg_flags[bg + '_deco']:
                blit_surfaces[bg].blit(blit_surfaces[bg + '_deco'],(0,0))

        #print(top_left)
        backgrounds = []
        for i, bg in enumerate(bg_list):
            if bg == 'bg_fixed':
                backgrounds.append(Entities.BG_Block((0,0),blit_surfaces[bg]))#pos,img,paralex
            elif bg == 'bg_far':
                backgrounds.append(Entities.BG_Block((-int(0.97*new_map_diff[0]),-int(0.97*new_map_diff[1])),blit_surfaces[bg],0.03))#pos,img,paralex
            elif bg == 'bg_mid':
                backgrounds.append(Entities.BG_Block((-int(0.5*new_map_diff[0]),-int(0.5*new_map_diff[1])),blit_surfaces[bg],0.5))#pos,img,paralex
            elif bg == 'bg_near':
                backgrounds.append(Entities.BG_Block((-int(0.25*new_map_diff[0]),-int(0.25*new_map_diff[1])),blit_surfaces[bg],0.75))#pos,img,paralex
            elif bg == 'fg_fixed':
                backgrounds.append(Entities.BG_Block((0,0),blit_surfaces[bg]))#pos,img,paralex
            elif bg == 'fg_paralex':
                backgrounds.append(Entities.BG_Block((int(0.25*new_map_diff[0]),int(0.25*new_map_diff[1])),blit_surfaces[bg],1.25))#pos,img,paralex
        del blit_surfaces, bg_sheets, bg_maps
        return backgrounds

    def load_collison_layer(self):#load the whole map

class Sprite_sheet():

    def __init__(self, filename):
        try:
            self.sheet =  pygame.image.load(filename).convert()
        except:
            #print(f"Unable to load spritesheet image: {filename}")
            raise SystemExit(e)

    def image_at(self, rectangle, colorkey = None):
        #Loads image from x, y, x+tilesize, y+tilesize.

        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey = None):
        #returns list of all images in sheet
        return [self.image_at(rect, colorkey) for rect in rects]


#scrolling

class Camera():
    def __init__(self, center = (240,180)):
        self.scroll=[0,0]
        self.true_scroll=[0,0]
        self.center = center

    def update_scroll(self,shake):
        if shake>0:#inprinciple we do not need this if
            screen_shake=[random.randint(-shake,shake),random.randint(-shake,shake)]
        else:
            screen_shake=[0,0]

        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])+screen_shake[0]
        self.scroll[1]=int(self.scroll[1])+screen_shake[1]

class Auto(Camera):
    def __init__(self, center):
        super().__init__(center)

    def scrolling(self,knight,shake):
        self.true_scroll[0]+=(knight.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-self.center[1])
        self.update_scroll(shake)

class Auto_CapX(Camera):
    def __init__(self, center):
        super().__init__(center)

    def scrolling(self,knight,shake):
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-self.center[1])
        self.update_scroll(shake)

class Auto_CapY(Camera):
    def __init__(self, center):
        super().__init__(center)

    def scrolling(self,knight,shake):
        self.true_scroll[0]+=(knight.center[0]-8*self.true_scroll[0]-self.center[0])/15
        self.update_scroll(shake)

class Fixed(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,shake):
        self.update_scroll(shake)

class Autocap(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,distance,shake):
        if knight.center[0]>400:
            self.true_scroll[0]+=5
        elif knight.center[0]<30:
            self.true_scroll[0]-=5
        elif knight.center[0]>150 and knight.center[0]<220:
            self.true_scroll[0]=0

        if knight.center[1]>200:
            self.true_scroll[1]+=0.5
        elif knight.center[1]<70:
            self.true_scroll[1]-=0.5
        elif knight.center[1]>130 and knight.center[1]<190:
            self.true_scroll[1]=0

        self.update_scroll(shake)

class Border(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,total_distance,shake):
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-180)
        if -40 < total_distance[0]<1400:#map boundaries
            self.true_scroll[0]+=(knight.center[0]-4*self.true_scroll[0]-240)/20
        else:
            if knight.center[0]<60:
                self.true_scroll[0]-=1
            elif knight.center[0]>440:
                self.true_scroll[0]+=1
            else:
                self.true_scroll[0]=0
        self.update_scroll(shake)
