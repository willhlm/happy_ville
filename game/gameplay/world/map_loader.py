import pygame, math, sys

from engine.system import event_triggers, groups
from gameplay.entities.visuals.particles import screen_particles
from engine.utils import read_files
from engine import constants as C
from gameplay.world.weather import weather
from gameplay.world.wrapping_manager import WrappingManager
from gameplay.entities.items import SoulEssence
from gameplay.world.camera.stop import Stop

from gameplay.entities.interactables import *
from gameplay.entities.platforms import *
from gameplay.entities.visuals.environments import *
from engine.utils import functions

class Level():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.PLAYER_CENTER = [game_objects.game.window_size[0] * 0.5, game_objects.game.window_size[1] * 0.5]
        self.TILE_SIZE = C.tile_size
        self.level_name = ''
        self.biome_name = ''
        self.area_change = True#a flag to chenge if we change area/biome
        self.biome = Biome(self)

    def load_map(self, map_name, spawn):
        self.game_objects.game.screen_manager.clear_screens()
        self.game_objects.player.shader_state.handle_input('idle')#reset any shaders that might be on        
        self.references = {'shade':[], 'gate':[], 'lever':[], 'platforms':[], 'bg_fade': []}#to save some stuff so that it can be organisesed later in case e.g. some things needs to be loaded in order: needs to be cleaned after each map loading
        self.spawned = False#a flag so that we only spawn alia once
        self.level_name = map_name.lower()#biom_room
        self.spawn = spawn
        self.game_objects.lights.new_map()#set ambient default light and clear light sources
        self.check_biome()#pause the sound if we change area
        self.load_map_data()#load the map data
        self.init_state_file()#need to be before load groups
        self.load_groups()
        self.set_camera()
        self.orginise_references()

    def set_camera(self):
        self.game_objects.camera_manager.camera.reset_player_center()##need to be after load_group -> normal position
        self.biome.set_camera()#need to be after load_group  -> biome specific camera

    def check_biome(self):
        self.area_change = self.level_name[:self.level_name.rfind('_')] != self.biome_name
        if self.area_change:#new biome
            self.biome_name = self.level_name[:self.level_name.rfind('_')]
            self.biome.clear_biome()
            self.biome = getattr(sys.modules[__name__], self.biome_name.capitalize(), Biome)(self)#returns Biome (default) if there is no biome class
        room = self.level_name[self.level_name.rfind('_') + 1 :]
        self.biome.room(room)

    def init_state_file(self):
        if not self.game_objects.world_state.state.get(self.level_name, False):#if it is the first time loading the room
            self.game_objects.world_state.init_state_file(self.level_name)

    def load_map_data(self):
        level_name = self.level_name[:self.level_name.rfind('_')]        
        map_data = read_files.read_json("assets/maps/%s/%s.json" % (level_name,self.level_name))
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
            sheet = pygame.image.load("assets/maps/%s/%s" % (level_name, tileset['image'])).convert_alpha()
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

        for group in self.map_data['groups']:          
            parallax = [self.map_data['groups'][group]['parallaxx'], self.map_data['groups'][group]['parallaxy']]
            offset = [self.map_data['groups'][group]['offsetx'], self.map_data['groups'][group]['offsety']]

            self.game_objects.game.screen_manager.register_screen(group, parallax)#make a screen for eahcl ayer in tiled
            if group.startswith('bg'):
                self.game_objects.all_bgs.new_group(group, groups.LayeredUpdates())#make a new pygame group for each layer in tiled
                #self.game_objects.all_bgs.append(groups.Group_BG())#make a new pygame group for each layer in tiled                
                #self.game_objects.all_bgs[-1].reference = {}#to store the reference positions of each static bg layer or other information
            else:#fg
                self.game_objects.all_fgs.new_group(group, groups.LayeredUpdates())#make a new pygame group for each layer in tiled
                #self.game_objects.all_fgs.append(groups.Group_BG())#make a new pygame group for each layer in tiled
            self.layer = group#name of the folder in tiled

            self.load_objects(self.map_data['groups'][group]['objects'],parallax,offset,'back')#objects behind layers
            self.load_layers(self.map_data['groups'][group]['layers'],parallax,offset)
            self.load_objects(self.map_data['groups'][group]['objects'],parallax,offset,'front')#object infron of layers
            self.congigure_weather(group, parallax)#do this at the end so that it getis into the front of layers
            self.post_process(group, parallax)

    def post_process(self, group, parallax):
        self.biome.post_process(group, parallax)

    def congigure_weather(self, group, parallax):
        self.biome.congigure_weather(group, parallax)

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
                new_block = CollisionRightAngle(object_position, points_list,fall_through)
                self.game_objects.platforms_ramps.add(new_block)
                continue

            id = obj['gid'] - self.map_data['statics_firstgid']
            if id == 0:  # Player
                if self.spawned: continue#skip if player has already spawned
                for property in properties:
                    if property['name'] == 'spawn':#determine spawn type and set position accordingly
                        if isinstance(self.spawn, str):# Normal load case
                            if property['value'] != self.spawn:
                                continue

                            self.game_objects.player.set_pos(object_position)
                        else:#coordinate-based spawn
                            self.game_objects.player.set_pos(self.spawn)

                        self.game_objects.player.reset_movement()
                        self.spawned = True#mark as spawned to avoid re-entry
                        for prop in properties:#handle spawn movement based on direction property
                            if prop['name'] == 'right':
                                self.game_objects.player.dir[0] = 1
                                self.game_objects.player.acceleration[0] = C.acceleration[0]
                            elif prop['name'] == 'left':
                                self.game_objects.player.dir[0] = -1
                                self.game_objects.player.acceleration[0] = C.acceleration[0]
                            if prop['name'] == 'up':
                                self.game_objects.player.velocity[1] = C.jump_vel_player
                            elif prop['name'] == 'down':
                                pass

            elif id == 1:#npcs
                for property in properties:
                    if property['name'] == 'class':
                        npc_name = property['value']

                new_npc = self.game_objects.registry.fetch('npcs', npc_name)(object_position, self.game_objects)
                self.game_objects.npcs.add(new_npc)

            elif id == 2:#enemies
                for property in properties:
                    if property['name'] == 'class':
                        enemy_name = property['value']

                new_enemy = self.game_objects.registry.fetch('enemies', enemy_name)(object_position, self.game_objects)
                self.game_objects.enemies.add(new_enemy)

            elif id == 4:#pass
                pass

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
                new_block = CollisionBlock(object_position,object_size,types)
                self.game_objects.platforms.add(new_block)

            elif id == 8:#spike collision blocks
                new_block = CollisionDamage(object_position,object_size)
                self.game_objects.platforms.add(new_block)

            elif id == 9:
                for property in properties:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    elif property['name'] == 'spawn':
                        spawn = property['value']
                    elif property['name'] == 'image':
                        image = property['value']

                new_path = PathInteract(object_position,self.game_objects, object_size, destination, spawn, image)
                self.game_objects.interactables.add(new_path)

            elif id == 10:
                for property in properties:
                    if property['name'] == 'path_to':
                        destination = property['value']
                    if property['name'] == 'spawn':
                        spawn = property['value']
                new_path = PathCollision(object_position,self.game_objects,object_size,destination,spawn)                        
                self.game_objects.interactables.add(new_path)

            elif id == 11:#one way collision block (currently only top implemented)
                for property in properties:
                    if property['name'] == 'particles':
                        types = property['value']
                new_block = CollisionOnewayUp(object_position,object_size,types)
                self.game_objects.platforms.add(new_block)

            elif id == 12:#hole, if aila collides, aila will move to safe_spawn position
                new_block = Hole(object_position, self.game_objects, object_size)                
                self.game_objects.interactables.add(new_block)

            elif id == 13:#spawn position
                spawn_pos = [object_position[0] + object_size[0]*0.5, object_position[1] + object_size[1]*0.5]
                for property in properties:
                    if property['name'] == 'position':
                        pos = property['value']
                        string_list = pos.split(",")
                        spawn_pos = [int(item) for item in string_list]
                
                new_block = SafeSpawn(object_position, self.game_objects, object_size, spawn_pos)
                self.game_objects.interactables.add(new_block)

            elif id == 14:#camera stop
                camera_offset = 0
                for property in properties:
                    if property['name'] == 'direction':
                        values = property['value']
                    if property['name'] == 'offset':
                        camera_offset = property['value']
                new_camera_stop = Stop(self.game_objects, object_size, object_position, values, camera_offset)
                self.game_objects.camera_blocks.add(new_camera_stop)

            elif id == 15:#bg_particles -> circles, etc
                for property in properties:
                    if property['name'] == 'particle':
                        particle_type = property['value']

                new_shader_screen = getattr(screen_particles, particle_type)                
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(self.layer, new_shader_screen(self.game_objects, parallax, 20))
                else:
                    self.game_objects.all_bgs.add(self.layer, new_shader_screen(self.game_objects, parallax, 20))

            elif id == 16:
                print(object_position)

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

                god_rays = GodRays(object_position, self.game_objects, parallax, object_size, **prop)
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(self.layer,god_rays)
                else:
                    self.game_objects.all_bgs.add(self.layer,god_rays)

            elif id == 19:#trigger
                kwarg = {}
                for property in properties:
                    if property['name'] == 'event':
                        kwarg['event'] = property['value']
                    elif property['name'] == 'new_state':
                        kwarg['new_state'] = property['value']

                if self.game_objects.world_state.cutscenes_complete.get(kwarg['event'], False): continue#if the cutscene has been shown before, return.
                if self.game_objects.world_state.events.get(kwarg['event'], False): continue#if event has already been done
                
                new_trigger = getattr(event_triggers, kwarg['event'].capitalize(), event_triggers.Event_trigger)(object_position, self.game_objects, object_size, **kwarg)#returns Event_trigger (default) if there is no Event_trigger class
                self.game_objects.interactables.add(new_trigger)

            elif id == 20:#reflection object
                prop = {}
                for property in properties:
                    if property['name'] == 'offset':
                        prop['offset'] = property['value']
                    elif property['name'] == 'speed':
                        prop['speed'] = property['value']
                    elif property['name'] == 'texture_parallax':
                        prop['texture_parallax'] = property['value']              
                    elif property['name'] == 'water_texture_on':
                        prop['water_texture_on'] = property['value']                                      

                reflection = River(object_position, self.game_objects, parallax, object_size, self.layer, **prop)

                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(self.layer,reflection)
                else:
                    self.game_objects.all_bgs.add(self.layer,reflection)

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
                
                new_zoom = ZoomCollision(object_position, self.game_objects, object_size, **kwarg)
                self.game_objects.interactables.add(new_zoom)

            elif id == 23:#shade trigger, to change the screen shade upon trigger
                for property in properties:
                    if property['name'] == 'colour':
                        colour = property['value']
                
                new_interacable = ShadeTrigger(object_position, self.game_objects, object_size, pygame.Color(colour))
                self.references['shade_trigger'] = new_interacable
                self.game_objects.interactables.add(new_interacable)

            elif id == 24:#deadth fog
                new_fog = DeathFog(object_position, self.game_objects, object_size)
                self.game_objects.cosmetics.add(new_fog)

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
                prop['parallax'] = parallax

                ligth_source = LightSource(object_position, self.game_objects, parallax, self.layer)
                self.game_objects.lights.add_light(ligth_source, **prop)
                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(self.layer,ligth_source)
                else:
                    self.game_objects.all_bgs.add(self.layer,ligth_source)

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

                water = TwoDLiquid(object_position, self.game_objects, object_size, self.layer, **prop)
                self.game_objects.interactables_fg.add(water)#cosmetics

            elif id == 27:#sky
                sky = Sky(object_position, self.game_objects, parallax, object_size)

                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(self.layer,sky)
                else:
                    #if parallax == [1,1]:#need to be in cosmetics if we want to reflect enteties on stage
                     #   self.game_objects.cosmetics.add(sky)
                    #else:
                    self.game_objects.all_bgs.add(self.layer,sky)

            elif id == 28:#shadow light platform
                platform = ShadowLight_1(object_position, self.game_objects, object_size)
                self.game_objects.cosmetics.add(platform)

            elif id == 31:#rainbow
                explosion = Rainbow(object_position, self.game_objects, object_size, parallax)
                self.game_objects.all_bgs.add(self.layer,explosion)

            elif id == 32:#smoke
                prop = {}
                for property in properties:
                    if property['name'] == 'colour':
                        colour= list(pygame.Color(property['value']))
                        prop['colour'] = [colour[1]/255,colour[2]/255,colour[3]/255,colour[0]/255]
                    elif property['name'] == 'spawn_rate':
                        prop['spawn_rate'] = property['value']
                    elif property['name'] == 'radius':
                        prop['radius'] = property['value']
                    elif property['name'] == 'speed':
                        prop['speed'] = property['value']
                    elif property['name'] == 'horizontalSpread':
                        prop['horizontalSpread'] = property['value']
                    elif property['name'] == 'lifetime':
                        prop['lifetime'] = property['value']
                    elif property['name'] == 'spawn_position':
                        if property['value']:
                            string = property['value'].strip('()')  # Remove parentheses
                            prop['spawn_position'] = [float(x) for x in string.split(',')]

                smoke = Smoke(object_position, self.game_objects, object_size, **prop)
                self.game_objects.cosmetics.add(smoke)

            elif id == 33:#upsteam
                prop = {}
                up, down, left, right = 0, 0, 0, 0
                for property in properties:
                    if property['name'] == 'up':
                        up = -int(property['value'])
                    elif property['name'] == 'down':
                        down = int(property['value'])
                    elif property['name'] == 'left':
                        left = -int(property['value'])
                    elif property['name'] == 'right':
                        right = int(property['value'])

                prop['vertical'] = up + down
                prop['horizontal'] = left + right
                upstream = UpStream(object_position, self.game_objects, object_size, **prop)
                self.game_objects.interactables_fg.add(upstream)

            elif id == 34:#waterfall object
                waterfall = Waterfall(object_position, self.game_objects, parallax, object_size, self.layer)

                if self.layer.startswith('fg'):
                    self.game_objects.all_fgs.add(self.layer,waterfall)
                else:
                    self.game_objects.all_bgs.add(self.layer,waterfall)

    def load_interactables_objects(self,data,parallax,offset):#load object infront of layers
        loot_container, soul_essence_int = 1, 1

        for obj in data['objects']:
            new_map_diff = [-self.PLAYER_CENTER[0],-self.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['interactables_firstgid']

            if id == 2:#save point
                #new_int = SavePoint(object_position,self.game_objects,self.level_name)  
                new_int = AbilityBall(object_position,self.game_objects)     

                self.game_objects.interactables.add(new_int)

            elif id == 3:#runestones, colectable
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                state = self.game_objects.world_state.state[self.level_name]['runestone'].get(ID, False)
                new_rune = Runestones(object_position, self.game_objects, state, ID)
                self.game_objects.interactables.add(new_rune)

            elif id == 4:#chests
                state = self.game_objects.world_state.state[self.level_name]['loot_container'].get(str(loot_container), False)
                new_interacable = Chest(object_position,self.game_objects, state, str(loot_container))
                self.game_objects.interactables.add(new_interacable)
                loot_container += 1

            elif id == 5:#fireplace
                on = False
                for property in properties:
                    if property['name'] == 'type':
                        type = property['value']
                    if property['name'] == 'on':
                        on = property['value']
                new_interacable =Fireplace(object_position, self.game_objects, on)
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
                new_sign = Sign(object_position,self.game_objects,values)
                self.game_objects.interactables.add(new_sign)

            elif id == 7:#roadsign
                fast_travel = FastTravel(object_position,self.game_objects,self.level_name)
                self.game_objects.interactables.add(fast_travel)

            elif id == 8:#inorinoki
                inorinoki = Inorinoki(object_position,self.game_objects)
                self.game_objects.interactables.add(inorinoki)

            elif id == 9:#uberstone
                runestone = UberRunestone(object_position,self.game_objects)
                self.game_objects.interactables.add(runestone)

            elif id == 10:#lever
                kwarg = {}
                for property in properties:                    
                    if property['name'] == 'ID':
                        kwarg['ID'] = property['value']
                    elif property['name'] == 'on':
                        kwarg['on'] = property['value']
                
                lever = Lever(object_position,self.game_objects, **kwarg)
                self.references['lever'].append(lever)
                self.game_objects.interactables.add(lever)

            elif id == 11:#gate
                kwarg = {}
                for property in properties:
                    if property['name'] == 'ID':
                        kwarg['ID'] = property['value']
                    elif property['name'] == 'erect':
                        kwarg['erect'] = property['value']
                gate = Gate_1(object_position,self.game_objects, **kwarg)
                self.references['gate'].append(gate)
                self.game_objects.platforms.add(gate)

            elif id == 12:#challenge monument
                for property in properties:
                    if property['name'] == 'ID':
                        ID = property['value']
                statue = QuestStatue(object_position, self.game_objects, ID)
                self.game_objects.interactables.add(statue)

            elif id == 13:#Soul_essence
                if not self.game_objects.world_state.state[self.game_objects.map.level_name]['soul_essence'].get(soul_essence_int, False):#if it has not been interacted with
                    new_loot = SoulEssence(object_position, self.game_objects, soul_essence_int)
                    self.game_objects.loot.add(new_loot)
                soul_essence_int += 1

            elif id == 14:#interactable_item
                for property in properties:
                    if property['name'] == 'interactable_item':
                        name = property['value']
                if not self.game_objects.world_state.state[self.game_objects.map.level_name]['interactable_items'].get(name, False):#if it has not been interacted with: (assume only one interactable)
                    obj = self.game_objects.registry.fetch('items', name)(object_position, self.game_objects, state = 'wild')      
                    self.game_objects.loot.add(obj)

            elif id == 15:#gate
                kwarg = {}
                for property in properties:
                    if property['name'] == 'ID':
                        kwarg['ID'] = property['value']
                    elif property['name'] == 'erect':
                        kwarg['erect'] = property['value']
                gate = Gate_2(object_position,self.game_objects, **kwarg)
                self.references['gate'].append(gate)
                self.game_objects.platforms.add(gate)

            elif id == 16:#air dash statue
                statue = AirDashStatue(object_position, self.game_objects)
                self.game_objects.interactables.add(statue)

            elif id == 17:#thunder dive statue
                statue = ThunderDiveStatue(object_position, self.game_objects)
                self.game_objects.interactables.add(statue)

            elif id == 18:
                state = self.game_objects.world_state.state[self.level_name]['loot_container'].get(str(loot_container), False)
                amber_rock = AmberRock(object_position, self.game_objects, state, str(loot_container))
                self.game_objects.interactables.add(amber_rock)
                loot_container += 1

            elif id == 19:#collision block that can only brak with charge flag on projectile
                platform = BreakableBlockCharge_1(object_position, self.game_objects)
                self.game_objects.platforms.add(platform)

    def load_layers(self, data, parallax, offset):
        'Tiled design notes: all tile layers and objects need to be in a group (including statics and other object layers).'
        'The offset and parallax should be specified for group, which affects all in that group. Individual tile layers can be specified as well.'
        'Each group needs at least one tile layer (but can be emppty).'
        'The groups should contain "fg", "bg" in their name.'
        'The tile layer in groups can be called whatever.'
        'recommended convention: bg_#, bg_interact_# or bg_fade_# for the layers  (normal, stiff infront of interactables, e.g. grass, and stuff that fades upon collision with player). It doesnt have to be called bg but needs _fade_# and _interact_# for the spaceial ones'
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
                            new_animation = BgAnimated(self.game_objects,blit_pos,path,parallax)
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
                        bg = BgFade(pos, self.game_objects, blit_fade_surfaces[fade], parallax, blit_fade_pos[fade], data[fade]['id'])                        
                        if self.layer.startswith('bg'): self.game_objects.all_bgs.add(self.layer,bg)#bg
                        else: self.game_objects.all_fgs.add(self.layer,bg)
                        self.game_objects.bg_fade.add(bg)
                        self.references['bg_fade'].append(bg)

            elif 'interact' in tile_layer:#the stuff that blits in front of interactables, e.g. grass
                self.game_objects.bg_interact.add(BgBlock(pos,self.game_objects,blit_compress_surfaces[tile_layer],parallax, live_blur = self.biome.live_blur))#pos,img,parallax

            elif self.layer.startswith('bg'):#bg
                bg = BgBlock(pos,self.game_objects, blit_compress_surfaces[tile_layer], parallax, live_blur = self.biome.live_blur)
                self.game_objects.all_bgs.add(self.layer, bg)
            elif self.layer.startswith('fg'):#fg
                self.game_objects.all_fgs.add(self.layer, BgBlock(pos,self.game_objects,blit_compress_surfaces[tile_layer],parallax, live_blur = self.biome.live_blur))#pos,img,parallax

            if animation_entities.get(tile_layer, False):#add animations
                for bg_animation in animation_entities[tile_layer]:
                    if 'fg' in tile_layer:
                        self.game_objects.all_fgs.add(self.layer,bg_animation)
                    elif 'bg' in tile_layer:
                        self.game_objects.all_bgs.add(self.layer,bg_animation)

    def orginise_references(self):#called at the end of the loader
        if self.references.get('shade_trigger',False):
            self.references['shade_trigger'].add_shade_layers(self.references['shade'])

        for lever in self.references['lever']:#assume that the gate/platform - lever is on the same map
            for gate in self.references['gate']:#conenct gates to a lever
                if lever.ID_key == gate.ID_key:
                    lever.add_reference(gate)

            for platform in self.references['platforms']:#connect a platform to a lever
                if lever.ID_key == platform.ID_key:
                    lever.add_reference(platform)

        for i, bg_fade in enumerate(self.references['bg_fade']):#combines the bg_fades
            for j in range(i + 1, len(self.references['bg_fade'])):
                if bg_fade.hitbox.colliderect(self.references['bg_fade'][j].hitbox):
                    bg_fade.add_child(self.references['bg_fade'][j])
                    self.references['bg_fade'][j].add_child(bg_fade)

class Biome():
    def __init__(self, level):
        self.level = level
        self.live_blur = False#default is false live blurring
        self.play_music()
        self.weather_config = {}
        self._weather_registry = {
            "wind": {
                "manager": self.level.game_objects.weather.wind,
                "fx_class": "WindFX",
            },
            "rain": {
                "manager": self.level.game_objects.weather.rain,
                "fx_class": "RainFX",
            },
            "fog": {
                "manager": self.level.game_objects.weather.fog,
                "fx_class": "FogFX",
            },
            "snow": {
                "manager": self.level.game_objects.weather.snow,
                "fx_class": "SnowFX",
            },            
        }

    def congigure_weather(self, group, parallax):        
        for weather_type in self.weather_config.keys():#wind, rain, for etc.
            if self.weather_config[weather_type]['layers'].get(group, False):   
                kwarg = self.weather_config[weather_type]['layers'][group]                 
                new_weather = getattr(weather, self._weather_registry[weather_type]['fx_class'])(self.level.game_objects, parallax = parallax, **kwarg)
                
                self._weather_registry[weather_type]['manager'].add_fx(new_weather)
                if group.startswith('fg'):
                    self.level.game_objects.all_fgs.add(group, new_weather)
                else:
                    self.level.game_objects.all_bgs.add(group, new_weather)        

    def load_objects(self, data, parallax, offset):
        pass

    def set_camera(self):
        pass

    def room(self, room):#called wgen a new room is loaded -> before load objects or configure weather
        pass
    
    def post_process(self, layer_name, parallax):
        radius = functions.blur_radius(parallax)
        self.level.game_objects.game.screen_manager.append_shader('Blur_fast', [layer_name], radius = radius)   
        if layer_name == 'bg1':     
            self.level.game_objects.game.screen_manager.append_shader('Blur_fast', ['player'], radius = radius)   
            self.level.game_objects.game.screen_manager.append_shader('Blur_fast', ['player_fg'], radius = radius)   

    def play_music(self):
        try:#try laoding bg music
            sound = read_files.load_single_sfx("audio/music/maps/" + self.level.biome_name + "/default.mp3" )
            self.level.game_objects.sound.play_background_sound(sound, index = 0, loop = -1, fade = 700, volume = 1.0)
        except FileNotFoundError:
            print("No BG music found")

    def clear_biome(self):#called when a new biome is about to load. need to clear the old stuff
        self.level.game_objects.sound.fade_all_music(fade_time = 2000)
        self.release_textures()

    def release_textures(self):
        pass

class Village(Biome):
    def __init__(self, level):
        super().__init__(level)

    def post_process(self, layer_name, parallax):#called at the end of group loading
        if self.live_blur:
            if parallax[0] == 1: 
                 radius = 0.01
            else:                
                radius = functions.blur_radius(parallax)
            self.level.game_objects.game.screen_manager.append_shader('Blur', [layer_name], radius = radius)   
            if layer_name == 'bg1':     
                self.level.game_objects.game.screen_manager.append_shader('Blur', ['player'], radius = radius)   
                self.level.game_objects.game.screen_manager.append_shader('Blur', ['player_fg'], radius = radius)   

    def room(self, room):#called wgen a new room is loaded
        if room in ['5']:
            self.live_blur = True            

    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 0:
                thor_mtn = ThorMountain(object_position, self.level.game_objects, parallax, self.level.layer, self.live_blur)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,thor_mtn)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,thor_mtn)

            elif id == 1:#boulder
                new_tree = Boulder(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_tree)

            elif id == 2:# locked door
                kwarg = {}
                for property in properties:
                    if property['name'] == 'ID':
                        kwarg['ID'] = property['value']
                    elif property['name'] == 'erect':
                        kwarg['erect'] = property['value']
                    elif property['name'] == 'key':
                        kwarg['key'] = property['value']
                door = DoorRightOrient(object_position, self.level.game_objects, **kwarg)
                door_i = DoorInteract(object_position, self.level.game_objects, door)
                self.level.game_objects.platforms.add(door)
                self.level.game_objects.interactables.add(door_i)
                #self.references['gate'].append(door)

