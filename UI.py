import Entities, pygame

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
            self.hearts.append(Entities.Health(self.game_objects))
        self.update_hearts()

    def init_spirits(self):
        self.spirits = []
        for i in range(0,self.game_objects.player.max_spirit):#make hearts
            self.spirits.append(Entities.Spirit(self.game_objects))
        self.update_spirits()

    def init_ability(self):
        self.ability_hud=[]#the hud
        for i in range(0,self.game_objects.player.movement_abilities.number):
            self.ability_hud.append(Entities.Movement_hud(self.game_objects))#the ability object

        self.abilities = self.game_objects.player.movement_abilities.abilities[0:len(self.ability_hud)]#the abilities

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

    def remove_hearts(self,dmg):#dmg is an integer: 1 or 2 and set the rellavant to hurt
        index = self.game_objects.player.health
        index = max(index,0)#in principle not needed but make it fool proof
        for i in range(index,index+dmg):
            self.hearts[i].currentstate.handle_input('Hurt')#make heart go white

    def update_hearts(self):#set the rellavant onces to idle
        for i in range(0,self.game_objects.player.health):#set them to idle for the number of health we have
            self.hearts[i].currentstate.handle_input('Idle')

    def remove_spirits(self,spirit):
        index = self.game_objects.player.spirit + spirit - 1
        index = max(index,0)#in principle not needed but make it fool proof
        for i in range(index,index+spirit):
            self.spirits[i].currentstate.handle_input('Hurt')#make heart go white

    def update_spirits(self):#set the rellavant onces to idle
        for i in range(0,self.game_objects.player.spirit):#set them to idle for the number of health we have
            self.spirits[i].currentstate.handle_input('Idle')
