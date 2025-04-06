import pygame
import entities_UI

class HUD():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.screen = self.game_objects.game.display.make_layer((200,150))

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
        #for i in range(0,self.game_objects.player.abilities.number):
        self.ability_hud.append(entities_UI.Movement_hud(self.game_objects.player))#the ability object

        self.abilities = []
        for key in self.game_objects.player.abilities.movement_dict.keys():
            self.abilities.append(self.game_objects.player.abilities.movement_dict[key])#the ability object
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
        self.screen.clear(0,0,0,0)
        for index, heart in enumerate(self.hearts):#draw health
            self.game_objects.game.display.render(heart.image,self.screen, position = (16*index,0))

        for index, spirit in enumerate(self.spirits):#draw spirit
            self.game_objects.game.display.render(spirit.image,self.screen, position = (16*index,16))

        for index,ability_hud in enumerate(self.ability_hud):#draw movement ability_hud
            self.game_objects.game.display.render(ability_hud.image,self.screen, position = (32*index,60))

        #for index,ability in enumerate(self.abilities):#draw ability symbols
        #    self.game_objects.game.display.render(ability.image,self.screen, position = (32*index,60))

        self.game_objects.game.display.render(self.screen.texture,self.game_objects.game.screen,position = (20, 10))

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