class Nordveden(Biome):
    def __init__(self, level):
        super().__init__(level)
        self.weather_config = {
            "wind": {                                
                "layers": {
                    "bg1": {"velocity": [-2, 0.1], "duration_range": [3000, 7000] },
                    "bg2": {"velocity": [-2, 0.1], "duration_range": [3000, 7000] },
                    "bg3": {"velocity": [-2, 0.1], "duration_range": [3000, 7000] }
                }
            },
            "rain": {
                "layers": {
                    "bg1": { "number_particles": 20}
                }
            },
            "fog": {
                "layers": {
                    "bg1": { "intensity": 0.5, 'colour': (1,1,1,1) },
                    "bg2": { "intensity": 1.0, 'colour': (1,1,1,1) },
                    "bg3": { "intensity": 0.3, 'colour': (1,1,1,1) },
                    "bg4": { "intensity": 0.5, 'colour': (1,1,1,1) },
                    "bg5": { "intensity": 1.0, 'colour': (1,1,1,1) }
                }
            }
        }           

    def play_music(self):
        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/environments/ambient/nordveden/')
        self.level.game_objects.sound.play_background_sound(sounds['idle'][0], index = 1, loop = -1, fade = 1000, volume = 0.2)

    def room(self, room):#called wgen a new room is loaded
        return
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

            if id == 2:#light forest tree tree
                new_tree = NordvedenTree_1(object_position, self.level.game_objects, parallax, self.level.layer)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_tree)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_tree)

            elif id == 3:#light forest tree tree
                new_tree = NordvedenTree_2(object_position, self.level.game_objects, parallax, self.level.layer)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_tree)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_tree)

            elif id == 4:#light forest breakable collisio block
                new_plarform = BreakableBlock_1(object_position,self.level.game_objects)
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

                new_grind = Grind(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_grind)

            elif id == 6:#stone wood
                kwarg = {}
                for property in properties:
                    if property['name'] == 'quest':
                        kwarg['quest'] = property['value']
                    elif property['name'] == 'item':
                        kwarg['item'] = property['value']

                new_stone_wood = StoneWood(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_stone_wood)

            elif id == 7:#cocoon
                if parallax == [1,1]:#if BG1 layer
                    new_cocoon = InteractableCocoon(object_position, self.level.game_objects)
                    self.level.game_objects.interactables.add(new_cocoon)
                else:#if in parallax layers
                    new_cocoon = BackgroundCocoon(object_position, self.level.game_objects, parallax)
                    if self.level.layer.startswith('fg'):
                        self.level.game_objects.all_fgs.add(self.level.layer,new_cocoon)
                    else:
                        self.level.game_objects.all_bgs.add(self.level.layer,new_cocoon)

            elif id == 8:#cocoon
                new_boss = self.level.game_objects.registry.fetch('enemies', 'cocoon_boss')(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(new_boss)

            elif id == 9:#one side brakable
                for property in properties:
                    if property['name'] == 'ID':
                        ID_key = property['value']

                if not self.level.game_objects.world_state.state[self.level.level_name]['breakable_platform'].get(str(ID_key), False):
                    platform = BreakableOnesideLeft(object_position, self.level.game_objects, str(ID_key), 'assets/sprites/entitites/platforms/breakable/nordveden/type2/')
                    self.level.game_objects.platforms.add(platform)

            elif id == 10:#dissapera when standing on it
                for property in properties:
                    if property['name'] == 'ID':
                        ID_key = property['value']

                if not self.level.game_objects.world_state.state[self.level.level_name]['breakable_platform'].get(str(ID_key), False):
                    platform = Nordveden_1(object_position, self.level.game_objects, str(ID_key))
                    self.level.game_objects.platforms.add(platform)  

            elif id == 11:#one side brakable
                for property in properties:
                    if property['name'] == 'ID':
                        ID_key = property['value']

                if not self.level.game_objects.world_state.state[self.level.level_name]['breakable_platform'].get(str(ID_key), False):
                    platform = BreakableOnesideRight(object_position, self.level.game_objects, str(ID_key), 'assets/sprites/entities/platforms/breakable/nordveden/type3/')
                    self.level.game_objects.platforms.add(platform)                                                           

class Rhoutta_encounter(Biome):
    def __init__(self, level):
        super().__init__(level)  
        self.weather_config = {
            "wind": {                                
                "layers": {
                    "bg1": {"velocity": [-2, 0.1], "duration_range": [3000, 7000] },
                    "bg2": {"velocity": [-2, 0.1], "duration_range": [3000, 7000] },
                    "bg3": {"velocity": [-2, 0.1], "duration_range": [3000, 7000] }
                }
            },
            "rain": {
                "layers": {
                    "bg1": { "number_particles": 20}
                }
            },
            "fog": {
                "layers": {
                    "bg1": { "intensity": 0.5, 'colour': (0,0,0,1) },
                    "bg2": { "intensity": 1.0, 'colour': (0,0,0,1) },
                    "bg3": { "intensity": 0.3, 'colour': (0,0,0,1) },
                    "bg4": { "intensity": 0.5, 'colour': (0,0,0,1) },
                    "bg5": { "intensity": 1.0, 'colour': (0,0,0,1) }
                }
            }
        }      

    def room(self, room):
        if room == '2':
            self.level.game_objects.lights.ambient = (30/255,30/255,30/255,230/255)#230
            if self.level.game_objects.world_state.events.get('guide', False):#if guide interaction has happened
                self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [200/255,200/255,200/255,200/255],interact = False)

    def set_camera(self):
        if self.level.level_name == 'rhoutta_encounter_1' and self.level.spawn == '1':#if it a new game
            self.level.game_objects.game.state_manager.enter_state('start_game')

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

                new_platofrm = RhouttaEncounter_1( self.level.game_objects, object_position, types)
                self.level.game_objects.platforms.add(new_platofrm)

