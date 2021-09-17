import pygame, csv, Entities, math, random, json

class Tilemap():
    def __init__(self, level,mode='auto'):
        self.tile_size=16
        self.chunk_size=10
        self.total_disatnce=[0,0]
        self.level_name = level
        self.chunks=self.define_chunks("collision")#placeholder to store the chunks containing collision information
        self.keys=[]
        self.chunk_render_distance=1000
        self.sprite_sheet = self.read_spritesheet("Sprites/level_sheets/" + level + "/bg_fixed.png")
        self.platforms = pygame.sprite.Group()
        self.invisible_blocks = pygame.sprite.Group()

        if mode=='auto':
            self.camera=Auto()
        elif mode=='autocap':
            self.camera=Autocap()
        elif mode=='border':
            self.camera=Border()

    def scrolling(self,knight,shake):
        self.camera.scrolling(knight,self.total_disatnce,shake)

    def read_csv(self, path):
        tile_map=[]
        with open(path) as data:
            data=csv.reader(data,delimiter=',')
            for row in data:
                tile_map.append(list(row))
        return tile_map

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


#________________chunks#
    def define_chunks(self,path):#devide the data into chunks
        map=self.read_csv("Tiled/" + self.level_name + "_" + path + ".csv")

        columns = len(map[0])//self.chunk_size
        rows = len(map)//self.chunk_size
        chunks = {}

        for k in range(rows):#Row: number of chunks
            for j in range(columns):#Column: number of chunks
                chunk=[[]*self.chunk_size]*self.chunk_size
                for i in range(0,self.chunk_size):#extract rows
                    chunk[i]=map[i+k*self.chunk_size][j*self.chunk_size:j*self.chunk_size+self.chunk_size]
                string=str(k)+';'+str(j)
                chunks[string] = chunk#will look like chunks={'0;0':data,'0;1':data...}

        return chunks

    def chunk_distance(self):
        chunk_distance={}
        self.total_disatnce[0]+=self.camera.scroll[0]#total distance
        self.total_disatnce[1]+=self.camera.scroll[1]#total distance

        for key in self.chunks.keys():
            y=int(key.split(';')[0])#y
            x=int(key.split(';')[1])#x

            chunk_distance_x=self.chunk_size*self.tile_size*x-240-self.total_disatnce[0]+self.chunk_size*self.tile_size/2#from middle
            chunk_distance_y=self.chunk_size*self.tile_size*y-180-self.total_disatnce[1]+self.chunk_size*self.tile_size/2#from middle

            chunk_distance[key]=int(round(math.sqrt(chunk_distance_x**2+chunk_distance_y**2)))
        return chunk_distance

    def test(self):
        print(self.collision_sheet[1])

    def load_bg_music(self):
        return pygame.mixer.Sound("Audio/" + self.level_name + "/default.wav")

    def load_statics(self, map_state):
    #load entities that shouldn't despawn with chunks, npc, enemies, interactables etc
        map_statics = self.read_csv("Tiled/" + self.level_name + "_statics.csv")

        pathways = map_state["pathways"]
        chests = map_state["chests"]

        npcs = pygame.sprite.Group()
        interactables = pygame.sprite.Group()
        enemies = pygame.sprite.Group()

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
                elif tile == '16':
                    player = (col_index * self.tile_size, row_index * self.tile_size)
                elif tile == '17':
                    new_npc = Entities.Aslat((col_index * self.tile_size, row_index * self.tile_size))
                    npcs.add(new_npc)
                elif tile == '25':
                    new_enemy = Entities.Woopie((col_index * self.tile_size, row_index * self.tile_size))
                    enemies.add(new_enemy)
                elif tile == '24':
                    pass
                    #new_enemy = Entities.Enemy_2((col_index * self.tile_size, row_index * self.tile_size))
                    #enemies.add(new_enemy)
                col_index += 1
            row_index += 1
            col_index = 0 #reset column

        return player, npcs, enemies, interactables

    def load_bg(self):
    #returns one surface with all backround images blitted onto it
        bg_list = ['bg_fixed','bg_far','bg_mid','bg_near','fg_fixed','fg_paralex']
        bg_flags = {}
        for bg in bg_list:
            bg_flags[bg] = True

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
            except:
                bg_flags[bg] = False
                print("Failed to read %s" % bg)

        for row in range(rows):
            for col in range(cols):
                for bg in bg_list:
                    if bg_flags[bg]:
                        if not bg_maps[bg][row][col] == '-1':
                            blit_surfaces[bg].blit(bg_sheets[bg][int(bg_maps[bg][row][col])], (col * self.tile_size, row * self.tile_size))


        backgrounds = []
        for bg in bg_list:
            if bg == 'bg_fixed':
                backgrounds.append(Entities.BG_Block(blit_surfaces[bg],(0,0)))
            elif bg == 'bg_far':
                backgrounds.append(Entities.BG_far(blit_surfaces[bg],(0,-100)))
            elif bg == 'bg_mid':
                backgrounds.append(Entities.BG_mid(blit_surfaces[bg],(0,0)))
            elif bg == 'bg_near':
                backgrounds.append(Entities.BG_near(blit_surfaces[bg],(0,0)))
            elif bg == 'fg_fixed':
                backgrounds.append(Entities.FG_fixed(blit_surfaces[bg],(0,0)))
            elif bg == 'fg_paralex':
                backgrounds.append(Entities.FG_paralex(blit_surfaces[bg],(0,0)))

        return backgrounds

    def load_chunks(self):
        chunk_distances=self.chunk_distance()


        for key in chunk_distances.keys():
            if chunk_distances[key]<self.chunk_render_distance and key not in self.keys:

                self.keys.append(key)#store all keys already loaded

                map=self.chunks[key]
                tile_x=0
                tile_y=0
                y=int(key.split(';')[0])#y
                x=int(key.split(';')[1])#x

                #add collision blocks for new chunk
                for row in map:
                    tile_x=0
                    for tile in row:
                        if tile=='-1':
                            tile_x+=1
                            continue

                        new_block = Entities.Platform(self.sprite_sheet[int(tile)],self.entity_position(tile_x, tile_y, x, y),key)
                        self.platforms.add(new_block)
                        tile_x+=1
                    tile_y+=1

            elif chunk_distances[key]>self.chunk_render_distance and key in self.keys:
                platform_list = [i for i in self.platforms.sprites() if i.chunk_key==key]
                self.platforms.remove(platform_list)

                #update key
                self.keys.remove(key)

        return self.platforms, self.invisible_blocks
