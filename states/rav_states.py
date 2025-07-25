import math, sys, random

class BaseState():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_state(self, newstate, **kwarg):     
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def deactivate(self):
        self.enter_state('Idle')

    def handle_input(self, input):#input is hurt when taking dmg
        pass

    def increase_phase(self):
        pass

    def handle_input(self, input):#input is hurt when taking dmg
        if input == 'Hurt':
            self.enter_state('Hurt')

class Idle(BaseState):#do nothing
    def __init__(self, entity):
        super().__init__(entity)

class Patrol(BaseState):#goes back and forth
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('walk', 0.17)
        self.entity.dir[0] = self.entity.dir[0] * -1
        self.entity.velocity = [self.entity.patrol_speed, self.entity.velocity[1]]
        self.timer = self.entity.game_objects.timer_manager.start_timer(self.entity.patrol_timer, self.timeout, ID = 'BOOYAA')

    def update(self):
        super().update()        
        self.entity.velocity[0] += self.entity.dir[0]*self.entity.patrol_speed
        self.check_sight()
        self.check_ground()       

    def timeout(self):
        self.enter_state('Wait', time = 120, next_state = 'Patrol')

    def check_ground(self):
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_state('Wait', time = 60, next_state = 'Patrol')

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_state('Wait', time = 10, next_state = 'Chase')            

class Wait(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.time = kwarg.get('time',50)
        self.next_state = kwarg.get('next_state','Patrol')
        self.entity.animation.play('idle', 0.2)

    def update(self):
        super().update()
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.attack_distance[0]: # and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close
            self.enter_state('Attack_pre')
        elif abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_state('Chase')
        else:
            self.enter_state(self.next_state)

class Chase(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('walk')
        self.giveup = kwarg.get('giveup', 400)
        self.time = self.giveup

    def update(self):
        super().update()
        self.check_sight()
        self.check_ground()
        self.look_target()
        self.entity.chase(self.player_distance)

    def check_ground(self):
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            self.enter_state('Wait', time = 120, next_state = 'Patrol')

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.attack_distance[0]: # and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close
            self.enter_state('Attack_pre')
        elif abs(self.player_distance[0]) > self.entity.aggro_distance[0] or abs(self.player_distance[1]) > self.entity.aggro_distance[1]:#player far away
            self.time -= self.entity.game_objects.game.dt
            if self.time < 0:
                self.enter_state('Wait',next_state = 'Patrol', time = 20)
        else:#player close, reset timer
            self.time = self.giveup

    def look_target(self):
        if self.player_distance[0] > 0:
            self.entity.dir[0] = 1
        else:
            self.entity.dir[0] = -1

class Hurt(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('hurt', 0.2)

    def increase_phase(self):
        self.enter_state('Wait', time=20)

class Death(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('death', 0.2)

    def enter_state(self, newstate, **kwarg):
        pass

    def increase_phase(self):
        self.entity.dead()

class Attack_pre(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_pre', 0.25)

    def increase_phase(self):
        self.enter_state('Attack_main')

class Attack_main(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_main', 0.2)
        self.entity.attack()

    def increase_phase(self):
        self.enter_state('Wait', time=10)