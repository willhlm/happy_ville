import pygame, csv, math
import Entities, Read_files, weather, entities_parallax, states, platforms
import constants as C

#from PIL import Image, ImageFilter#for blurring
#import numpy as np#for blurring

class Level():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.PLAYER_CENTER = C.player_center
        self.TILE_SIZE = C.tile_size
        self.level_name = ''
        self.area_name = ''
        self.area_change = True#a flag to chenge if we change area

    def load_map(self,map_name,spawn):
        self.references = {'shade':[],'gate':[],'lever':[]}#to save some stuff so that it can be organisesed later in case e.g. some things needs to be loaded in order: needs to be cleaned after each map loading
        self.game_objects.game.state_stack[-1].handle_input('exit')#remove any unnormal gameplay states, e.g. cultist encountr, pause gameplay etc
        self.level_name = map_name.lower()
        self.spawn = spawn
        self.check_pause_sound()#pause the sound if we change area
        self.load_map_data()#load the map data
        self.init_state_file()#need to be before load groups
        self.load_groups()
        self.map_specifics()#append any light effects depending on map
        self.orginise_references()

    def check_pause_sound(self):
        self.area_change = self.level_name[:self.level_name.rfind('_')] != self.area_name
        if self.area_change:
            self.game_objects.sound.pause_bg_sound()

    def init_state_file(self):
        if not self.game_objects.world_state.state.get(self.level_name, False):#if it is the first time loading the map
            self.game_objects.world_state.init_state_file(self.level_name,self.map_data)

    def map_specifics(self):
        self.game_objects.camera.reset_player_center()
        level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _
        if level_name == 'light_forest_cave':
            self.screen = Entities.Dark_screen(self.game_objects)#makes the screen dark
            self.game_objects.cosmetics.add(self.screen)#need to be added before Dark glow on player
            self.game_objects.cosmetics.add(Entities.Dark_glow(self.game_objects.player))
        elif level_name == 'village_cave':
            self.game_objects.cosmetics.add(Entities.Light_glow(self.game_objects.player))#add a light glow around the player
        elif level_name == 'dark_forest':
            self.game_objects.cosmetics.add(Entities.Light_glow(self.game_objects.player))#add a light glow around the player
        elif self.level_name == 'rhoutta_encounter_1':#if it is a new game file
            if self.spawn != '1': return
            new_state = states.New_game(self.game_objects.game)
            new_state.enter_state()
            self.game_objects.camera.true_scroll = [self.game_objects.player.true_pos[0] - self.game_objects.camera.center[0], self.game_objects.player.true_pos[1] - self.game_objects.camera.center[1]]#-self.game_objects.player.rect[2]*0.5,-self.game_objects.player.rect[3]*0.5 if there was a camera stopp

    def load_map_data(self):
        level_name = self.level_name[:self.level_name.rfind('_')]#get the name up to last _
        self.area_name = level_name

        map_data = Read_files.read_json("maps/%s/%s.json" % (level_name,self.level_name))
        self.map_data = Read_files.format_tiled_json_group(map_data)

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
        load_front_objects = {'rhoutta_encounter_front':self.load_rhoutta_encounter_objects,'light_forest_front':self.load_light_forest_objects,'light_forest_cave_front':self.load_light_forest_cave_objects,'interactables':self.load_interactables_objects,'statics':self.load_statics}#the keys are the naes of the object in tiled
        load_back_objects = {'rhoutta_encounter_back':self.load_rhoutta_encounter_objects,'light_forest_back':self.load_light_forest_objects,'light_forest_cave_back':self.load_light_forest_cave_objects}#the keys are the naes of the object in tiled
        self.game_objects.all_bgs.reference = {}#to store the reference positions of each static bg layer or other information

        for group in self.map_data['groups']:
            parallax = [self.map_data['groups'][group]['parallaxx'], self.map_data['groups'][group]['parallaxy']]
            offset = [self.map_data['groups'][group]['offsetx'], self.map_data['groups'][group]['offsety']]

            if 'bg' in group: self.layer = 'bg'
            elif 'fg' in group: self.layer = 'fg'
            elif 'interact' in group: self.layer = 'interact'

            self.load_objects(self.map_data['groups'][group]['objects'],parallax,offset,load_back_objects)#objects behind layers
            self.load_layers(self.map_data['groups'][group]['layers'],parallax,offset)
            self.load_objects(self.map_data['groups'][group]['objects'],parallax,offset,load_front_objects)#object infron of layers

    def load_objects(self,data,parallax,offset,method):
        for object in method.keys():#load each object in group
            if data.get(object[object.rfind('_')+1:],False):
                if object[object.rfind('_')+1:] == 'back' or object[object.rfind('_')+1:] == 'front':#map specifics
                    if object[:object.rfind('_')] != self.level_name[:self.level_name.rfind('_')]: continue#check if it macthes the map
                    key = self.level_name[:self.level_name.rfind('_')+1] + object[object.rfind('_')+1:]#make sure to only load the rellavant map
                else:#statics and interactables
                    key = object
                method[key](data[object[object.rfind('_')+1:]],parallax,offset)

    def load_statics(self,data,parallax,offset):#load statics and collision
        chest_int = 1
        soul_essence_int = 1

        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1] - object_size[1]]
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
                new_npc = getattr(Entities, npc_name)
                self.game_objects.npcs.add(new_npc(object_position,self.game_objects))

            elif id == 2:#enemies
                for property in properties:
                    if property['name'] == 'class':
                        enemy_name = property['value']
                new_enemy = getattr(Entities, enemy_name)
                self.game_objects.enemies.add(new_enemy(object_position, self.game_objects))

            elif id == 4:#Spawner: spawn enemies
                values={}
                for property in properties:
                    if property['name'] == 'class':
                        values['entity'] = property['value']
                    elif property['name'] == 'number':
                        values['number']=property['value']
                new_spawn = Entities.Spawner(object_position,self.game_objects,values)
                self.game_objects.cosmetics.add(new_spawn)

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

                new_path = Entities.Path_inter(object_position,self.game_objects,object_size,destination,spawn,image,sfx)
                self.game_objects.interactables.add(new_path)

            elif id == 10:
                for property in properties:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    if property['name'] == 'spawn':
                        spawn = property['value']
                new_path = Entities.Path_col(object_position,self.game_objects,object_size,destination,spawn)
                self.game_objects.interactables.add(new_path)

            elif id == 11:#one way collision block (currently only top implemented)
                for property in properties:
                    if property['name'] == 'particles':
                        types = property['value']
                new_block = platforms.Collision_oneway_up(object_position,object_size,types)
                self.game_objects.platforms.add(new_block)

            elif id == 13:#breakable collision block
                for property in properties:
                    if property['name'] == 'sprite':
                        types = property['value']
                new_block = Entities.Collision_breakable(object_position,self.game_objects,types)
                self.game_objects.interactables.add(new_block)

            elif id == 14:#camera stop
                camera_offset = 0
                for property in properties:
                    if property['name'] == 'direction':
                        values = property['value']
                    if property['name'] == 'offset':
                        camera_offset = property['value']
                new_camera_stop = Entities.Camera_Stop(self.game_objects, object_size, object_position, values, camera_offset)
                self.game_objects.camera_blocks.add(new_camera_stop)

            elif id == 15:#bg_particles -> circles, rain etc
                for property in properties:
                    if property['name'] == 'particle':
                        particle_type = property['value']
                if self.layer == 'fg':
                    self.game_objects.weather.create_particles(particle_type,parallax,self.game_objects.all_fgs)
                else:
                    self.game_objects.weather.create_particles(particle_type,parallax,self.game_objects.all_bgs)

            elif id == 16:#scren shade
                for property in properties:
                    if property['name'] == 'colour':
                        colour = property['value']

                new_shade = Entities.Shade_Screen(self.game_objects,parallax,pygame.Color(colour))
                self.references['shade'].append(new_shade)
                if self.layer == 'fg':
                    self.game_objects.all_fgs.add(new_shade)
                else:
                    self.game_objects.all_bgs.add(new_shade)

            #elif id == 17:#leaves
            #    information = [object_position,object_size]
            #    if self.layer == 'fg':
            #        entities_parallax.create_leaves(information,parallax,self.game_objects.all_fgs)
            #    else:
            #        entities_parallax.create_leaves(information,parallax,self.game_objects.all_bgs)

            elif id == 19:#trigger
                values={}
                for property in properties:
                    if property['name'] == 'event':
                        values['event'] = property['value']
                    elif property['name'] == 'event_type':
                        values['event_type']=property['value']

                if values['event_type'] == 'cutscene':
                    new_trigger = Entities.Cutscene_trigger(object_position,self.game_objects,object_size ,values['event'])
                    self.game_objects.interactables.add(new_trigger)

            elif id == 20:#reflection object
                for property in properties:
                    if property['name'] == 'direction':
                        dir = property['value']
                dir = 'up'
                reflection = Entities.Reflection(object_position, object_size, dir, self.game_objects)
                self.game_objects.reflections.add(reflection)

            elif id == 23:#shade trigger
                for property in properties:
                    if property['name'] == 'colour':
                        colour = property['value']

                new_interacable = Entities.Shade_trigger(object_position,self.game_objects,object_size,pygame.Color(colour))
                self.references['shade_trigger'] = new_interacable
                self.game_objects.interactables.add(new_interacable)

            #move to interactables objects
            elif id == 24:#event: e.g. bridge that is built when the reindeer dies
                values={}
                for property in properties:
                    if property['name'] == 'name':
                        interactable = property['value']

                    #write specefic conditions if thse should spawn
                    if interactable == 'Bridge':
                        if self.game_objects.world_state.progress > 1:#if reindeer has been defeated
                            new_interactable = getattr(Entities, interactable)(object_position,self.game_objects)
                            self.game_objects.interactables.add(new_interactable)

            elif id == 28:#key items: soul_essence etc.
                for property in properties:
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

            elif id == 30:#trapsª
                for property in properties:
                    if property['name'] == 'type':
                        trap_type = property['value']

                object_size = [int(obj['width']),int(obj['height'])]
                new_trap = getattr(Entities, trap_type)(object_position,self.game_objects,object_size)
                self.game_objects.interactables.add(new_trap)

    def load_interactables_objects(self,data,parallax,offset):#load object infront of layers
        chest_int = 1
        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['interactables_firstgid']

            if id == 2:#save point
                new_int = Entities.Savepoint(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(new_int)

            elif id == 3:#runestones, colectable
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                new_rune = Entities.Runestones(object_position,self.game_objects,self.game_objects.world_state.state[self.level_name]['runestone'][ID],ID)
                self.game_objects.interactables.add(new_rune)

            elif id == 4:#chests
                new_interacable = Entities.Chest(object_position,self.game_objects,self.game_objects.world_state.state[self.level_name]['chest'][str(chest_int)],str(chest_int))
                self.game_objects.interactables.add(new_interacable)
                chest_int += 1

            elif id == 5:#fireplace
                new_interacable = Entities.Fireplace(object_position,self.game_objects)
                self.game_objects.interactables.add(new_interacable)

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
                new_sign = Entities.Sign(object_position,self.game_objects,values)
                self.game_objects.interactables.add(new_sign)

            elif id == 7:#roadsign
                fast_travel = Entities.Fast_travel(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(fast_travel)

            elif id == 8:#inorinoki
                inorinoki = Entities.Inorinoki(object_position,self.game_objects)
                self.game_objects.interactables.add(inorinoki)

            elif id == 9:#uberstone
                runestone = Entities.Uber_runestone(object_position,self.game_objects)
                self.game_objects.interactables.add(runestone)

            elif id == 10:#lever
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                lever = Entities.Lever(object_position,self.game_objects, self.game_objects.world_state.state[self.level_name]['lever'][str(ID)], ID)
                self.references['lever'].append(lever)
                self.game_objects.interactables.add(lever)

            elif id == 11:#gate
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                gate = platforms.Gate(object_position,self.game_objects,ID)
                self.references['gate'].append(gate)
                self.game_objects.platforms.add(gate)

    def load_light_forest_objects(self,data,parallax,offset):#load objects back of layers
        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['objects_firstgid']

            if id == 2:#light forest tree tree
                new_tree = entities_parallax.Light_forest_tree1(object_position,self.game_objects,parallax)
                if self.layer == 'fg':
                    self.game_objects.all_fgs.add(new_tree)
                else:
                    self.game_objects.all_bgs.add(new_tree)

            elif id == 3:#light forest tree tree
                new_tree = entities_parallax.Light_forest_tree2(object_position,self.game_objects,parallax)
                if self.layer == 'fg':
                    self.game_objects.all_fgs.add(new_tree)
                else:
                    self.game_objects.all_bgs.add(new_tree)

            elif id == 4:#light forest breakable collisio block
                new_plarform = platforms.Breakable_block_1(object_position,self.game_objects)
                if self.layer == 'fg':
                    self.game_objects.platforms.add(new_plarform)
                else:
                    self.game_objects.platforms.add(new_plarform)

    def load_light_forest_cave_objects(self,data,parallax,offset):
        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['objects_firstgid']

            if id == 0:#cave grass
                if parallax == [1,1]:#if BG1 layer
                    new_grass = Entities.Cave_grass(object_position, self.game_objects)
                    self.game_objects.interactables.add(new_grass)
                else:#if in parallax layers
                    new_grass = entities_parallax.Cave_grass(object_position, self.game_objects, parallax)
                    if self.layer == 'fg':
                        self.game_objects.all_fgs.add(new_grass)
                    else:
                        self.game_objects.all_bgs.add(new_grass)

            elif id == 1:#ljusmaksar
                new_grass = entities_parallax.Ljusmaskar(object_position, self.game_objects, parallax)
                if self.layer == 'fg':
                    self.game_objects.all_fgs.add(new_grass)
                else:
                    self.game_objects.all_bgs.add(new_grass)

            elif id == 2:#droplet
                new_drop = entities_parallax.Droplet_source(object_position, self.game_objects, parallax)
                if self.layer == 'fg':
                    self.game_objects.all_fgs.add(new_drop)
                else:
                    self.game_objects.all_bgs.add(new_drop)

            elif id == 3:#falling rock trap
                new_rock = entities_parallax.Falling_rock_source(object_position, self.game_objects, parallax)
                if self.layer == 'fg':
                    self.game_objects.all_fgs.add(new_rock)
                else:
                    self.game_objects.all_bgs.add(new_rock)

    def load_rhoutta_encounter_objects(self,data,parallax,offset):
        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['objects_firstgid']

            if id == 2:#time collision
                types = 'dust'
                for property in properties:
                    if property['name'] == 'particles':
                        types = property['value']

                new_platofrm = platforms.Rhoutta_encounter_1( self.game_objects, object_position,object_size,types)
                self.game_objects.platforms.add(new_platofrm)

    @staticmethod
    def blur_value(parallax):#called from load_layers and load_back/front_objects
        return round(1/parallax[0])

    def load_layers(self,data, parallax, offset):
        'Tiled design notes: all tile layers and objects need to be in a group (including statics and other object layers).'
        'The offset and parallax should be specified for group, which affects all in that group. Individual tile layers can be specified as well.'
        'Each group needs at least one tile layer (but can be emppty).'
        'The groups should contain "fg", "bg" in their name.'
        'The tile layer in groups can be called whatever.'
        'recommended convention: bg_#, bg_interact_# or bg_fade_# for the layers. It doesnt have to be called bg but needs _fade_# and _interact_# for the spaceual ones'
        'The main layer needs to be called "bg1"'#world state file reads it
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

                            path = 'maps/%s/%s' % (level_name, Read_files.get_folder(tileset['image']))
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

        #blurring
        # strFormat = 'RGBA'
        # for layer in blit_compress_surfaces.keys():
        #     if parallax[0] == 1: continue
        #     blur_value = self.blur_value(parallax)
        #
        #     #surface to pil
        #     surface = blit_compress_surfaces[layer]
        #     raw_str = pygame.image.tobytes(surface, strFormat)
        #     image = Image.frombytes(strFormat, surface.get_size(), raw_str)
        #
        #     #blurImage = image.filter(ImageFilter.BoxBlur(blur_value))
        #     blurImage = image.filter(ImageFilter.GaussianBlur(blur_value))
        #
        #     #remove black border
        #     blurImage = np.array(blurImage)
        #     for i in range(3):
        #         blurImage[:,:,i] = np.divide(blurImage[:,:,i],blurImage[:,:,3].astype('int16')+1)*256
        #     blurImage =  Image.fromarray(blurImage.astype('uint8'), 'RGBA')
        #
        #     #pil to surface
        #     blit_compress_surfaces[layer] = pygame.image.fromstring(blurImage.tobytes(), blurImage.size, blurImage.mode)

        blur_value = self.blur_value(parallax)
        for layer in blit_compress_surfaces.keys():
            if parallax[0] == 1: break
            blit_compress_surfaces[layer] = pygame.transform.gaussian_blur(blit_compress_surfaces[layer], blur_value,repeat_edge_pixels=True)#box_blur

        #add the bg, fg, fade, animations and objects to the group
        for tile_layer in blit_compress_surfaces.keys():
            pos = (-math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0],-math.ceil((1-parallax[1])*new_map_diff[1])+ offset[1])

            if 'fade' in tile_layer:#add fade blocks
                for fade in blit_fade_surfaces.keys():
                    if 'fade' in fade:#is needed
                        bg = Entities.BG_Fade(pos,blit_fade_surfaces[fade],parallax,blit_fade_pos[fade])
                        if self.layer == 'bg':self.game_objects.all_bgs.add(bg)#bg
                        else: self.game_objects.all_fgs.add(bg)
                        self.game_objects.bg_fade.add(bg)
            elif 'interact' in tile_layer:#the stuff that blits in front of interactables, e.g. grass
                self.game_objects.bg_interact.add(Entities.BG_Block(pos,blit_compress_surfaces[tile_layer],parallax))#pos,img,parallax

            elif self.layer == 'bg':#bg
                bg = Entities.BG_Block(pos,blit_compress_surfaces[tile_layer],parallax)#pos,img,parallax
                self.game_objects.all_bgs.add(bg)
                self.game_objects.all_bgs.reference[tuple(parallax)] = bg
            elif self.layer == 'fg':#fg
                self.game_objects.all_fgs.add(Entities.BG_Block(pos,blit_compress_surfaces[tile_layer],parallax))#pos,img,parallax

            if animation_entities.get(tile_layer,False):#add animations
                for bg_animation in animation_entities[tile_layer]:
                    if 'fg' in tile_layer:
                        self.game_objects.all_fgs.add(bg_animation)
                    elif 'bg' in tile_layer:
                        self.game_objects.all_bgs.add(bg_animation)

    def orginise_references(self):
        if self.references.get('shade_trigger',False):
            self.references['shade_trigger'].add_shade_layers(self.references['shade'])

        if self.references.get('lever',False):#assume that the gate-lever is on the same map
            for lever in self.references['lever']:
                for gate in self.references['gate']:
                    if lever.ID_key == gate.ID_key:
                        lever.add_gate(gate)
