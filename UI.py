import pygame, math
import Read_files, entities_UI

class UI_loader():#for map
    def __init__(self,game_objects,type):
        self.game_objects = game_objects
        self.BG = pygame.image.load('UI/' + type + '/BG.png').convert_alpha()
        self.source = {'map':'map_UI','inventory':'inventory_map'}[type]#the name of the tmx file with the objects
        self.load_UI_data(type)
        self.load_data()

    def load_UI_data(self,type):
        map_data = Read_files.read_json("UI/%s/%s.json" % (type,type))
        self.map_data = Read_files.format_tiled_json(map_data)
        for tileset in self.map_data['tilesets']:
            if 'source' in tileset.keys():
                if self.source in tileset['source']:#the name of the tmx file
                    self.map_data['UI_firstgid'] =  tileset['firstgid']

    def load_data(self):
        self.objects = []
        map_statics = self.map_data['elements']
        for obj in map_statics:
            object_position = [int(obj['x']), int(obj['y'])]
            object_size = [int(obj['width']),int(obj['height'])]
            properties = obj.get('properties',[])
            id = obj['gid'] - self.map_data['UI_firstgid']

            #this part probably depends on the tmx file with the objects
            if id == 0:
                new_banner = entities_UI.Banner(object_position,self.game_objects,str(1),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 1:
                new_banner = entities_UI.Banner(object_position,self.game_objects,str(2),properties[0]['value'])
                self.objects.append(new_banner)
            elif id == 2:
                new_banner = entities_UI.Banner(object_position,self.game_objects,str(3),properties[0]['value'])
                self.objects.append(new_banner)

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

        self.abilities = self.game_objects.player.abilities.movement_abilities[0:len(self.ability_hud)]#the abilities

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
