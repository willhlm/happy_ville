import sys, random

class AI():
    def __init__(self,entity):
        self.entity = entity
        self.counter = 0
        self.player_distance = [0,0]

    def enter_AI(self,newAI):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity)#make a class based on the name of the newstate: need to import sys

    def handle_input(self,input,duration=100):
        pass

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance
        self.counter += 1

class Peace(AI):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if abs(self.player_distance[0])<self.aggro_distance[0]:
            self.entity.currentstate.handle_input('Fly')
        else:
            rand=random.randint(0,100)
            if rand==1:
                self.entity.currentstate.handle_input('Idle')
            elif rand==2:
                self.entity.currentstate.handle_input('Walk')
            elif rand==3:
                self.entity.currentstate.handle_input('Eat')
            elif rand==4:
                self.entity.dir[0]=-self.entity.dir[0]
