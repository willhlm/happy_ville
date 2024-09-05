import pygame, math, sys
import entities, read_files, weather, entities_parallax, states, platforms
import constants as C

class Level():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.PLAYER_CENTER = [game_objects.game.window_size[0] * 0.5, game_objects.game.window_size[1] * 0.5]
        self.TILE_SIZE = C.tile_size
        self.level_name = ''
        self.biome_name = ''
        self.area_change = True#a flag to chenge if we change area
        self.biome = Biome(self)

    def load_map(self,map_name,spawn):
        self.references = {'shade':[],'gate':[],'lever':[]}#to save some stuff so that it can be organisesed later in case e.g. some things needs to be loaded in order: needs to be cleaned after each map loading
        self.level_name = map_name.lower()
        self.spawn = spawn
        self.game_objects.lights.new_map()#set ambient default light and clear light sources
        self.check_biome()#pause the sound if we change area
        self.load_map_data()#load the map data
        self.init_state_file()#need to be before load groups
        self.load_groups()#memory leak here somwerhe
        self.set_camera()
        self.orginise_references()

    def set_camera(self):
        self.game_objects.camera.reset_player_center()##need to be after load_group -> normal position
        self.biome.set_camera()#need to be after load_group  -> biome specific camera

    def check_biome(self):
        self.area_change = self.level_name[:self.level_name.rfind('_')] != self.biome_name
        if self.area_change:#new biome
            self.biome.clear_biome()
            self.biome_name = self.level_name[:self.level_name.rfind('_')]
            self.biome = getattr(sys.modules[__name__], self.biome_name.capitalize(), Biome)(self)#returns Biome (default) if there is no biome class
        room = self.level_name[self.level_name.rfind('_') + 1 :]
        self.biome.room(room)

    def init_state_file(self):
        if not self.game_objects.world_state.state.get(self.level_name, False):#if it is the first time loading the room
            self.game_objects.world_state.init_state_file(self.level_name)

    def load_map_data(self):
        level_name = self.level_name[:self.level_name.rfind('_')]
        map_data = read_files.read_json("maps/%s/%s.json" % (level_name,self.level_name))
        self.map_data = read_files.format_tiled_json_group(map_data)

        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if 'static' in tileset['source']:#name of the tsx file
                    self.map_data['statics_firstgid'] =  tileset['firstgid']
                elif 'interactables' in tileset['source']:#name of the tsx file
                    self.map_data['interactables_firstgid'] = tileset['firstgid']
                elif 'objects' in tileset['source']:#name of the tsx file
                    self.map_data['objects_firstgid'] = tileset['firstgid']

    def read_all_spritesheets(self):
        sprites = {}
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():#objexts have source in dict
                continue

            level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _
            sheet = pygame.image.load("maps/%s/%s" % (level_name, tileset['image'])).convert_alpha()
            rows = int(sheet.get_rect().h/self.TILE_SIZE)
            columns = int(sheet.get_rect().w/self.TILE_SIZE)
            n = tileset['firstgid']

            for row in range(rows):
                for column in range(columns):
                    y = row * self.TILE_SIZE
                    x = column * self.TILE_SIZE
                    rect = pygame.Rect(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE)
                    image = pygame.Surface((self.TILE_SIZE,self.TILE_SIZE),pygame.SRCALPHA,32).convert_alpha()
                    image.blit(sheet,(0,0),rect)
                    sprites[n] = image
                    n += 1
        return sprites

    def load_groups(self):
        self.spritesheet_dict = self.read_all_spritesheets()#read the bg spritesheats, outside the loop
        self.game_objects.all_bgs.reference = {}#to store the reference positions of each static bg layer or other information

        for group in self.map_data['groups']:
            parallax = [self.map_data['groups'][group]['parallaxx'], self.map_data['groups'][group]['parallaxy']]
            offset = [self.map_data['groups'][group]['offsetx'], self.map_data['groups'][group]['offsety']]
            
            self.layer = group#name of the folder in tiled

            self.load_objects(self.map_data['groups'][group]['objects'],parallax,offset,'back')#objects behind layers
            self.load_layers(self.map_data['groups'][group]['layers'],parallax,offset)#memory leak somerhe
            self.load_objects(self.map_data['groups'][group]['objects'],parallax,offset,'front')#object infron of layers

    def load_objects(self, data, parallax, offset, position):
        for object in data.keys():
            if object == 'statics' or object == 'interactables':
                if position == 'back': continue#only load statics and interactables in the front
                load_objects = {'interactables':self.load_interactables_objects,'statics':self.load_statics}#the keys are the naes of the object in tiled
                load_objects[object](data[object], parallax, offset)
            else:#front and back objects
                if object == position:#load it at back or front
                    self.biome.load_objects(data[object], parallax, offset)

    def load_statics(self,data,parallax,offset):#load statics and collision
        chest_int = 1
        soul_essence_int = 1

        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1] - object_size[1]]#topleft
            properties = obj.get('properties',[])

            if 'polygon' in obj.keys():#check for polygon type first
                points_list = []
                for point in obj['polygon']:
                    points_list.append((point['x'],point['y']))

                fall_through = obj.get('properties',True)
                new_block = platforms.Collision_right_angle(object_position, points_list,fall_through)
                self.game_objects.platforms_ramps.add(new_block)
                continue

            id = obj['gid'] - self.map_data['statics_firstgid']
            if id == 0:#player
                for property in properties:
                    if property['name'] == 'spawn':
                        if type(self.spawn).__name__ != 'str':#if respawn/fast tarvel
                            self.game_objects.player.set_pos(self.spawn)
                        else:#if notmal load
                            if property['value'] == self.spawn:
                                self.game_objects.player.set_pos(object_position)

            elif id == 1:#npcs
                for property in properties:
                    if property['name'] == 'class':
                        npc_name = property['value']

                new_npc = getattr(entities, npc_name)
                self.game_objects.npcs.add(new_npc(object_position,self.game_objects))

            elif id == 2:#enemies
                for property in properties:
                    if property['name'] == 'class':
                        enemy_name = property['value']
                new_enemy = getattr(entities, enemy_name)
                self.game_objects.enemies.add(new_enemy(object_position, self.game_objects))

            elif id == 4:#Spawner: spawn enemies
                values={}
                for property in properties:
                    if property['name'] == 'class':
                        values['entity'] = property['value']
                    elif property['name'] == 'number':
                        values['number']=property['value']
                new_spawn = entities.Spawner(object_position,self.game_objects,values)
                self.game_objects.cosmetics.add(new_spawn)

            elif id == 5:#items
                kwarg = {}
                for property in properties:
                    if property['name'] == 'item':
                        loot = property['value']
                    elif property['name'] == 'quest':
                        kwarg['quest'] = property['value']

                new_loot = getattr(entities, loot)(object_position, self.game_objects, **kwarg)
                self.game_objects.loot.add(new_loot)

            elif id == 7:#normal collision blocks
                types = 'dust'
                for property in properties:
                    if property['name'] == 'particles':
                        types = property['value']
                new_block = platforms.Collision_block(object_position,object_size,types)
                self.game_objects.platforms.add(new_block)

            elif id == 8:#spike collision blocks
                new_block = platforms.Collision_dmg(object_position,object_size)
                self.game_objects.platforms.add(new_block)

            elif id == 9:
                sfx = None
                for property in properties:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    elif property['name'] == 'spawn':
                        spawn = property['value']
                    elif property['name'] == 'image':
                        image = property['value']
                    elif property['name'] == 'sfx':
                        sfx = property['value']

                new_path = entities.Path_inter(object_position,self.game_objects,object_size,destination,spawn,image,sfx)
                self.game_objects.interactables.add(new_path)

            elif id == 10:
                for property in properties:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    if property['name'] == 'spawn':
                        spawn = property['value']
                new_path = entities.Path_col(object_position,self.game_objects,object_size,destination,spawn)
                self.game_objects.interactables.add(new_path)

            elif id == 11:#one way collision block (currently only top implemented)
                for property in properties:
                    if property['name'] == 'particles':
                        types = property['value']
                new_block = platforms.Collision_oneway_up(object_position,object_size,types)
                self.game_objects.platforms.add(new_block)

            elif id == 12:#hole, if aila collides, aila will move to safe_spawn position
                new_block = entities.Hole(object_position, self.game_objects, object_size)
                self.game_objects.interactables.add(new_block)

            elif id == 13:#spawn position
                spawn_pos = [object_position[0] + object_size[0]*0.5, object_position[1] + object_size[1]*0.5]
                for property in properties:
                    if property['name'] == 'position':
                        pos = property['value']
                        string_list = pos.split(",")
                        spawn_pos = [int(item) for item in string_list]

                new_block = entities.Safe_spawn(object_position, self.game_objects, object_size, spawn_pos)
                self.game_objects.interactables.add(new_block)

            elif id == 14:#camera stop
                camera_offset = 0
                for property in properties:
                    if property['name'] == 'direction':
                        values = property['value']
                    if property['name'] == 'offset':
                        camera_offset = property['value']
                new_camera_stop = entities.Camera_Stop(self.game_objects, object_size, object_position, values, camera_offset)
                self.game_objects.camera_blocks.add(new_camera_stop)

            elif id == 15:#bg_particles -> circles, rain, fog etc
                for property in properties:
                    if property['name'] == 'particle':
                        particle_type = property['value']

                new_shader_screen = getattr(weather, particle_type)
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(new_shader_screen(self.game_objects, parallax, 20))
                else:
                    self.game_objects.all_bgs.add(new_shader_screen(self.game_objects, parallax, 20))

            elif id == 16:#scren shade
                for property in properties:
                    if property['name'] == 'colour':
                        colour = property['value']

                new_shade = entities.Shade_Screen(self.game_objects,parallax,pygame.Color(colour))
                self.references['shade'].append(new_shade)
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(new_shade)
                else:
                    self.game_objects.all_bgs.add(new_shade)

            #elif id == 17:#leaves
            #    information = [object_position,object_size]
            #    if self.layer.startswith('fg')
            #        entities_parallax.create_leaves(information,parallax,self.game_objects.all_fgs)
            #    else:
            #        entities_parallax.create_leaves(information,parallax,self.game_objects.all_bgs)

            elif id  == 18:#god rays
                prop = {}
                for property in properties:
                    if property['name'] == 'angle':
                        prop['angle'] = 3.141592*float(property['value'])/180
                    elif property['name'] == 'falloff':
                        falloff = property['value'].split(',')
                        prop['falloff'] = [float(falloff[0]),float(falloff[1])]
                    elif property['name'] == 'position':
                        position = property['value'].split(',')
                        prop['position'] = [float(position[0]),float(position[1])]
                    elif property['name'] == 'colour':
                         colour= list(pygame.Color(property['value']))
                         prop['colour'] = [colour[1]/255,colour[2]/255,colour[3]/255,colour[0]/255]

                god_rays = entities.God_rays(object_position, self.game_objects, parallax, object_size, **prop)
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(god_rays)
                else:
                    self.game_objects.all_bgs.add(god_rays)

            elif id == 19:#trigger
                kwarg = {}
                for property in properties:
                    if property['name'] == 'event':
                        kwarg['event'] = property['value']
                    elif property['name'] == 'new_state':
                        kwarg['new_state'] = property['value']                        
                new_trigger = entities.Event_trigger(object_position, self.game_objects, object_size, **kwarg)
                self.game_objects.interactables.add(new_trigger)

            elif id == 20:#reflection object
                for property in properties:
                    if property['name'] == 'direction':
                        dir = property['value']
                dir = 'up'
                reflection = entities.Reflection(object_position, self.game_objects, parallax, object_size, dir)

                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(reflection)
                else:
                    self.game_objects.all_bgs.add(reflection)

            elif id == 21:#camera zoom
                kwarg = {}
                for property in properties:
                    if property['name'] == 'center':
                        input_string = property['value']
                        kwarg['center'] = [float(i) for i in input_string.split(',')]
                    elif property['name'] == 'rate':
                        kwarg['rate'] = float(property['value'])
                    elif property['name'] == 'scale':
                        kwarg['scale'] = float(property['value'])

                new_zoom = entities.Zoom_col(object_position, self.game_objects, object_size, **kwarg)
                self.game_objects.interactables.add(new_zoom)

            elif id == 23:#shade trigger, to change the screen shade upon trigger
                for property in properties:
                    if property['name'] == 'colour':
                        colour = property['value']

                new_interacable = entities.Shade_trigger(object_position, self.game_objects, object_size, pygame.Color(colour))
                self.references['shade_trigger'] = new_interacable
                self.game_objects.interactables.add(new_interacable)

            elif id  == 25:#light sourde
                prop = {}
                for property in properties:
                    if property['name'] == 'radius':
                        prop['radius'] = float(property['value'])
                    elif property['name'] == 'interact':
                        prop['interact'] = property['value']
                    elif property['name'] == 'colour':
                         colour= list(pygame.Color(property['value']))
                         prop['colour'] = [colour[1]/255,colour[2]/255,colour[3]/255,colour[0]/255]
                    elif property['name'] == 'flicker':
                        prop['flicker'] = property['value']
                    elif property['name'] == 'fade':
                        prop['fade'] = property['value']
                    elif property['name'] == 'pulsting':
                        prop['pulsting'] = property['value']

                ligth_source = entities_parallax.Light_source(object_position, self.game_objects, parallax)
                self.game_objects.lights.add_light(ligth_source, **prop)
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(ligth_source)
                else:
                    self.game_objects.all_bgs.add(ligth_source)

            elif id  == 26:#2D water
                prop = {}
                for property in properties:
                    if property['name'] == 'water_tint':
                        colour= list(pygame.Color(property['value']))
                        prop['water_tint'] = [colour[1]/255,colour[2]/255,colour[3]/255,colour[0]/255]
                    elif property['name'] == 'darker_color':
                        colour= list(pygame.Color(property['value']))
                        prop['darker_color'] = [colour[1]/255,colour[2]/255,colour[3]/255,colour[0]/255]
                    elif property['name'] == 'line_color':
                        colour= list(pygame.Color(property['value']))
                        prop['line_color'] = [colour[1]/255,colour[2]/255,colour[3]/255,colour[0]/255]

                water = entities.TwoD_liquid(object_position, self.game_objects, object_size, **prop)
                self.game_objects.interactables_fg.add(water)#cosmetics

            elif id == 27:#sky
                reflection = entities.Sky(object_position, self.game_objects, parallax, object_size)

                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(reflection)
                else:
                    #if parallax == [1,1]:#need to be in cosmetics if we want to reflect enteties on stage
                     #   self.game_objects.cosmetics.add(reflection)
                    #else:
                    self.game_objects.all_bgs.add(reflection)

            elif id == 34:#reflection object
                reflection = entities.Waterfall(object_position, self.game_objects, parallax, object_size)

                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(reflection)
                else:
                    self.game_objects.all_bgs.add(reflection)

    def load_interactables_objects(self,data,parallax,offset):#load object infront of layers
        chest_int = 1
        soul_essence_int = 1
        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['interactables_firstgid']

            if id == 2:#save point
                new_int = entities.Savepoint(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(new_int)

            elif id == 3:#runestones, colectable
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                state = self.game_objects.world_state.state[self.level_name]['runestone'].get(ID, False)
                new_rune = entities.Runestones(object_position, self.game_objects, state, ID)
                self.game_objects.interactables.add(new_rune)

            elif id == 4:#chests
                state = self.game_objects.world_state.state[self.level_name]['chest'].get(str(chest_int), False)
                new_interacable = entities.Chest(object_position,self.game_objects, state, str(chest_int))
                self.game_objects.interactables.add(new_interacable)
                chest_int += 1

            elif id == 5:#fireplace
                type = 'Fire'#default
                on = False
                for property in properties:
                    if property['name'] == 'type':
                        type = property['value']
                    if property['name'] == 'on':
                        on = property['value']
                new_interacable = getattr(entities, type+'place')
                self.game_objects.interactables.add(new_interacable(object_position, self.game_objects, on))

            elif id == 6:#roadsign
                values={}
                for property in properties:
                    if property['name'] == 'left':
                        values['left'] = property['value']
                    elif property['name'] == 'up':
                        values['up']=property['value']
                    elif property['name'] == 'right':
                        values['right']=property['value']
                    elif property['name'] == 'down':
                        values['down']=property['value']
                new_sign = entities.Sign(object_position,self.game_objects,values)
                self.game_objects.interactables.add(new_sign)

            elif id == 7:#roadsign
                fast_travel = entities.Fast_travel(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(fast_travel)

            elif id == 8:#inorinoki
                inorinoki = entities.Inorinoki(object_position,self.game_objects)
                self.game_objects.interactables.add(inorinoki)

            elif id == 9:#uberstone
                runestone = entities.Uber_runestone(object_position,self.game_objects)
                self.game_objects.interactables.add(runestone)

            elif id == 10:#lever
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                lever = entities.Lever(object_position,self.game_objects, ID)
                self.references['lever'].append(lever)
                self.game_objects.interactables.add(lever)

            elif id == 11:#gate
                kwarg = {}
                for property in properties:
                    if property['name'] == 'ID':
                        kwarg['ID'] = property['value']
                    elif property['name'] == 'erect':
                        kwarg['erect'] = property['value']
                gate = platforms.Gate(object_position,self.game_objects, **kwarg)
                self.references['gate'].append(gate)
                self.game_objects.platforms.add(gate)

            elif id == 12:#challenge monument
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                gate = entities.Challenge_monument(object_position, self.game_objects, ID)
                self.game_objects.interactables.add(gate)

            elif id == 13:#Soul_essence
                if not self.game_objects.world_state.state[self.game_objects.map.level_name]['soul_essence'].get(soul_essence_int, False):#if it has not been interacted with
                    new_loot = entities.Soul_essence(object_position, self.game_objects, soul_essence_int)
                    self.game_objects.loot.add(new_loot)
                soul_essence_int += 1

    @staticmethod
    def blur_value(parallax):#called from load_layers and load_back/front_objects
        return round(1/parallax[0])

    def load_layers(self, data, parallax, offset):
        'Tiled design notes: all tile layers and objects need to be in a group (including statics and other object layers).'
        'The offset and parallax should be specified for group, which affects all in that group. Individual tile layers can be specified as well.'
        'Each group needs at least one tile layer (but can be emppty).'
        'The groups should contain "fg", "bg" in their name.'
        'The tile layer in groups can be called whatever.'
        'recommended convention: bg_#, bg_interact_# or bg_fade_# for the layers  (normal, stiff infront of interactables, e.g. grass, and stuff that fades upon collision with player). It doesnt have to be called bg but needs _fade_# and _interact_# for the spaceial ones'
        'The main group needs to be called "bg1"'#world state file reads it
        'The objects need to be called statics, interactables, front or back.'
        'Each level can have a tmx file called "objects" and be placed in object layer called front or back'

        #make empty surfaces
        key = list(data.keys())[0]
        cols = data[key]['width']#number of columns
        rows = data[key]['height']#number of rows

        blit_surfaces = {}#every layer from tiled
        blit_compress_surfaces = {}#the ones with the same paralax are merged
        animation_list = {}#a place holder for animation objects
        blit_fade_surfaces = {}#fade surfaces that goes away upon collision
        blit_fade_pos = {}#fade surfaces that goes away upon collision

        for tile_layer in data.keys():#make a blank surface
            animation_list[tile_layer] = []
            if 'animated' in tile_layer: continue
            blit_surfaces[tile_layer] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32)#.convert_alpha()
            blit_compress_surfaces[tile_layer[0:tile_layer.rfind('_')]] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32)#.convert_alpha()
            blit_fade_surfaces[tile_layer] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32)#.convert_alpha()
            blit_fade_pos[tile_layer] = []

        #blit the BG sprites to a surface, mapping tile set data to image data. make also the animated objects and save them in dict
        new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]#[-330,-215]
        for tile_layer in data.keys():
            for index, tile_number in enumerate(data[tile_layer]['data']):
                if tile_number == 0: continue
                y = math.floor(index/cols)
                x = (index - (y*cols))

                if 'animated' in tile_layer:#if animation
                    for tileset in self.map_data['tilesets']:
                        if tile_number == tileset['firstgid']:
                            level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _

                            path = 'maps/%s/%s' % (level_name, read_files.get_folder(tileset['image']))
                            blit_pos = (x * self.TILE_SIZE - math.ceil(new_map_diff[0]*(1-parallax[0])) + offset[0] + data[tile_layer]['offsetx'], y * self.TILE_SIZE - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1] + data[tile_layer]['offsety'])
                            new_animation = Entities.BG_Animated(self.game_objects,blit_pos,path,parallax)
                            animation_list[tile_layer].append(new_animation)
                else:#if statics
                    blit_pos = (x * self.TILE_SIZE + data[tile_layer]['offsetx'], y * self.TILE_SIZE + data[tile_layer]['offsety'])
                    blit_surfaces[tile_layer].blit(self.spritesheet_dict[tile_number], blit_pos)
                    blit_fade_pos[tile_layer].append(blit_pos)#for fade layer

        #blit all static sublayers onto one single parallax layer in order as drawn in Tiled. And sort the animations into the key grouops
        animation_entities = {}
        for layer in data.keys():
            bg = layer[0:layer.rfind('_')]#bg2_2 -> bg2
            if 'animated' in layer:#animations
                try:#make a dictionary of list
                    animation_entities[bg].append(animation_list[layer])
                except KeyError:
                    animation_entities[bg] = [animation_list[layer]]
            elif 'fade' in layer:
                blit_fade_surfaces[layer].blit(blit_surfaces[layer], (0,0))
            else:#statics
                blit_compress_surfaces[bg].blit(blit_surfaces[layer], (0,0))

        #add the bg, fg, fade, animations and objects to the group
        for tile_layer in blit_compress_surfaces.keys():
            pos = (-math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0],-math.ceil((1-parallax[1])*new_map_diff[1])+ offset[1])

            if 'fade' in tile_layer:#add fade blocks
                for fade in blit_fade_surfaces.keys():
                    if 'fade' in fade:#is needed
                        bg = entities.BG_Fade(pos, self.game_objects, blit_fade_surfaces[fade],parallax,blit_fade_pos[fade])
                        if self.layer.startswith('bg'): self.game_objects.all_bgs.add(bg)#bg
                        else: self.game_objects.all_fgs.add(bg)
                        self.game_objects.bg_fade.add(bg)

            elif 'interact' in tile_layer:#the stuff that blits in front of interactables, e.g. grass
                self.game_objects.bg_interact.add(entities.BG_Block(pos,self.game_objects,blit_compress_surfaces[tile_layer],parallax, live_blur = self.biome.live_blur))#pos,img,parallax

            elif self.layer.startswith('bg'):#bg
                bg = entities.BG_Block(pos,self.game_objects, blit_compress_surfaces[tile_layer], parallax, live_blur = self.biome.live_blur)
                self.game_objects.all_bgs.add(bg)
                self.game_objects.all_bgs.reference[tuple(parallax)] = bg
            elif self.layer.startswith('fg'):#fg
                self.game_objects.all_fgs.add(entities.BG_Block(pos,self.game_objects,blit_compress_surfaces[tile_layer],parallax, live_blur = self.biome.live_blur))#pos,img,parallax

            if animation_entities.get(tile_layer,False):#add animations
                for bg_animation in animation_entities[tile_layer]:
                    if 'fg' in tile_layer:
                        self.game_objects.all_fgs.add(bg_animation)
                    elif 'bg' in tile_layer:
                        self.game_objects.all_bgs.add(bg_animation)

    def orginise_references(self):#called at the end of the loader
        if self.references.get('shade_trigger',False):
            self.references['shade_trigger'].add_shade_layers(self.references['shade'])

        if self.references.get('lever',False):#assume that the gate-lever is on the same map
            for lever in self.references['lever']:
                for gate in self.references['gate']:
                    if lever.ID_key == gate.ID_key:
                        lever.add_gate(gate)

