import pygame, csv, Entities, math, random

platforms = pygame.sprite.Group()
bg_blocks = pygame.sprite.Group()
Enemies = pygame.sprite.Group()
npc = pygame.sprite.Group()
interactables = pygame.sprite.Group()
invisible_blocks = pygame.sprite.Group()

class Tilemap():
    def __init__(self, level,mode='auto'):
        self.tile_size=16
        self.chunk_size=10
        self.total_disatnce=[0,0]
        self.level_name = level
        self.chunks=self.define_chunks("collision")#placeholder to store the chunks containing collision information
        self.chunks_bg1=self.define_chunks("bg1") #chunks containg first bg layer
        self.chunks_interactables=self.define_chunks("interactables")
        self.keys=[]
        self.chunk_render_distance=800
        self.sprite_sheet = self.read_spritesheet("Sprites/level_sheets/" + level + "/sprite_sheet.png")

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
                        if tile=='n':#temporary NPC
                            new_npc = Entities.MrBanks(self.entity_position(tile_x, tile_y, x, y))
                            npc.add(new_npc)
                            tile_x+=1
                            continue
                        if tile=='e':#temporary NPC
                            new_enemie = Entities.Enemy_2(self.entity_position(tile_x, tile_y, x, y),1)
                            Enemies.add(new_enemie)
                            tile_x+=1
                            continue

                        new_block = Entities.Block(self.sprite_sheet[int(tile)],self.entity_position(tile_x, tile_y, x, y),key)
                        platforms.add(new_block)
                        tile_x+=1
                    tile_y+=1

                map = self.chunks_bg1[key]
                tile_x=0
                tile_y=0

                #add bg blocks for new chunk
                for row in map:
                    tile_x=0
                    for tile in row:
                        if tile=='-1':
                            tile_x+=1
                            continue
                        new_block = Entities.BG_Block(self.sprite_sheet[int(tile)],self.entity_position(tile_x, tile_y, x, y),key)
                        bg_blocks.add(new_block)
                        tile_x+=1
                    tile_y+=1

                map = self.chunks_interactables[key]
                tile_x=0
                tile_y=0

                #add bg blocks for new chunk
                for row in map:
                    tile_x=0
                    for tile in row:
                        if tile=='-1':
                            tile_x+=1
                            continue
                        elif tile == '9':
                            new_block = Entities.Chest(self.entity_position(tile_x, tile_y, x, y))
                            interactables.add(new_block)
                        elif tile == '10':
                            new_block = Entities.Chest_Big(self.entity_position(tile_x, tile_y, x, y))
                            interactables.add(new_block)
                        else:
                            new_block = Entities.Door(self.sprite_sheet[int(tile)],self.entity_position(tile_x, tile_y, x, y),key)
                            interactables.add(new_block)
                        tile_x+=1
                    tile_y+=1

            elif chunk_distances[key]>self.chunk_render_distance and key in self.keys:
                platform_list = [i for i in platforms.sprites() if i.chunk_key==key]
                platforms.remove(platform_list)

                bg_list = [i for i in bg_blocks.sprites() if i.chunk_key==key]
                bg_blocks.remove(bg_list)

                #update key
                self.keys.remove(key)

        return platforms, bg_blocks, Enemies, npc, invisible_blocks, interactables
#________________chunks#

    def entity_position(self, tile_x, tile_y, x, y):
        x_pos = tile_x * self.tile_size+self.chunk_size*self.tile_size*x-int(round(self.total_disatnce[0]))
        y_pos = tile_y * self.tile_size+self.chunk_size*self.tile_size*y-int(round(self.total_disatnce[1]))
        return [x_pos,y_pos]

    #load everything at once
    def load_tiles(self,path):
        map=self.read_csv(path)
        x=0
        y=0
        for row in map:
            x=0
            for tile in row:
                if tile=='12':
                    new_block = Entities.Block(1,[x*self.tile_size,y*self.tile_size])
                    platforms.add(new_block)
                x+=1
            y+=1
        self.map_w,self.map_h=x*self.tile_size,y*self.tile_size#map size

        return platforms, Enemies

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
            screen_shake=[random.randint(-4,4),random.randint(-4,4)]
        else:
            screen_shake=[0,0]

        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])+screen_shake[0]
        self.scroll[1]=int(self.scroll[1])+screen_shake[1]



class Auto(Camera):
    def __init__(self):
        super().__init__()

    def scrolling(self,knight,distance,shake):
        self.true_scroll[0]+=(knight.center[0]-4*self.true_scroll[0]-240)/20
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
