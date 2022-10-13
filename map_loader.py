import pygame, csv, Entities, math, Read_files
import constants as C

class Level():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.PLAYER_CENTER = C.player_center
        self.SCREEN_SIZE = C.window_size
        self.TILE_SIZE = C.tile_size
        self.init_player_pos = (0,0)
        self.state = Read_files.read_json("map_state.json") #check this file for structure of object

    def load_map(self,map_name,spawn):
        self.game_objects.game.state_stack[-1].handle_input('exit')#remove any unnormal gameplay states
        self.level_name = map_name
        self.spawn = spawn
        self.parallax_reference_pos = []# reset any reference point
        self.load_map_data()
        self.init_state_file()#make a state file if it is the first time loading this map
        self.load_statics()
        self.load_collision_layer()
        self.load_bg()
        self.append_light_effet()#append any light effects

    def set_weather(self,particle):
        self.game_objects.weather.create_particles(particle)

    def append_light_effet(self):
        if self.level_name == 'light_forest_cave':
            self.game_objects.game.state_stack[-1].handle_input('dark')#make a dark effect gameplay state
        elif self.level_name == 'village_cave':
            self.game_objects.game.state_stack[-1].handle_input('light')#make a light effect gameplay state
        elif self.level_name == 'dark_forest':
            self.game_objects.game.state_stack[-1].handle_input('light')#make a light effect gameplay state

    def load_map_data(self):
        self.map_data = Read_files.read_json("maps/%s/%s.json" % (self.level_name,self.level_name))
        self.map_data = Read_files.format_tiled_json(self.map_data)

        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                self.map_data['statics_firstgid'] = tileset['firstgid']

    def init_state_file(self):
        try:#first time?
            self.state[self.level_name]
        except:#if first time loading a map, prepare a state file
            chest_int = 0
            soul_essence_int = 0
            map_statics = self.map_data["statics"]
            self.state[self.level_name] = {'chest':{},'soul_essence':{}}#a place holder for things that should depend on map state

            for obj in map_statics:
                id = obj['gid'] - self.map_data['statics_firstgid']

                if id == 23:#bushes, chests etc
                    for property in obj['properties']:
                        if property['name'] == 'type':
                            interactable_type = property['value']

                    if interactable_type == 'Chest':
                        self.state[self.level_name]['chest'][str(chest_int)] = 'closed'
                        chest_int += 1

                elif id == 28:#key items: Soul_essence etc.
                    for property in obj['properties']:
                        if property['name'] == 'name':
                            keyitem = property['value']

                    if keyitem == 'Soul_essence':
                        self.state[self.level_name]['soul_essence'][str(soul_essence_int)] = 'available'
                        soul_essence_int += 1

    def read_all_spritesheets(self):
        sprites = {}

        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                continue

            sheet = pygame.image.load("maps/%s/%s" % (self.level_name, tileset['image'])).convert_alpha()
            rows = int(sheet.get_rect().h/self.TILE_SIZE)
            columns = int(sheet.get_rect().w/self.TILE_SIZE)
            n = tileset['firstgid']

            for row in range(rows):
                for column in range(columns):
                    y = row * self.TILE_SIZE
                    x = column * self.TILE_SIZE
                    rect = pygame.Rect(x, y, x + self.TILE_SIZE, y + self.TILE_SIZE)
                    image = pygame.Surface((self.TILE_SIZE,self.TILE_SIZE),pygame.SRCALPHA,32)
                    image.blit(sheet,(0,0),rect)
                    sprites[n] = image
                    n += 1

        return sprites

    def load_bg_music(self):
        return pygame.mixer.Sound("Audio/" + self.level_name + "/default.wav")

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
                new_block = Entities.Spikes(object_position,object_size)
                self.game_objects.platforms.add(new_block)
            #one way collision block (currently on top implemented)
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
                self.game_objects.enemies.add(new_block)

    def load_statics(self):
        chest_int = 0
        soul_essence_int = 0

        map_statics = self.map_data["statics"]

        for obj in map_statics:
            id = obj['gid'] - self.map_data['statics_firstgid']
            object_position = (int(obj['x']),int(obj['y']))
            #player
            if id == 0:
                for property in obj['properties']:
                    if property['name'] == 'spawn':
                        if type(self.spawn).__name__ != 'str':#if respawn
                            self.game_objects.player.set_pos(self.spawn)
                            self.init_player_pos = self.spawn
                        else:#if notmal load
                            if property['value'] == self.spawn:
                                self.game_objects.player.set_pos(object_position)
                                self.init_player_pos = object_position
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

            elif id == 14:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'right')
                self.game_objects.camera_blocks.add(new_camera_stop)
            elif id == 15:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'top')
                self.game_objects.camera_blocks.add(new_camera_stop)
            elif id == 16:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'left')
                self.game_objects.camera_blocks.add(new_camera_stop)
            elif id == 17:
                object_size = (int(obj['width']),int(obj['height']))
                new_camera_stop = Entities.Camera_Stop(object_size, object_position, 'bottom')
                self.game_objects.camera_blocks.add(new_camera_stop)

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

            elif id == 21:#re-spawpoint, save point
                new_int = Entities.Spawnpoint(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(new_int)

            elif id == 22:#Spawner: spawn enemies
                values={}
                for property in obj['properties']:
                    if property['name'] == 'entity':
                        values['entity'] = property['value']
                    elif property['name'] == 'number':
                        values['number']=property['value']
                new_spawn = Entities.Spawner(object_position,self.game_objects,values)
                self.game_objects.cosmetics.add(new_spawn)

            elif id == 23:#bushes, chests etc
                for property in obj['properties']:
                    if property['name'] == 'type':
                        interactable_type = property['value']

                if interactable_type == 'Chest':
                    new_interacable = getattr(Entities, interactable_type)(object_position,self.game_objects,self.state[self.level_name]['chest'][str(chest_int)],str(chest_int))
                    chest_int += 1
                else:
                    new_interacable = getattr(Entities, interactable_type)(object_position,self.game_objects)
                #new_bush = Entities.Interactable_bushes(object_position,self.game_objects,bush_type)
                self.game_objects.interactables.add(new_interacable)

            elif id == 28:#key items: genkidama etc.
                for property in obj['properties']:
                    if property['name'] == 'name':
                        keyitem = property['value']

                if self.state[self.level_name][str(keyitem).lower()][str(soul_essence_int)] == 'available':#if player hasn't picked it up
                    new_keyitem = getattr(Entities, keyitem)(object_position,self.game_objects,str(soul_essence_int))
                    self.game_objects.loot.add(new_keyitem)
                    if keyitem == 'Soul_essence':
                        soul_essence_int += 1

            elif id == 20:#reference point
                self.parallax_reference_pos = object_position

            elif id == 24:#sign
                values={}
                for property in obj['properties']:
                    if property['name'] == 'name':
                        interactable = property['value']

                    #write specefic conditions if thse should spawn
                    if interactable == 'Bridge_block':
                        if self.game_objects.state > 1:#if reindeer hasn't been defeated
                            return

                new_interactable = getattr(Entities, interactable)(object_position,self.game_objects)
                self.game_objects.interactables.add(new_interactable)

            elif id == 25:#sign
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

    def load_bg(self):
    #returns one surface with all backround images blitted onto it, for each bg/fg layer
        base_bg_list = ['bg_behindfar','bg_far','bg_behindmid','bg_mid','bg_behindnear','bg_near','bg_fixed','ground','fg_fixed','fg_near','fg_mid']
        #bg_list = ['bg_farfar','bg_far','bg_midmid','bg_mid','bg_nearnear','bg_near','bg_fixed','fg_fixed','fg_near','fg_mid']
        bg_list = []
        parallax_values = {'bg_behindfar': 0.01,
                            'bg_far': 0.1,
                            'bg_behindmid': 0.4,
                            'bg_mid': 0.5,
                            'bg_behindnear': 0.7,
                            'bg_near': 0.8,
                            'bg_fixed': 1,
                            'ground': 1,
                            'fg_fixed': 1,
                            'fg_near': 1.25,
                            'fg_mid': 1.5}
        animation_list = {}
        top_left = {}
        bg_flags = {}
        blit_dict = {}

        #check for animation and deco layers in map data
        for bg in base_bg_list:
            for layer in list(self.map_data['tile_layers'].keys()):
                if '_animated' in layer:
                    animation_base_layer = layer[:layer.find('_animated')]
                    animation_list[animation_base_layer] = layer
                elif bg in layer:
                    if bg in blit_dict.keys():
                        blit_dict[bg].append(layer)
                    else:
                        blit_dict[bg] = [layer]
                    bg_list.append(layer)

        for bg in bg_list:
            bg_flags[bg] = True

        #all these figures below should be passed and not hardcoded, will break if we change UI etc.
        screen_center = self.PLAYER_CENTER
        try:#if a reference point is provided in tiled
            parallax_reference_pos = [self.parallax_reference_pos[0],self.parallax_reference_pos[1]-32]#where is 32 comming from?
        except:#if a reference point is not provided in tiled
            parallax_reference_pos =  self.init_player_pos

        new_map_diff = (parallax_reference_pos[0] - screen_center[0], parallax_reference_pos[1] - screen_center[1])

        cols = self.map_data['tile_layers'][list(self.map_data['tile_layers'].keys())[0]]['width']
        rows = self.map_data['tile_layers'][list(self.map_data['tile_layers'].keys())[0]]['height']

        blit_surfaces = {}
        for bg in bg_list:
            blit_surfaces[bg] = pygame.Surface((cols*self.TILE_SIZE,rows*self.TILE_SIZE), pygame.SRCALPHA, 32).convert_alpha()

        bg_sheets = {}
        bg_maps = {}

        spritesheet_dict = self.read_all_spritesheets()

        #try loading all parallax backgrounds
        for bg in bg_list:
            try:
                bg_maps[bg] = self.map_data['tile_layers'][bg]['data']
                top_left[bg] = (0,0)
            except:
                bg_flags[bg] = False
                #print("Failed to read %s" % bg)

        #blit background to one image, mapping tile set data to image data
        for bg in bg_list:
            if bg_flags[bg]:
                for index, tile_number in enumerate(bg_maps[bg]):
                    if tile_number == 0:
                        continue
                    else:
                        y = math.floor(index/cols)
                        x = (index - (y*cols))
                        blit_pos = (x * self.TILE_SIZE, y * self.TILE_SIZE)
                        blit_surfaces[bg].blit(spritesheet_dict[tile_number], blit_pos)
                        if top_left[bg] == (0,0):
                            top_left[bg] = blit_pos

        #blit all sublayers onto one single parallax layer in order
        for bg in list(blit_dict.keys()):
            if len(blit_dict[bg]) == 1:
                continue
            blit_dict[bg].sort(reverse = True)
            for i in range(1,len(blit_dict[bg])):
                blit_surfaces[blit_dict[bg][0]].blit(blit_surfaces[blit_dict[bg][i]],(0,0))

        animation_entities = {}
        #create animation layers
        for bg in animation_list.keys():
            for index, tile_number in enumerate(self.map_data['tile_layers'][animation_list[bg]]['data']):
                if tile_number == 0:
                    continue
                else:
                    for tileset in self.map_data['tilesets']:
                        if tile_number == tileset['firstgid']:
                            path = 'maps/%s/%s' % (self.level_name, Read_files.get_folder(tileset['image']))
                            y = math.floor(index/cols)
                            x = (index - (y*cols))
                            parallax = parallax_values[bg]
                            blit_pos = (x * self.TILE_SIZE - math.ceil(new_map_diff[0]*(1-parallax)), y * self.TILE_SIZE - math.ceil((1-parallax)*new_map_diff[1]))
                            new_animation = Entities.BG_Animated(blit_pos,path,parallax)
                            try:
                                animation_entities[bg].append(new_animation)
                            except KeyError:
                                animation_entities[bg] = [new_animation]

        for bg in base_bg_list:
            parallax = parallax_values[bg]

            if bg in blit_dict.keys():
                if 'fg' in bg:
                    self.game_objects.all_fgs.add(Entities.BG_Block((math.ceil((1-parallax)*new_map_diff[0]),math.ceil((1-parallax)*new_map_diff[1])),blit_surfaces[blit_dict[bg][0]],parallax))
                elif bg =='ground':#the small grass stuff that should go in front of interactables
                        self.game_objects.bg_ground.add(Entities.BG_Block(pos,blit_surfaces[blit_dict[bg][0]],parallax))#pos,img,parallax
                else:
                    pos=(-math.ceil((1-parallax)*new_map_diff[0]),-math.ceil((1-parallax)*new_map_diff[1]))
                    self.game_objects.all_bgs.add(Entities.BG_Block(pos,blit_surfaces[blit_dict[bg][0]],parallax))#pos,img,parallax
            try:
                for bg_animation in animation_entities[bg]:
                    self.game_objects.all_bgs.add(bg_animation)
            except KeyError:
                pass
        del blit_surfaces, bg_sheets, bg_maps