class Biome():
    def __init__(self, level):
        self.level = level
        self.live_blur = False#default is false live blurring

    def load_objects(self, data, parallax, offset):
        pass

    def set_camera(self):
        pass

    def room(self, room):#called wgen a new room is loaded
        pass

    def clear_biome(self):#called when a new biome is about to load. need to clear the old stuff
        self.level.game_objects.sound.pause_bg_sound()
        self.release_textures()

    def release_textures(self):
        pass

class Village_ola2(Biome):
    def __init__(self, level):
        super().__init__(level)

    def room(self, room):#called wgen a new room is loaded
        if room in ['5']:
            self.live_blur = True

    def load_objects(self,data,parallax,offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 2:
                new_tree = entities_parallax.Thor_mtn(object_position, self.level.game_objects, parallax, self.live_blur)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_tree)
                else:
                    self.level.game_objects.all_bgs.add(new_tree)

            elif id == 1:#boulder
                new_tree = platforms.Boulder(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_tree)                    

class Light_forest(Biome):
    def __init__(self, level):
        super().__init__(level)

    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 2:#light forest tree tree
                new_tree = entities_parallax.Light_forest_tree1(object_position,self.level.game_objects,parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_tree)
                else:
                    self.level.game_objects.all_bgs.add(new_tree)

            elif id == 3:#light forest tree tree
                new_tree = entities_parallax.Light_forest_tree2(object_position,self.level.game_objects,parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_tree)
                else:
                    self.level.game_objects.all_bgs.add(new_tree)

            elif id == 4:#light forest breakable collisio block
                new_plarform = platforms.Breakable_block_1(object_position,self.level.game_objects)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.platforms.add(new_plarform)
                else:
                    self.level.game_objects.platforms.add(new_plarform)

            elif id == 5:#grind
                kwarg = {}
                for property in properties:
                    if property['name'] == 'frequency':
                        kwarg['frequency'] = property['value']
                    elif property['name'] == 'direction':
                        kwarg['direction'] = property['value']
                    elif property['name'] == 'distance':
                        kwarg['distance'] = property['value']
                    elif property['name'] == 'speed':
                        kwarg['speed'] = property['value']

                new_grind = entities.Grind(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_grind)

            elif id == 6:#stone wood
                kwarg = {}
                for property in properties:
                    if property['name'] == 'quest':
                        kwarg['quest'] = property['value']
                    elif property['name'] == 'item':
                        kwarg['item'] = property['value']

                new_stone_wood = entities.Stone_wood(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_stone_wood)

