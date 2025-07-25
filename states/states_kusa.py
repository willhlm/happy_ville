import sys
from states_entity import Entity_States

class EnemyStates(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate, **kwarg):
        self.entity.currentstate=getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx-self.entity.rect.centerx,self.entity.game_objects.player.rect.centery-self.entity.rect.centery]#check plater distance

class Idle(EnemyStates):
    def __init__(self, entity):
        super().__init__(entity)

    def update(self):
        super().update()
        if abs(self.player_distance[0]) < 150:
            self.enter_state('Transform')

class Transform(EnemyStates):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[1] = -7

    def update(self):
        if self.entity.collision_types['bottom']:
            self.enter_state('Wait', next_state = 'Chase')

class Wait(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.time = kwarg.get('time',50)
        self.next_state = kwarg.get('next_state','Patrol')
        self.entity.animation.play('idle_aggro')

    def update(self):
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.enter_state(self.next_state)

class Chase(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.giveup = kwarg.get('giveup', 400)
        self.time = self.giveup
        self.entity.animation.play('walk')

    def update(self):
        super().update()
        self.look_target()
        self.entity.chase(self.player_distance)
        self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away
            self.time -= self.entity.game_objects.game.dt
            if self.time < 0:
                self.enter_state('Wait',next_AI = 'Patrol', time = 20)
        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close
            self.enter_state('Death')
        else:#player close, reset timer
            self.time = self.giveup

    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Death(EnemyStates):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.suicide()

    def increase_phase(self):
        self.entity.dead()