class Hlifblom(Biome):
    def __init__(self, level):
        super().__init__(level)

    def play_music(self):
        super().play_music()
        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/environments/ambient/light_forest_cave/')
        #self.level.game_objects.sound.play_background_sound(sounds['idle'][0], index = 1, loop = -1, fade = 1000, volume = 0.1)

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
                    new_grass = InteractableCaveGrass(object_position, self.level.game_objects)
                    self.level.game_objects.interactables.add(new_grass)
                else:#if in parallax layers
                    new_grass = BackgroundCaveGrass(object_position, self.level.game_objects, parallax, self.level.layer)
                    if self.level.layer.startswith('fg'):
                        self.level.game_objects.all_fgs.add(self.level.layer,new_grass)
                    else:
                        self.level.game_objects.all_bgs.add(self.level.layer,new_grass)

            elif id == 1:#ljusmaksar
                new_grass = LjusMaskar(object_position, self.level.game_objects, parallax, self.level.layer)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_grass)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_grass)

            elif id == 2:#droplet
                if self.level.layer.startswith('fg'):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs

                new_drop = DropletSource(object_position, self.level.game_objects, parallax, self.level.layer, group)
                group.add(self.level.layer, new_drop)

            elif id == 3:#falling rock trap
                new_rock = FallingRockSource(object_position, self.level.game_objects, parallax, self.level.layer)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_rock)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_rock)

            elif id == 4:#vines
                new_vine = Vines_2(object_position, self.level.game_objects, parallax, self.level.layer)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_vine)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_vine)

            elif id == 5:#bubble source
                prop = {}
                for property in properties:
                    if property['name'] == 'lifetime':
                        prop['lifetime'] = property['value']
                    elif property['name'] == 'init_delay':
                        prop['init_delay'] = property['value']
                    elif property['name'] == 'spawnrate':
                        prop['spawnrate'] = property['value']
                    elif property['name'] == 'cos_amp_scaler':
                        prop['cos_amp_scaler'] = property['value']
                    elif property['name'] == 'state':
                        state = property['value']#horizontal or vertical movement #TODO

                bubble_source =  BubbleSource(object_position, self.level.game_objects, **prop)
                self.level.game_objects.interactables.add(bubble_source)

            elif id == 6:#spieks
                spikes = Spikes(object_position, self.level.game_objects)
                self.level.game_objects.interactables.add(spikes)

            elif id == 7:#bubble
                prop = {}
                for property in properties:
                    if property['name'] == 'lifetime':
                        prop['lifetime'] = property['value']

                new_bubble = BubbleStatic(object_position, self.level.game_objects, **prop)
                self.level.game_objects.platforms.add(new_bubble)

            elif id == 8:#ball challange
                new_challange = ChallengeBall(object_position, self.level.game_objects)
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
                new_bridge = Bridge(object_position, self.level.game_objects)
                self.level.game_objects.platforms.add(new_bridge)

            elif id == 3:#droplet
                if self.level.layer.startswith('fg'):
                    group = self.level.game_objects.all_fgs
                else:
                    group = self.level.game_objects.all_bgs

                new_drop = DropletSource(object_position, self.level.game_objects, parallax, self.level.layer, group)
                group.add(self.level.layer, new_drop)

