import pygame, math
import Read_files, entities_UI

class UI_loader():#for map, omamori, ability, journal etc
    def __init__(self,game_objects,type):
        self.game_objects = game_objects
        self.BG = pygame.image.load('UI/' + type + '/BG.png').convert_alpha()
        self.source = {'map':'map_UI','omamori':'omamori_UI','journal':'journal_UI','fast_travel':'fast_travel_UI','ability_spirit_upgrade':'ability_spirit_upgrade_UI','ability_movement_upgrade':'ability_movement_upgrade_UI','inventory':'inventory_UI'}[type]#the name of the tmx file with the objects
        self.load_UI_data(type)
        self.load_data = {'map':self.load_map_data,'omamori':self.load_omamori_data,'journal':self.load_journal_data,'fast_travel':self.load_fast_travel_data,'ability_spirit_upgrade':self.load_ability_spirit_upgrade_data,'ability_movement_upgrade':self.load_ability_movement_upgrade_data,'inventory':self.load_inventory_data}[type]()

    def load_UI_data(self,type):
        map_data = Read_files.read_json("UI/%s/%s.json" % (type,type))
        self.map_data = Read_files.format_tiled_json(map_data)
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if self.source in tileset['source']:#the name of the tmx file
                    self.map_data['UI_firstgid'] =  tileset['firstgid']

    def load_map_data(self):
        self.objects = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:
                new_banner = entities_UI.Banner(topleft_object_position,self.game_objects,str(1),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 1:
                new_banner = entities_UI.Banner(topleft_object_position,self.game_objects,str(2),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 2:
                new_banner = entities_UI.Banner(topleft_object_position,self.game_objects,str(3),properties[0]['value'])
                self.objects.append(new_banner)

    def load_omamori_data(self):
        self.equipped = []
        self.inventory = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#inventory
                name = properties[0]['value']#the name of omamori
                new_omamori = entities_UI.Empty_omamori(topleft_object_position,self.game_objects)
                self.inventory[name] = new_omamori
            elif id == 1:#equipeed
                new_omamori = entities_UI.Empty_omamori(topleft_object_position,self.game_objects)
                self.equipped.append(new_omamori)

    def load_journal_data(self):
        self.name_pos = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#image
                self.image_pos = topleft_object_position
            elif id == 1:#name
                self.name_pos.append(topleft_object_position)

    def load_fast_travel_data(self):
        self.name_pos = []
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#name
                self.name_pos.append(topleft_object_position)

    def load_ability_spirit_upgrade_data(self):
        self.abilities = [[],[],[],[],[]]#orginise them accotding to the grid in tiled
        self.rows = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#arrow
                new_ability = entities_UI.Arrow(topleft_object_position,self.game_objects)
                self.abilities[0].append(new_ability)
                self.rows['Arrow'] = 0
            elif id == 1:#force
                new_ability = entities_UI.Force(topleft_object_position,self.game_objects)
                self.abilities[1].append(new_ability)
                self.rows['Force'] = 1
            elif id == 2:#migawari
                new_ability = entities_UI.Migawari(topleft_object_position,self.game_objects)
                self.abilities[2].append(new_ability)
                self.rows['Migawari'] = 2
            elif id == 3:#slowmotion
                new_ability = entities_UI.Slow_motion(topleft_object_position,self.game_objects)
                self.abilities[3].append(new_ability)
                self.rows['Slow_motion'] = 3
            elif id == 4:#thunder
                new_ability = entities_UI.Thunder(topleft_object_position,self.game_objects)
                self.abilities[4].append(new_ability)
                self.rows['Thunder'] = 4

    def load_ability_movement_upgrade_data(self):
        self.abilities = [[],[],[]]#orginise them accotding to the grid in tiled
        self.rows = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#dash
                new_ability = entities_UI.Dash(topleft_object_position,self.game_objects)
                self.abilities[0].append(new_ability)
                self.rows['Dash'] = 0
            elif id == 1:#double_jump
                new_ability = entities_UI.Double_jump(topleft_object_position,self.game_objects)
                self.abilities[1].append(new_ability)
                self.rows['Double_jump'] = 1
            elif id == 2:#wall_glide
                new_ability = entities_UI.Wall_glide(topleft_object_position,self.game_objects)
                self.abilities[2].append(new_ability)
                self.rows['Wall_glide'] = 2

    def load_inventory_data(self):
        self.key_items = {}
        self.items = []
        self.stones = {}
        for obj in self.map_data['elements']:
            object_size = [int(obj['width']),int(obj['height'])]
            topleft_object_position = [int(obj['x']), int(obj['y'])-int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            if id == 0:#sword
                new_item = entities_UI.Sword(topleft_object_position,self.game_objects)
                self.sword = new_item
            elif id == 1:#infinity stone
                name = properties[0]['value']#the name of stone
                new_item = entities_UI.Infinity_stone(topleft_object_position,self.game_objects)#make an object based on stringgetattr(entities_UI, name)
                self.stones[name] = new_item
            elif id == 2:#item
                name = properties[0]['value']#the name of item
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)
                self.items.append(new_item)
            elif id == 3:#key_item
                name = properties[0]['value']#the name of keyitem
                new_item = entities_UI.Item(topleft_object_position,self.game_objects)
                self.key_items[name] = new_item

class Gameplay_UI():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.surface = pygame.Surface((500,100),pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        self.init_hearts()
        self.init_spirits()
        self.init_ability()

    def init_hearts(self):
        self.hearts = []
        for i in range(0,self.game_objects.player.max_health):#make hearts
            self.hearts.append(entities_UI.Health(self.game_objects))
        self.update_hearts()

    def init_spirits(self):
        self.spirits = []
        for i in range(0,self.game_objects.player.max_spirit):#make hearts
            self.spirits.append(entities_UI.Spirit(self.game_objects))
        self.update_spirits()

    def init_ability(self):
        self.ability_hud=[]#the hud
        for i in range(0,self.game_objects.player.abilities.number):
            self.ability_hud.append(entities_UI.Movement_hud(self.game_objects.player))#the ability object

        self.abilities = []
        for key in self.game_objects.player.abilities.movement_dict.keys():
            self.abilities.append(getattr(entities_UI, key)([0,0],self.game_objects))
            if len(self.abilities) == len(self.ability_hud):
                break

    def update(self):
        for heart in self.hearts:
            heart.update()
        for spirit in self.spirits:
            spirit.update()
        for ability_hud in self.ability_hud:
            ability_hud.update()
        for ability in self.abilities:
            ability.update()

    def render(self):
        #draw health
        temp = self.surface.copy()
        for index, heart in enumerate(self.hearts):
            temp.blit(heart.image,(16*index,0))

        #draw spirit
        for index, spirit in enumerate(self.spirits):
            temp.blit(spirit.image,(16*index,16))

        #draw movement ability_hud
        for index,ability_hud in enumerate(self.ability_hud):
            temp.blit(ability_hud.image,(32*index,60))

        #draw ability symbols
        for index,ability in enumerate(self.abilities):
            temp.blit(ability.image,(32*index,60))

        self.game_objects.game.screen.blit(temp,(20, 10))

    def remove_hearts(self,dmg):#dmg is 0.5, 1 or 2. Will set the rellavant to hurt
        index = int(self.game_objects.player.health)-1
        index = max(index,-1)
        for i in range(index+int(dmg+0.5+self.game_objects.player.health-int(self.game_objects.player.health)),index,-1):
            health = self.hearts[i].health
            self.hearts[i].take_dmg(dmg)
            dmg -= health#distribute the dmg

    def update_hearts(self):#set the rellavant onces to idle
        for i in range(0,int(self.game_objects.player.health)):#set them to idle for the number of health we have
            self.hearts[i].currentstate.handle_input('Idle')
        if self.game_objects.player.health - i -1 == 0.5:
            self.hearts[i+1].currentstate.enter_state('Idle')
            self.hearts[i+1].take_dmg(0.5)

    def remove_spirits(self,spirit):
        index = self.game_objects.player.spirit + spirit - 1
        index = max(index,0)#in principle not needed but make it fool proof
        for i in range(index,index+spirit):
            self.spirits[i].currentstate.handle_input('Hurt')#make heart go white

    def update_spirits(self):#set the rellavant onces to idle
        for i in range(0,self.game_objects.player.spirit):#set them to idle for the number of health we have
            self.spirits[i].currentstate.handle_input('Idle')
