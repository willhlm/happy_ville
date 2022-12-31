import Entities, pygame

class Gameplay_UI():
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.surface = pygame.Surface((1000,100),pygame.SRCALPHA,32).convert_alpha()
        self.init_hearts()
        self.init_spirits()

    def init_hearts(self):
        self.hearts = []
        for i in range(0,self.game_objects.player.max_health):#make hearts
            self.hearts.append(Entities.Health())
        for i in range(0,self.game_objects.player.health):#set them to idle for the number of health we have
            self.hearts[i].currentstate.handle_input('Idle')

        self.heart_index = self.game_objects.player.health - 1#an index to indicate the number of idle/death hearts

    def init_spirits(self):
        self.spirits = []
        for i in range(0,self.game_objects.player.max_spirit):#make hearts
            self.spirits.append(Entities.Spirit())
        for i in range(0,self.game_objects.player.spirit):#set them to idle for the number of health we have
            self.spirits[i].currentstate.handle_input('Idle')#make heart go white

        self.spirit_index = self.game_objects.player.spirit - 1#an index to indicate the number of idle/death hearts

    def update(self):
        for heart in self.hearts:
            heart.update()
        for spirit in self.spirits:
            spirit.update()

    def render(self):
        #draw health
        temp = self.surface.copy()
        for index, heart in enumerate(self.hearts):
            temp.blit(heart.image,(16*index,0))
        self.game_objects.game.screen.blit(temp,(20, 10))

        #draw spirit
        for index, spirit in enumerate(self.spirits):
            temp.blit(spirit.image,(16*index,20))
        self.game_objects.game.screen.blit(temp,(20, 10))

    def remove_health(self,dmg):#dmg is an integer: 1 or 2
        for i in range(dmg):
            self.hearts[self.heart_index].currentstate.handle_input('Hurt')#make heart go white
            self.heart_index -= 1
            self.heart_index = max(self.heart_index, 0)#in principle not needed

    def add_health(self):
        for i in range(0,self.game_objects.player.health):#set them to idle for the number of health we have
            self.hearts[i].currentstate.handle_input('Idle')#set all rellavant once to idle to sync their animation
        self.heart_index += 1
        self.heart_index = min(self.heart_index, len(self.hearts))#in principle not needed

    def add_spirit(self,spirit):
        pass

    def remove_spirit(self,spirit):
        for i in range(spirit):
            self.spirits[self.spirit_index].currentstate.handle_input('Hurt')#make heart go white
            self.spirit_index -= 1
            self.spirit_index = max(self.spirit_index, 0)#in principle not needed
