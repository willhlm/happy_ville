import math, sys, random

class AI():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_AI(self, newAI, **kwarg):
        self.entity.AI = getattr(sys.modules[__name__], newAI)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def deactivate(self):
        self.enter_AI('Idle')

    def handle_input(self, input):#input is hurt when taking dmg
        pass

    def handle_input(self, input):#input is hurt when taking dmg
        if input == 'Hurt':
            self.enter_AI('Chase')

class Idle(AI):#do nothing
    def __init__(self, entity):
        super().__init__(entity)

class Patrol(AI):#patrol in a circle aorund the original position
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.dir[0] = self.entity.dir[0] * -1
        self.entity.velocity = [self.entity.patrol_speed, self.entity.velocity[1]]
        self.timer = self.entity.game_objects.timer_manager.start_timer(self.entity.patrol_timer, self.timeout)

    def update(self):
        super().update()
        self.entity.velocity[0] += self.entity.dir[0]*self.entity.patrol_speed
        self.check_sight()
        self.check_ground()

    def timeout(self):
        self.enter_AI('Wait', time = 150, next_AI = 'Patrol')

    def check_ground(self):
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_AI('Wait', time = 70, next_AI = 'Patrol')

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_AI('Wait', time = 10, next_AI = 'Chase')

class Wait(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.time = kwarg.get('time',50)
        self.next_AI = kwarg.get('next_AI','Patrol')
        self.entity.currentstate.enter_state('Idle')

    def update(self):
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.enter_AI(self.next_AI)

class Chase(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.giveup = kwarg.get('giveup', 400)
        self.time = self.giveup

    def update(self):
        super().update()
        self.look_target()
        self.entity.chase(self.player_distance)
        self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away
            self.time -= self.entity.game_objects.game.dt
            if self.time < 0:
                self.enter_AI('Wait',next_AI = 'Patrol', time = 20)
        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close
            self.enter_AI('Attack')
        else:#player close, reset timer
            self.time = self.giveup

    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Knock_back(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def update(self):
        super().update()
        self.look_target()
        self.entity.chase_knock_back(self.player_distance)
        self.check_vel()

    def check_vel(self):
        if abs(self.entity.velocity[0]) + abs(self.entity.velocity[1]) < 0.3:
            self.enter_AI('Wait', next_AI = 'Chase', time = 10)

    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Attack(AI):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.currentstate.handle_input('attack')

    def handle_input(self,input):#called from states, depending on if the player was close when it wanted to explode or not
        if input == 'finish_attack':
            self.enter_AI('Wait', next_AI = 'Chase', time = 30)
