import math, sys, random

class EnemyStates():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_state(self, newstate, **kwarg):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self, dt):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def handle_input(self, input):#input is hurt when taking dmg
        if input == 'Hurt':
            self.enter_state('Chase')

    def increase_phase(self):
        pass

class Idle(EnemyStates):#do nothing
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

class Patrol(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.dir[0] = self.entity.dir[0] * -1
        patrol_timer = 100
        self.patrol_speed = 0.5
        self.timer = self.entity.game_objects.timer_manager.start_timer(patrol_timer, self.timeout)
        self.entity.animation.play('walk')

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] += self.entity.dir[0]*self.patrol_speed
        self.check_sight()
        self.check_ground()

    def timeout(self):
        self.enter_state('Wait', time = 150, next_state = 'Patrol')

    def check_ground(self):
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5
            
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_state('Wait', time = 70, next_state = 'Patrol')

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_state('Wait', time = 10, next_state = 'Chase')

class Wait(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.time = kwarg.get('time',50)
        self.next_state = kwarg.get('next_state','Patrol')
        self.entity.animation.play('idle')

    def update(self, dt):
        self.time -= dt
        if self.time < 0:
            self.enter_state(self.next_state)

class Chase(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.giveup = kwarg.get('giveup', 400)
        self.time = self.giveup
        self.entity.animation.play('walk')

    def update(self, dt):
        super().update(dt)
        self.look_target()
        self.entity.chase(self.player_distance)
        self.check_sight(dt)

    def check_sight(self, dt):
        if abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away
            self.time -= dt
            if self.time < 0:
                self.enter_state('Wait',next_state = 'Patrol', time = 20)
        elif abs(self.player_distance[0]) < self.entity.attack_distance[0] and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close
            self.enter_state('Attack')
        else:#player close, reset timer
            self.time = self.giveup

    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Knock_back(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def update(self, dt):
        super().update(dt)
        self.look_target()
        self.entity.chase_knock_back(self.player_distance)
        self.check_vel()

    def check_vel(self):
        if abs(self.entity.velocity[0]) + abs(self.entity.velocity[1]) < 0.3:
            self.enter_state('Wait', next_state = 'Chase', time = 10)

    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Attack(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.currentstate.handle_input('attack')

    def handle_input(self,input):#called from states, depending on if the player was close when it wanted to explode or not
        if input == 'finish_attack':
            self.enter_state('Wait', next_state = 'Chase', time = 30)

class Death(EnemyStates):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('death')

    def enter_state(self, newstate, **kwarg):
        pass

    def update(self, dt):
        self.entity.velocity = [0,0]

    def increase_phase(self):
        self.entity.dead()        