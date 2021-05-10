import pygame, csv, Entities, math

platforms = pygame.sprite.Group()
bg_blocks = pygame.sprite.Group()
Enemies = pygame.sprite.Group()
npc = pygame.sprite.Group()
invisible_blocks = pygame.sprite.Group()

class Tilemap():
    def __init__(self, level):
        self.tile_size=16
        self.chunk_size=50
        self.scroll=[0,0]
        self.true_scroll=[0,0]
        self.total_disatnce=[0,0]
        self.chunks={}#placeholder to store the chunks containing collision information
        self.chunks_bg1={} #chunks containg first bg layer
        self.keys=[]
        self.chunk_render_distance=800
        self.level_name = level
        self.collision_sheet = self.read_spritesheet("Sprites/" + level + "/collision.png")
        self.bg1_sheet = self.read_spritesheet("Sprites/" + level + "/bg1.png")

    def scrolling(self,knight):
        self.true_scroll[0]+=(knight.center[0]-4*self.true_scroll[0]-240)/20
        self.true_scroll[1]+=(knight.center[1]-self.true_scroll[1]-180)

        self.scroll=self.true_scroll.copy()
        self.scroll[0]=int(self.scroll[0])
        self.scroll[1]=int(self.scroll[1])

        #if knight.action['death']:#if kngiht is dead, don't move game.screen
        #    self.scroll[0]=0
        #    self.scroll[1]=0

    #@staticmethod
    def read_csv(self, path):
        tile_map=[]
        with open(path) as data:
            data=csv.reader(data,delimiter=',')
            for row in data:
                tile_map.append(list(row))
        return tile_map

    def read_spritesheet(self, path):
        sprites = {}
        print(path)
        sheet = pygame.image.load(path).convert_alpha()
        rows = int(sheet.get_rect().w/self.tile_size)
        columns = int(sheet.get_rect().h/self.tile_size)
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
    def define_chunks(self):#devide the data into chunks
        map=self.read_csv("Tiled/" + self.level_name + "_collision.csv")
        map_bg=self.read_csv("Tiled/" + self.level_name + "_bg1.csv")
        for k in range(len(map[0])//self.chunk_size):#Row: number of chunks
            for j in range(len(map[:][0])//self.chunk_size):#Column: number of chunks
                chunk=[[]*self.chunk_size]*self.chunk_size
                chunk_bg=[[]*self.chunk_size]*self.chunk_size
                for i in range(0,self.chunk_size):#extract rows
                    chunk[i]=map[i+k*self.chunk_size][j*self.chunk_size:j*self.chunk_size+self.chunk_size]
                    chunk_bg[i]=map_bg[i+k*self.chunk_size][j*self.chunk_size:j*self.chunk_size+self.chunk_size]
                string=str(k)+';'+str(j)
                self.chunks[string] = chunk#will look like chunks={'0;0':data,'0;1':data...}
                self.chunks_bg1[string] = chunk_bg

    def chunk_distance(self):
        chunk_distance={}
        self.total_disatnce[0]+=self.scroll[0]#total distance
        self.total_disatnce[1]+=self.scroll[1]#total distance

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
                        new_block = Entities.Block(self.collision_sheet[int(tile)],self.entity_position(tile_x, tile_y, x, y),key)
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
                        new_block = Entities.BG_Block(self.bg1_sheet[int(tile)],self.entity_position(tile_x, tile_y, x, y),key)
                        bg_blocks.add(new_block)
                        tile_x+=1
                    tile_y+=1

            elif chunk_distances[key]>self.chunk_render_distance and key in self.keys:
                entity_list = [i for i in platforms.sprites() if i.chunk_key==key]

                platforms.remove(entity_list)#need to remove from playforms grup in main

                #update key
                self.keys.remove(key)

        return platforms, bg_blocks, Enemies, npc, invisible_blocks
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
                if tile=='1':
                    new_block = Entities.Block(1,[x*self.tile_size,y*self.tile_size])
                    platforms.add(new_block)
                elif tile=='2':
                    new_block = Entities.Block(2,[x*self.tile_size,y*self.tile_size])
                    platforms.add(new_block)
                elif tile=='e':
                    new_Enemies = Entities.Enemy_1([x*self.tile_size,y*self.tile_size],1)
                    Enemies.add(new_Enemies)
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
