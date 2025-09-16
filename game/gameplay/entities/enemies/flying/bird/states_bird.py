import sys, random

class Enemy_states():
    def __init__(self,entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())#the name of the class       
        #self.dir = self.entity.dir.copy()

    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

    def enter_state(self,newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update(self, dt):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance            
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_state('Fly')

class Idle(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 0
        self.duration = random.randint(10,100)

    def update(self, dt):
        super().update(dt)
        self.duration -= dt

    def increase_phase(self):
        if self.duration < 0:                    
            rand = random.randint(1,4)
            if rand==1:#go back being idle
                self.duration = random.randint(10,100)
            elif rand==2:
                self.entity.animation.play('eat')
                self.duration = random.randint(10,100)
            elif rand==3:
                self.enter_state('Walk')                   
            elif rand==4:
                self.entity.dir[0] *= -1
                self.duration = random.randint(10,100)

class Walk(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 0.5
        self.duration = random.randint(10,100)

    def update(self, dt):
        super().update(dt)
        self.duration -= dt

    def increase_phase(self):
        if self.duration < 0:
            rand = random.randint(1,2)
            if rand==1:
                self.entity.dir[0] *= -1
            self.enter_state('Idle')

class Fly(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration = [0,0]
        self.entity.friction = [0,0]
        self.lifetime = 200
        rand = random.randint(2,7)
        sign = random.choice([-1,1])
        self.entity.dir[0] = sign        
        self.entity.velocity=[sign*rand,-rand]

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0:
            self.entity.kill()

class Death(Enemy_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration = [0,0]

    def update(self, dt):
        self.entity.velocity[0] *= 0.8
        self.entity.velocity[1] *= 0.8

    def increase_phase(self):
        self.entity.dead()

    def enter_state(self,newstate):
        pass