class Crystal_mines(Biome):
    def __init__(self, level):
        super().__init__(level)

    def play_music(self):
        super().play_music()
        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/environments/ambient/crystal_mines')
        self.level.game_objects.sound.play_background_sound(sounds['idle'][0], index = 1, loop = -1, fade = 1000, volume = 0.2)

    def room(self, room = 1):
        self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [255/255,255/255,255/255,255/255], normal_interact = False)
        self.level.game_objects.lights.ambient = (50/255,50/255,100/255,170/255)

    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 7:#Conveyor_belt
                kwarg = {}
                for property in properties:
                    if property['name'] == 'right':
                        kwarg['right'] = property['value']
                    elif property['name'] == 'up':
                        kwarg['up'] = property['value']
                    elif property['name'] == 'vertical':
                        kwarg['vertical'] = property['value']

                new_conveyor_belt = ConveyorBelt(object_position, self.level.game_objects, object_size, **kwarg)
                self.level.game_objects.platforms.add(new_conveyor_belt)

            elif id == 8:#smacker
                kwarg = {'hole': Hole(object_position, self.level.game_objects, object_size)}
                for property in properties:
                    if property['name'] == 'distance':
                        kwarg['distance'] = property['value']

                new_smacker = Smacker(object_position, self.level.game_objects, **kwarg)
                #self.level.game_objects.dynamic_platforms.add(new_smacker)
                self.level.game_objects.platforms.add(new_smacker)

            elif id == 9:#platform
                new_platofrm = CrystalMines_1(self.level.game_objects, object_position)
                self.level.game_objects.platforms.add(new_platofrm)

            elif id == 10:#crystal emitter
                kwarg = {}
                for property in properties:
                    if property['name'] == 'dir':#for proectile
                        pos = property['value']
                        string_list = pos.split(",")
                        kwarg['dir'] = [int(item) for item in string_list]
                    elif property['name'] == 'velocity':#for proectile
                        amp = property['value']
                        string_list = amp.split(",")
                        kwarg['amp'] = [int(item) for item in string_list]
                    elif property['name'] == 'lifetime':#for proectile
                        kwarg['lifetime'] = int(property['value'])
                    elif property['name'] == 'frequency':#for emitter
                        kwarg['frequency'] = int(property['value'])

                new_emitter = CrystalSource(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_emitter)

            elif id == 11:#crystal  1
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, self.level.layer, 'crystal_1')
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_crystal)

            elif id == 12:#crystal  1
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, self.level.layer, 'crystal_2')
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_crystal)

            elif id == 13:#crystal  3
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, self.level.layer, 'crystal_3')
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_crystal)

            elif id == 14:#crystal  4
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, self.level.layer, 'crystal_4')
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_crystal)

            elif id == 15:#crystal  5
                new_crystal = Crystals(object_position, self.level.game_objects, parallax, self.level.layer, 'crystal_5')
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_crystal)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_crystal)

