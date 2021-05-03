import pygame, csv, Entities, math

platforms = pygame.sprite.Group()
Enemies = pygame.sprite.Group()

class Tilemap():
    def __init__(self):
        self.tile_size=16
        self.chunk_size=10
        self.scroll=[0,0]
        self.true_scroll=[0,0]
        self.total_disatnce=[0,0]
        self.chunks={}#placeholder to store the chunks
        self.keys=[]
        self.chunk_render_distance=400

    @staticmethod
    def read_csv(path):
        tile_map=[]
        with open(path) as data:
            data=csv.reader(data,delimiter=',')
            for row in data:
                tile_map.append(list(row))
        return tile_map


#________________chunks#
    def define_chunks(self,path):#devide the data into chunks
        map=self.read_csv(path)
        for k in range(len(map[0])//self.chunk_size):#Row: number of chunks
            for j in range(len(map[:][0])//self.chunk_size):#Column: number of chunks
                chunk=[[]*self.chunk_size]*self.chunk_size
                for i in range(0,self.chunk_size):#extract rows
                    chunk[i]=map[i+k*self.chunk_size][j*self.chunk_size:j*self.chunk_size+self.chunk_size]
                string=str(k)+';'+str(j)
                self.chunks[string]=chunk#will look like chunks={'0;0':data,'0;1':data...}

    def chunk_distance(self):
        chunk_distance={}
        self.total_disatnce[0]+=self.scroll[0]#total distance
        self.total_disatnce[1]+=self.scroll[1]#total distance

        for key in self.chunks.keys():
            y=int(key.split(';')[0])#y
            x=int(key.split(';')[1])#x

            chunk_distance_x=self.chunk_size*self.tile_size*x-400-self.total_disatnce[0]+self.chunk_size*self.tile_size/2#from middle
            chunk_distance_y=self.chunk_size*self.tile_size*y-200-self.total_disatnce[1]+self.chunk_size*self.tile_size/2#from middle

            chunk_distance[key]=int(round(math.sqrt(chunk_distance_x**2+chunk_distance_y**2)))
        return chunk_distance

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

                for row in map:
                    tile_x=0
                    for tile in row:
                        if tile=='1':
                            new_block = Entities.Block(1,[tile_x*self.tile_size+self.chunk_size*self.tile_size*x-int(round(self.total_disatnce[0])),tile_y*self.tile_size+self.chunk_size*self.tile_size*y-int(round(self.total_disatnce[1]))],key)
                            platforms.add(new_block)
                        elif tile=='2':
                            new_block = Entities.Block(2,[tile_x*self.tile_size+self.chunk_size*self.tile_size*x-int(round(self.total_disatnce[0])),tile_y*self.tile_size+self.chunk_size*self.tile_size*y-int(round(self.total_disatnce[1]))],key)
                            platforms.add(new_block)
                        elif tile=='e':
                            new_Enemies = Entities.Enemy_1([tile_x*self.tile_size+self.chunk_size*self.tile_size*x-int(round(self.total_disatnce[0])),tile_y*self.tile_size+self.chunk_size*self.tile_size*y-int(round(self.total_disatnce[1]))],1)
                            Enemies.add(new_Enemies)

                        tile_x+=1
                    tile_y+=1
            elif chunk_distances[key]>self.chunk_render_distance and key in self.keys:
                entity_list = [i for i in platforms.sprites() if i.chunk_key==key]

                platforms.remove(entity_list)#need to remove from playforms grup in main

                #update key
                self.keys.remove(key)

        return platforms, Enemies
#________________chunks#





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
