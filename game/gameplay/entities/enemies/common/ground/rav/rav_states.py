import math, sys, random

class BaseState():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0, 0]

    def update(self, dt):
        player = self.entity.game_objects.player
        self.player_distance = [player.rect.centerx - self.entity.rect.centerx, player.rect.centery - self.entity.rect.centery]

    def increase_phase(self):
        pass

    def handle_input(self, input_type):
        if input_type == 'Hurt':
            if not self.entity.flags['hurt_able']: return                
            self.enter_state('hurt')

    def enter_state(self, state_name, **kwargs):
        """Delegate state transition to manager"""
        self.entity.currentstate.enter_state(state_name, **kwargs)

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

    def update(self, dt):
        super().update(dt)        
        self.entity.velocity[0] += self.entity.dir[0]*self.entity.patrol_speed
        self.check_sight()
        self.check_ground()       

    def timeout(self):
        self.enter_state('wait', time = 120, next_state = 'patrol')

    def check_ground(self):
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_state('wait', time = 60, next_state = 'patrol')

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.entity.game_objects.timer_manager.remove_timer(self.timer)
            self.enter_state('wait', time = 10, next_state = 'chase')            

class Wait(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.time = kwarg.get('time',50)
        self.next_state = kwarg.get('next_state','patrol')
        self.entity.animation.play('idle', 0.2)

    def update(self, dt):
        super().update(dt)
        self.time -= dt
        if self.time < 0:
            self.check_sight()

    def check_sight(self):
        if abs(self.player_distance[0]) < self.entity.attack_distance[0]: # and abs(self.player_distance[1]) < self.entity.attack_distance[1]:#player close
            self.enter_state('attack_pre')
        elif abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
            self.enter_state('chase')
        else:
            self.enter_state(self.next_state)

class Chase(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('walk')
        self.giveup = kwarg.get('giveup', 400)
        self.time = self.giveup

    def update(self, dt):
        super().update(dt)
        self.check_sight(dt)
        self.check_ground()
        self.look_target()
        self.entity.chase(self.player_distance)

    def check_ground(self):
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            self.enter_state('wait', time = 120, next_state = 'patrol')

    def check_sight(self, dt):
        # Use attack decider for professional decision making
        chosen_attack = self.entity.currentstate.attack_decider.choose_attack(self.player_distance)
        if chosen_attack:
            self.enter_state(chosen_attack)
            return

        # Fallback to old behavior for out-of-range
        if (abs(self.player_distance[0]) > self.entity.aggro_distance[0] or 
            abs(self.player_distance[1]) > self.entity.aggro_distance[1]):
            self.time -= dt
            if self.time < 0:
                self.enter_state('wait', next_state='patrol', time=20)
        else:
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
        self.entity.game_objects.timer_manager.start_timer(200, self.entity.on_hurt_timeout)
        self.entity.flags['hurt_able'] = False

    def increase_phase(self):
        if random.random() < 0.5:  # 50% chance
            self.enter_state('jump_back')
        else:
            self.enter_state('chase')        

class JumpBack(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_back')
        self.entity.velocity[0] = -self.entity.dir[0] * 5.0
        self.time = 15  # short slide time

    def update(self, dt):
        super().update(dt)
        self.time -= dt
        if self.time <= 0:
            self.enter_state('chase')

class JumpAttackPre(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_attack_pre')                

    def increase_phase(self):
        self.enter_state('jump_attack_main')

class JumpAttackMain(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_attack_main')        
        self.entity.velocity[1] = -5
        
        # Set cooldown through manager
        cooldown = self.entity.config['cooldowns']['jump_attack']
        self.entity.currentstate.cooldowns.set('jump_attack', cooldown)

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] += self.entity.dir[0]
        if self.entity.collision_types['bottom']:
            self.enter_state('jump_attack_post')          

class JumpAttackPost(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('jump_attack_post')        

    def increase_phase(self):
        self.enter_state('wait', next_state = 'chase', time = 10)                   

class Death(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('death', 0.2)

    def enter_state(self, newstate, **kwarg):
        pass

    def increase_phase(self):
        self.entity.dead()

class AttackPre(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_pre', 0.25)

    def increase_phase(self):
        self.enter_state('attack_main')

class AttackMain(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('attack_main', 0.2)
        self.entity.attack()
        
         # Set cooldown through manager
        cooldown = self.entity.config['cooldowns']['melee_attack']
        self.entity.currentstate.cooldowns.set('melee_attack', cooldown)

    def increase_phase(self):
        self.enter_state('wait', time=10)