class Light_forest_semi_cave(Biome):
    def __init__(self, level):
        super().__init__(level)

    def room(self, room):#called wgen a new room is loaded
        if room in ['11', '8', '7', '6', '5']:
            self.level.game_objects.lights.ambient = (100/255,100/255,100/255,255/255)
            self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [200/255,200/255,200/255,200/255], interact = False)

    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 5:#cocoon
                if parallax == [1,1]:#if BG1 layer
                    new_cocoon = entities.Cocoon(object_position, self.level.game_objects)
                    self.level.game_objects.interactables.add(new_cocoon)
                else:#if in parallax layers
                    new_cocoon = entities_parallax.Cocoon(object_position, self.level.game_objects, parallax)
                    if self.level.layer.startswith('fg'):
                        self.level.game_objects.all_fgs.add(new_cocoon)
                    else:
                        self.level.game_objects.all_bgs.add(new_cocoon)

            elif id == 8:#cocoon
                new_cocoon = entities.Cocoon_boss(object_position, self.level.game_objects)
                self.level.references['cocoon_boss'] = new_cocoon#save for ater use in encounter
                self.level.game_objects.interactables.add(new_cocoon)

            elif id == 9:#vines
                new_viens = entities_parallax.Vines(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_viens)
                else:
                    self.level.game_objects.all_bgs.add(new_viens)

            elif id == 10:#smalltree 1
                new_viens = entities_parallax.Small_tree1(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_viens)
                else:
                    self.level.game_objects.all_bgs.add(new_viens)

