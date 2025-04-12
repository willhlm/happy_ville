import pygame
import entities_UI

class HUD():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.screen = self.game_objects.game.display.make_layer((500,300))

        self.offset = 5

        self.init_hearts()
        self.init_spirits()
        self.init_ability()
        self.init_money()



    def init_hearts(self):
        self.hearts = []
        self.hearts.append(entities_UI.Health_frame(self.game_objects))
        for i in range(0,self.game_objects.player.max_health - 1):#make hearts
            self.hearts.append(entities_UI.Health(self.game_objects))
        self.update_hearts()

    def init_spirits(self):
        self.spirits = []
        self.spirits.append(entities_UI.Spirit_frame(self.game_objects))
        for i in range(0,self.game_objects.player.max_spirit - 1):#make hearts
            self.spirits.append(entities_UI.Spirit(self.game_objects))
        self.update_spirits()

    def init_ability(self):
        self.ability_hud = []#the hud
        #for i in range(0,self.game_objects.player.abilities.number):
        self.ability_hud.append(entities_UI.Movement_hud(self.game_objects.player))#the ability object

        #self.ability_hud = entities_UI.Movement_hud(self.game_objects.player)

        self.abilities = []
        for key in self.game_objects.player.abilities.movement_dict.keys():
            self.abilities.append(self.game_objects.player.abilities.movement_dict[key])#the ability object
            if len(self.abilities) == len(self.ability_hud):
                break

    def init_money(self):
        self.money_frame = entities_UI.Money_frame(self.game_objects.player)

        string = '9'
        self.money_image = self.game_objects.font.render((50,20),string)

        self.money_pos = (self.offset, 50)
        self.number_pos = (self.offset + 23, 55)

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

        #self.temp_screen = self.game_objects.game.display.make_layer((500,300))
        #self.temp_screen.clear(0,0,0,0)

        h_pos = (14, 12)
        s_pos = (12, 12)
        frame_width = self.ability_hud[0].rect.width
        self.screen.clear(0,0,0,0)

        #self.game_objects.game.display.render(ability_frame.image, heart.image, self.screen, position=(16 * index, 0))

        for index,ability_hud in enumerate(self.ability_hud):#draw movement ability_hud
            self.game_objects.game.display.render(ability_hud.image,self.screen, position = (self.offset, self.offset))

        for index, heart in enumerate(self.hearts):#draw health
            if index == 0:
                pos = (h_pos[0]*index + frame_width-3+self.offset, 7+self.offset)
            else:
                pos = (h_pos[0]*index + frame_width-5+self.offset, h_pos[1]+self.offset)
            self.game_objects.game.display.render(heart.image,self.screen, position = pos)

        for index, spirit in enumerate(self.spirits):#draw spirit
            continue
            if index == 0:
                pos = (5+self.offset, s_pos[1] * index + frame_width - 3+self.offset)
            else:
                pos = (s_pos[0]+self.offset, s_pos[1] * index + frame_width - 5+self.offset)
            self.game_objects.game.display.render(spirit.image,self.screen, position = pos)

        self.game_objects.game.display.render(self.money_frame.image,self.screen, position = self.money_pos)
        self.game_objects.game.display.render(self.money_image,self.screen, position = self.number_pos)

        #for index,ability in enumerate(self.abilities):#draw ability symbols
        #    self.game_objects.game.display.render(ability.image,self.screen, position = (32*index,60))

        self.game_objects.shaders['blur_outline']['blurRadius'] = 1
        self.game_objects.game.display.render(self.screen.texture, self.game_objects.game.screen, position = (20, 20), shader = self.game_objects.shaders['blur_outline'])

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
        if self.game_objects.player.health - i - 1 == 0.5:
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