#________________chunks#

    def entity_position(self, tile_x, tile_y, x, y):
        x_pos = tile_x * self.tile_size+self.chunk_size*self.tile_size*x-int(round(self.total_disatnce[0]))
        y_pos = tile_y * self.tile_size+self.chunk_size*self.tile_size*y-int(round(self.total_disatnce[1]))
        return [x_pos,y_pos]

class Sprite_sheet():

    def __init__(self, filename):
        try:
            self.sheet =  pygame.image.load(filename).convert()
        except:
            print(f"Unable to load spritesheet image: {filename}")
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
    def __init__(self):
        self.scroll=[0,0]
        self.true_scroll=[0,0]

    def update_scroll(self,shake):
        if shake>0:
            screen_shake=[random.randint(-shake,shake),random.randint(-shake,shake)]
        else:
            screen_shake=[0,0]

        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])+screen_shake[0]
        self.scroll[1]=int(self.scroll[1])+screen_shake[1]

class Auto(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,distance,shake):
        self.true_scroll[0]+=(knight.center[0]-10*self.true_scroll[0]-240)/20
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-180)
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

    def scrolling(self,knight,total_disatnce,shake):
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-180)
        if -40 < total_disatnce[0]<1400:#map boundaries
            self.true_scroll[0]+=(knight.center[0]-4*self.true_scroll[0]-240)/20
        else:
            if knight.center[0]<60:
                self.true_scroll[0]-=1
            elif knight.center[0]>440:
                self.true_scroll[0]+=1
            else:
                self.true_scroll[0]=0
        self.update_scroll(shake)
