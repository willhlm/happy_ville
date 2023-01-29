import pygame, csv, Entities, math, Read_files, weather
import constants as C

class Level():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.PLAYER_CENTER = C.player_center
        self.TILE_SIZE = C.tile_size
        self.level_name = ''
        self.area_name = ''
        self.area_change = True#a flag to chenge if we change area

    def load_map(self,map_name,spawn):
        self.game_objects.game.state_stack[-1].handle_input('exit')#remove any unnormal gameplay states, e.g. light effect
        self.level_name = map_name
        self.spawn = spawn
        self.check_pause_sound()#pause the sound if we change area
        self.load_map_data()#load the map data
        self.init_state_file()#need to be before load statics
        self.load_statics()
        self.load_collision_layer()
        self.load_bgs()
        self.append_light_effet()#append any light effects

    def check_pause_sound(self):
        self.area_change = self.level_name[:self.level_name.rfind('_')] != self.area_name
        if self.area_change:
            self.game_objects.sound.pause_bg_sound()

    def init_state_file(self):
        try:
            self.game_objects.world_state.state[self.level_name]
        except:#make a state file if it is the first time loading this map
            self.game_objects.world_state.init_state_file(self.level_name,self.map_data)

    def append_light_effet(self):
        level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _
        if level_name == 'light_forest_cave':
            self.game_objects.game.state_stack[-1].handle_input('dark')#make a dark effect gameplay state
        elif level_name == 'village_cave':
            self.game_objects.game.state_stack[-1].handle_input('light')#make a light effect gameplay state
        elif level_name == 'dark_forest':
            self.game_objects.game.state_stack[-1].handle_input('light')#make a light effect gameplay state

    def load_map_data(self):
        level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _
        self.area_name = level_name

        self.map_data = Read_files.read_json("maps/%s/%s.json" % (level_name,self.level_name))
        self.map_data = Read_files.format_tiled_json(self.map_data)        

        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if 'static' in tileset['source']:
                    self.map_data['statics_firstgid'] =  tileset['firstgid']
                elif 'interactables' in tileset['source']:
                    self.map_data['interactables_firstgid'] = tileset['firstgid']

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

    def load_collision_layer(self):#load the whole map
        map_collisions = self.map_data["collision"]

        def convert_points_to_list(points):
            points_list = []
            for point in points:
                points_list.append((point['x'],point['y']))
            return points_list

        for obj in map_collisions:

            object_position = (int(obj['x']),int(obj['y']))
            object_size = (int(obj['width']),int(obj['height']))

            #check for polygon type first
            if 'polygon' in obj.keys():
                new_block = Entities.Collision_right_angle(object_position, convert_points_to_list(obj['polygon']))
                self.game_objects.platforms_ramps.add(new_block)
                continue

            id = obj['gid'] - self.map_data['statics_firstgid']
            #normal collision blocks
            if id == 7:
                try:
                    for property in obj['properties']:
                        if property['name'] == 'particles':
                            type = property['value']
                    new_block = Entities.Collision_block(object_position,object_size,type)
                except:
                    new_block = Entities.Collision_block(object_position,object_size)
                self.game_objects.platforms.add(new_block)
            #spike collision blocks
            elif id == 8:
                new_block = Entities.Collision_dmg(object_position,object_size)
                self.game_objects.platforms.add(new_block)
            #one way collision block (currently only top implemented)
            elif id == 11:
                try:
                    for property in obj['properties']:
                        if property['name'] == 'particles':
                            type = property['value']
                    new_block = Entities.Collision_oneway_up(object_position,object_size,type)
                except:
                    new_block = Entities.Collision_oneway_up(object_position,object_size)
                self.game_objects.platforms.add(new_block)

            elif id == 13:#breakable collision block
                for property in obj['properties']:
                    if property['name'] == 'sprite':
                        type = property['value']

                new_block = Entities.Collision_breakable(object_position,self.game_objects,type)
                self.game_objects.interactables.add(new_block)

    def load_statics(self):
        chest_int = 1
        soul_essence_int = 1

        map_statics = self.map_data["statics"]

        for obj in map_statics:
            id = obj['gid'] - self.map_data['statics_firstgid']
            object_position = (int(obj['x']),int(obj['y']))
            #player
            if id == 0:
                for property in obj['properties']:
                    if property['name'] == 'spawn':
                        if type(self.spawn).__name__ != 'str':#if respawn/fast tarvel
                            self.game_objects.player.set_pos(self.spawn)
                        else:#if notmal load
                            if property['value'] == self.spawn:
                                self.game_objects.player.set_pos(object_position)
            #npcs
            elif id == 1:
                properties = obj['properties']
                for property in properties:
                    if property['name'] == 'class':
                        npc_name = property['value']
                new_npc = getattr(Entities, npc_name)
                self.game_objects.npcs.add(new_npc(object_position,self.game_objects))

            #enemies
            elif id == 2:
                properties = obj['properties']
                for property in properties:
                    if property['name'] == 'class':
                        enemy_name = property['value']
                new_enemy = getattr(Entities, enemy_name)
                self.game_objects.enemies.add(new_enemy(object_position, self.game_objects))

            elif id == 4:#Spawner: spawn enemies
                values={}
                for property in obj['properties']:
                    if property['name'] == 'entity':
                        values['entity'] = property['value']
                    elif property['name'] == 'number':
                        values['number']=property['value']
                new_spawn = Entities.Spawner(object_position,self.game_objects,values)
                self.game_objects.cosmetics.add(new_spawn)

            elif id == 9:
                object_size = (int(obj['width']),int(obj['height']))
                for property in obj['properties']:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    if property['name'] == 'spawn':
                        spawn = property['value']
                    if property['name'] == 'image':
                        image = property['value']
                new_path = Entities.Path_inter(object_position,self.game_objects,object_size,destination,spawn,image)
                self.game_objects.interactables.add(new_path)

            elif id == 10:
                object_size = (int(obj['width']),int(obj['height']))
                for property in obj['properties']:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    if property['name'] == 'spawn':
                        spawn = property['value']
                new_path = Entities.Path_col(object_position,self.game_objects,object_size,destination,spawn)
                self.game_objects.interactables.add(new_path)

            elif id == 14:#camera stop
                for property in obj['properties']:
                    if property['name'] == 'direction':
                        values = property['value']

                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(self.game_objects, object_size, object_position, values)
                self.game_objects.camera_blocks.add(new_camera_stop)

            elif id == 15:#bg_particles
                self.particles = {}
                for property in obj['properties']:
                    if property['name'] == 'particle':
                        particle_type = property['value']
                    elif property['name'] == 'layers':
                        layers = property['value'].split(",")

                for layer in layers:
                    self.particles[layer] = particle_type

            elif id == 16:#bg_particles
                for property in obj['properties']:
                    if property['name'] == 'colour':
                        colour = property['value']

                self.fog_colour = pygame.Color(colour)

            elif id == 19:#trigger
                values={}
                object_size = (int(obj['width']),int(obj['height']))

                for property in obj['properties']:
                    if property['name'] == 'event':
                        values['event'] = property['value']
                    elif property['name'] == 'event_type':
                        values['event_type']=property['value']

                if values['event_type'] == 'cutscene':
                    new_trigger = Entities.Cutscene_trigger(object_position,self.game_objects,object_size ,values['event'])
                    self.game_objects.interactables.add(new_trigger)

            #reflection object
            elif id == 20:
                object_size = (int(obj['width']),int(obj['height']))
                try:
                    for property in obj['properties']:
                        if property['name'] == 'direction':
                            dir = property['value']
                except:
                    pass
                dir = 'up'
                reflection = Entities.Reflection(object_position, object_size, dir, self.game_objects)
                self.game_objects.reflections.add(reflection)

            elif id == 21:#re-spawpoint, save point
                new_int = Entities.Savepoint(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(new_int)

            elif id == 22:#runestones, colectable
                for property in obj['properties']:
                    if property['name'] == 'ID':
                        ID = property['value']

                new_rune = Entities.Runestones(object_position,self.game_objects,self.game_objects.world_state.state[self.level_name]['runestone'][ID],ID)
                self.game_objects.interactables.add(new_rune)

            elif id == 23:#bushes, chests etc
                for property in obj['properties']:
                    if property['name'] == 'type':
                        interactable_type = property['value']

                if interactable_type == 'Chest':
                    new_interacable = getattr(Entities, interactable_type)(object_position,self.game_objects,self.game_objects.world_state.state[self.level_name]['chest'][str(chest_int)],str(chest_int))
                    chest_int += 1
                else:
                    new_interacable = getattr(Entities, interactable_type)(object_position,self.game_objects)
                #new_bush = Entities.Interactable_bushes(object_position,self.game_objects,bush_type)
                self.game_objects.interactables.add(new_interacable)

            elif id == 24:#event: e.g. bridge that is built when the reindeer dies
                values={}
                for property in obj['properties']:
                    if property['name'] == 'name':
                        interactable = property['value']

                    #write specefic conditions if thse should spawn
                    if interactable == 'Bridge':
                        if self.game_objects.world_state.progress > 1:#if reindeer has been defeated
                            new_interactable = getattr(Entities, interactable)(object_position,self.game_objects)
                            self.game_objects.interactables.add(new_interactable)

            elif id == 25:#roadsign
                values={}
                for property in obj['properties']:
                    if property['name'] == 'left':
                        values['left'] = property['value']
                    elif property['name'] == 'up':
                        values['up']=property['value']
                    elif property['name'] == 'right':
                        values['right']=property['value']
                    elif property['name'] == 'down':
                        values['down']=property['value']
                new_sign = Entities.Sign(object_position,self.game_objects,values)
                self.game_objects.interactables.add(new_sign)

            elif id == 26:#uberstone
                runestone = Entities.Uber_runestone(object_position,self.game_objects)
                self.game_objects.interactables.add(runestone)

            elif id == 27:#inorinoki
                inorinoki = Entities.Inorinoki(object_position,self.game_objects)
                self.game_objects.interactables.add(inorinoki)

            elif id == 28:#key items: soul_essence etc.
                for property in obj['properties']:
                    if property['name'] == 'name':
                        keyitem = property['value']

                if keyitem == 'Soul_essence':
                    if self.game_objects.world_state.state[self.level_name][str(keyitem).lower()][str(soul_essence_int)] == 'idle':#if player hasn't picked it up
                        new_keyitem = getattr(Entities, keyitem)(object_position,self.game_objects,str(soul_essence_int))
                        self.game_objects.loot.add(new_keyitem)
                        soul_essence_int += 1
                elif keyitem == 'Spiritorb':
                        new_keyitem = getattr(Entities, keyitem)(object_position,self.game_objects)
                        self.game_objects.loot.add(new_keyitem)

            elif id == 29:#key items: soul_essence etc.
                fast_travel = Entities.Fast_travel(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(fast_travel)

    def load_bgs(self):
        'tiled design notes: all sublayers in bg1_X (x specifies the sublayer) should have the same paralax and offset.'
        'The animated layer, bg1_animatedX, need to have at least one "normal" layer of bg1_1 (which can be emppty).'
        'The particle/weather effect also need to have at least one "normal" layer of bg1_1'

        #sort the data
        bg_list = {}#a place hodler for tiled data
        animation_list = {}#a place holder for animation objects
        for tile_layer in self.map_data['tile_layers'].keys():
            animation_list[tile_layer] = []
            parallax = []
            try:#save parallax x value
                parallax.append(self.map_data['tile_layers'][tile_layer]['parallaxx'])
            except:#save parallax x value
                parallax.append(1)
            try:#save parallax y value
                parallax.append(self.map_data['tile_layers'][tile_layer]['parallaxy'])
            except:#save parallax y value
                parallax.append(1)
            bg_list[tile_layer] = {'parallax':parallax}

            try:#save offset value
                bg_list[tile_layer].update({'offset':(self.map_data['tile_layers'][tile_layer]['offsetx'],self.map_data['tile_layers'][tile_layer]['offsety'])})
            except:#save offset value
                bg_list[tile_layer].update({'offset':(0,0)})

            bg_list[tile_layer].update({'data':(self.map_data['tile_layers'][tile_layer]['data'])})
            #bg_list[tile_layer].update({'reference_point':(self.map_data['tile_layers'][tile_layer]['x'],self.map_data['tile_layers'][tile_layer]['y'])})#not used

        #make empty surfaces
        cols = self.map_data['tile_layers'][list(self.map_data['tile_layers'].keys())[0]]['width']#number of columns
        rows = self.map_data['tile_layers'][list(self.map_data['tile_layers'].keys())[0]]['height']#number of rows

        blit_surfaces = {}#every layer from tiled
        blit_compress_surfaces = {}#the ones with the same paralax are merged
        for tile_layer in bg_list.keys():#make a blank surface
            if not 'animated' in tile_layer:
                blit_surfaces[tile_layer] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32).convert_alpha()
                blit_compress_surfaces[tile_layer[0:tile_layer.find('_')]] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32).convert_alpha()

        #blit the BG sprites to a surface, mapping tile set data to image data. make also the animated objects and save them in dict
        spritesheet_dict = self.read_all_spritesheets()#read the bg spritesheats
        new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]#[-330,-215]
        for tile_layer in bg_list.keys():
            for index, tile_number in enumerate(bg_list[tile_layer]['data']):
                if tile_number == 0:
                    continue
                y = math.floor(index/cols)
                x = (index - (y*cols))

                if 'animated' in tile_layer:#if animation
                    for tileset in self.map_data['tilesets']:
                        if tile_number == tileset['firstgid']:
                            level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _

                            path = 'maps/%s/%s' % (level_name, Read_files.get_folder(tileset['image']))
                            parallax = bg_list[tile_layer]['parallax']
                            blit_pos = (x * self.TILE_SIZE - math.ceil(new_map_diff[0]*(1-parallax[0])) + bg_list[tile_layer]['offset'][0], y * self.TILE_SIZE - math.ceil((1-parallax[1])*new_map_diff[1])+bg_list[tile_layer]['offset'][1])
                            new_animation = Entities.BG_Animated(self.game_objects,blit_pos,path,parallax)
                            animation_list[tile_layer].append(new_animation)
                else:#if statics
                    blit_pos = (x * self.TILE_SIZE , y * self.TILE_SIZE)
                    blit_surfaces[tile_layer].blit(spritesheet_dict[tile_number], blit_pos)

        #blit all static sublayers onto one single parallax layer in order as drawn in Tiled. And sort the animations into the key grouops
        parallax = {}
        offset = {}
        animation_entities = {}
        for layer in bg_list.keys():
            bg = layer[0:layer.find('_')]#bg2_2 -> bg2
            if 'animated' in layer:#animations
                try:#make a dictionary of list
                    animation_entities[bg].append(animation_list[layer])
                except KeyError:
                    animation_entities[bg] = [animation_list[layer]]
            else:#statics
                blit_compress_surfaces[bg].blit(blit_surfaces[layer], (0,0))
                parallax[bg] = bg_list[layer]['parallax']
                offset[bg] = bg_list[layer]['offset']

        #add the bg, fg and animations to the group
        for tile_layer in blit_compress_surfaces.keys():

            if 'fg' in tile_layer:
                pos=(-math.ceil((1-parallax[tile_layer][0])*new_map_diff[0]) + offset[tile_layer][0],-math.ceil((1-parallax[tile_layer][1])*new_map_diff[1])+ offset[tile_layer][1])
                self.game_objects.all_fgs.add(Entities.BG_Block(pos,blit_compress_surfaces[tile_layer],parallax[tile_layer]))#pos,img,parallax
            elif 'interact' in tile_layer:#the stuff that blits in front of interactables
                pos=(-math.ceil((1 - parallax[tile_layer][0])*new_map_diff[0]) + offset[tile_layer][0],-math.ceil((1-parallax[tile_layer][1])*new_map_diff[1])+ offset[tile_layer][1])
                self.game_objects.bg_interact.add(Entities.BG_Block(pos,blit_compress_surfaces[tile_layer],parallax[tile_layer]))#pos,img,parallax
            elif 'bg' in tile_layer:#bg
                pos=(-math.ceil((1-parallax[tile_layer][0])*new_map_diff[0]) + offset[tile_layer][0],-math.ceil((1-parallax[tile_layer][1])*new_map_diff[1])+ offset[tile_layer][1])
                self.game_objects.all_bgs.add(Entities.BG_Block(pos,blit_compress_surfaces[tile_layer],parallax[tile_layer]))#pos,img,parallax

            try:
                #add fog to BG
                if tile_layer != 'bg1':
                    self.game_objects.weather.fog(self.game_objects.all_bgs,parallax[tile_layer],self.fog_colour)
            except:
                pass

            try:#add animations to group
                for bg_animation in animation_entities[tile_layer]:
                    if 'fg' in tile_layer:
                        self.game_objects.all_fgs.add(bg_animation)
                    elif 'bg' in tile_layer:
                        self.game_objects.all_bgs.add(bg_animation)
            except:
                pass

            try:#add particles inbetween layers
                if 'fg' in tile_layer:
                    self.game_objects.weather.create_particles(self.particles[tile_layer],parallax[tile_layer],self.game_objects.all_fgs)
                elif 'bg' in tile_layer:
                    self.game_objects.weather.create_particles(self.particles[tile_layer],parallax[tile_layer],self.game_objects.all_bgs)
            except:
                pass

        self.particles={}#reset particles
        self.fog_colour = []#reset fog