class Rhoutta_encounter(Biome):
    def __init__(self, level):
        super().__init__(level)

    def room(self, room):
        if room == '2':
            self.level.game_objects.lights.ambient = (30/255,30/255,30/255,230/255)#230
            if self.level.game_objects.world_state.events.get('guide', False):#if guide interaction has happened
                self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [200/255,200/255,200/255,200/255],interact = False)

    def set_camera(self):
        if self.level.level_name == 'rhoutta_encounter_1' and self.level.spawn == '1':#if it a new game
            new_state = states.New_game(self.level.game_objects.game)
            new_state.enter_state()

    def load_objects(self,data,parallax,offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 2:#time collision
                types = 'dust'
                for property in properties:
                    if property['name'] == 'particles':
                        types = property['value']

                new_platofrm = platforms.Rhoutta_encounter_1( self.level.game_objects, object_position, types)
                self.level.game_objects.platforms.add(new_platofrm)

class Light_forest_cave(Biome):
    def __init__(self, level):
        super().__init__(level)

    def room(self, room = 1):        
        self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [255/255,255/255,255/255,255/255], normal_interact = False)         
        self.level.game_objects.lights.ambient = (30/255,30/255,30/255,170/255)        

    def load_objects(self,data,parallax,offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 0:#cave grass
                if parallax == [1,1]:#if BG1 layer
                    new_grass = entities.Cave_grass(object_position, self.level.game_objects)
                    self.level.game_objects.interactables.add(new_grass)
                else:#if in parallax layers
                    new_grass = entities_parallax.Cave_grass(object_position, self.level.game_objects, parallax)
                    if self.level.layer.startswith('fg'):
                        self.level.game_objects.all_fgs.add(new_grass)
                    else:
                        self.level.game_objects.all_bgs.add(new_grass)

            elif id == 1:#ljusmaksar
                new_grass = entities_parallax.Ljusmaskar(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_grass)
                else:
                    self.level.game_objects.all_bgs.add(new_grass)

            elif id == 2:#droplet
                if self.level.layer.startswith('fg'):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs
                
                new_drop = entities_parallax.Droplet_source(object_position, self.level.game_objects, parallax, group)
                group.add(new_drop)

            elif id == 3:#falling rock trap
                new_rock = entities_parallax.Falling_rock_source(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_rock)
                else:
                    self.level.game_objects.all_bgs.add(new_rock)

            elif id == 4:#vines
                new_vine = entities_parallax.Vines_1(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(new_vine)
                else:
                    self.level.game_objects.all_bgs.add(new_vine)

            elif id == 5:#bubble source
                prop = {}
                for property in properties:
                    if property['name'] == 'lifetime':
                        prop['lifetime'] = property['value']
                    elif property['name'] == 'state':
                        state = property['value']#horizontal or vertical movement #TODO

                bubble_source = entities.Bubble_source(object_position, self.level.game_objects, platforms.Bubble, **prop)
                self.level.game_objects.interactables.add(bubble_source)

            elif id == 6:#spieks
                spikes = entities.Spikes(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(spikes)

            elif id == 7:#bubble
                prop = {}
                for property in properties:
                    if property['name'] == 'lifetime':
                        prop['lifetime'] = property['value']

                new_bubble = platforms.Bubble_static(object_position, self.level.game_objects, **prop)
                self.level.game_objects.platforms.add(new_bubble)

            elif id == 8:#ball challange
                new_challange = entities.Challenge_ball(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(new_challange)

class Golden_fields(Biome):
    def __init__(self, level):
        super().__init__(level)

    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 2:#bridge that is built when the reindeer dies                                        
                new_bridge = platforms.Bridge(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_bridge)

            elif id == 3:#droplet
                if self.level.layer.startswith('fg'):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs
                
                new_drop = entities_parallax.Droplet_source(object_position, self.level.game_objects, parallax, group)
                group.add(new_drop)
  