class Dark_forest(Biome):
    def __init__(self, level):
        super().__init__(level)
        self.weather_config = {
            "rain": {
                "layers": {
                    "bg1": { "number_particles": 20}
                }
            },
            "fog": {
                "layers": {
                    "bg1": { "intensity": 0.5, 'colour': (1,1,1,1) },
                    "bg2": { "intensity": 1.0, 'colour': (1,1,1,1) },
                    "bg3": { "intensity": 0.3, 'colour': (0,0,0,1) },
                    "bg4": { "intensity": 0.5, 'colour': (0,0,0,1) },
                    "bg5": { "intensity": 1.0, 'colour': (0,0,0,1) },
                    "bg6": { "intensity": 1.0, 'colour': (0,0,0,1) },
                    "bg7": { "intensity": 1.0, 'colour': (0,0,0,1) }
                }
            }
        }      

    def congigure_weather(self, group, parallax):        
        for weather_type in self.weather_config.keys():#wind, rain, for etc.
            if self.weather_config[weather_type]['layers'].get(group, False):   
                kwarg = self.weather_config[weather_type]['layers'][group]                  
                new_weather = getattr(weather, self._weather_registry[weather_type]['fx_class'])(self.level.game_objects, parallax = parallax, **kwarg)
                
                self._weather_registry[weather_type]['manager'].add_fx(new_weather)
                if group.startswith('fg'):
                    self.level.game_objects.all_fgs.add(group, new_weather)
                else:
                    self.level.game_objects.all_bgs.add(group, new_weather)

    def room(self, room = 1):
        #if room == '2':
        self.level.game_objects.lights.ambient = [30/255,30/255,30/255,170/255]
        self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [255/255,255/255,255/255,255/255], shadow_interact = True, platform_interact = True, normal_interact = False)

    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 9:#vines
                new_viens = Vines_1(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_viens)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_viens)

            elif id == 10:#smalltree 1
                new_viens = SmallTree_1(object_position, self.level.game_objects, parallax)
                if self.level.layer.startswith('fg'):
                    self.level.game_objects.all_fgs.add(self.level.layer,new_viens)
                else:
                    self.level.game_objects.all_bgs.add(self.level.layer,new_viens)

            elif id == 11:#smalltree 1
                new_block = DarkForest_1(object_position, self.level.game_objects)
                self.level.game_objects.cosmetics.add(new_block)

            elif id == 12:#shource of shadow_light
                kwarg = {}
                for property in properties:
                    if property['name'] == 'on':
                        kwarg['on'] = property['value']
                new_lantern = ShadowLightLantern(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.interactables.add(new_lantern)

            elif id == 13:
                kwarg = {}
                for property in properties:
                    if property['name'] == 'ID':
                        kwarg['ID'] = property['value']
                    elif property['name'] == 'erect':
                        kwarg['erect'] = property['value']

                new_platform = DarkForest_2(object_position, self.level.game_objects, **kwarg)
                #self.level.game_objects.dynamic_platforms.add(new_platform)
                self.level.game_objects.platforms.add(new_platform)
                self.level.references['platforms'].append(new_platform)

            elif id == 14:
                new_boss = self.game_objects.registry.fetch('enemies', 'reindeer')(object_position, self.game_objects)
                self.level.game_objects.enemies.add(new_boss)

class Tall_trees(Biome):
    def __init__(self, level):
        super().__init__(level)

    def room(self, room = 1):
        pass
 
    def load_objects(self, data, parallax, offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']

            if id == 10:#packun
                kwarg = {}
                for property in properties:
                    if property['name'] == 'direction':#determine spawn type and set position accordingly
                        kwarg['direction'] = property['value']

                new_enemy = self.game_objects.registry.fetch('enemies', 'packun')(object_position, self.level.game_objects, **kwarg)
                self.level.game_objects.enemies.add(new_enemy)

            elif id == 11:#one side brakable
                for property in properties:
                    if property['name'] == 'ID':
                        ID_key = property['value']

                if not self.level.game_objects.world_state.state[self.level.level_name]['breakable_platform'].get(str(ID_key), False):
                    platform = BreakableOnesideRight(object_position, self.level.game_objects, str(ID_key), 'assets/sprites/entities/platforms/breakable/nordveden/type2/')
                    self.level.game_objects.platforms.add(platform)      

            elif id == 12:#one side brakable
                for property in properties:
                    if property['name'] == 'ID':
                        ID_key = property['value']

                if not self.level.game_objects.world_state.state[self.level.level_name]['breakable_platform'].get(str(ID_key), False):
                    platform = BreakableOnesideLeft(object_position, self.level.game_objects, str(ID_key), 'assets/sprites/entities/platforms/breakable/nordveden/type3/')
                    self.level.game_objects.platforms.add(platform)                       

class Wakeup_forest(Biome):
    def __init__(self, level):
        super().__init__(level)
        self.wrapping_enabled = False
        self.world_width = 0         

    def room(self, room = 1):
        if room in ['3', '4']:
            self.level.game_objects.lights.ambient = (30/255,30/255,30/255,230/255)#230
            if self.level.game_objects.world_state.events.get('guide', False):#if guide interaction has happened
                self.level.game_objects.lights.add_light(self.level.game_objects.player, colour = [200/255,200/255,200/255,200/255],interact = False)

    def play_music(self):
        super().play_music()
        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/environments/ambient/light_forest_cave/')
        #self.level.game_objects.sound.play_background_sound(sounds['idle'][0], index = 1, loop = -1, fade = 1000, volume = 0.1)

    def load_objects(self,data,parallax,offset):
        for obj in data['objects']:
            new_map_diff = [-self.level.PLAYER_CENTER[0],-self.level.PLAYER_CENTER[1]]
            object_size = [int(obj['width']),int(obj['height'])]
            object_position = [int(obj['x']) - math.ceil((1-parallax[0])*new_map_diff[0]) + offset[0], int(obj['y']) - math.ceil((1-parallax[1])*new_map_diff[1]) + offset[1]-object_size[1]]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.level.map_data['objects_firstgid']
