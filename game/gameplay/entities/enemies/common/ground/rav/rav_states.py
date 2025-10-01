import math, sys, random
from engine.utils import functions
from .decider import *

class BaseState():
    def __init__(self, entity):
        self.entity = entity
        self.deciders = []

    def update(self, dt):
        self.update_logic(dt)
        self.check_transitions(dt)

    def update_logic(self, dt):
        """Override in subclasses: movement, attack, animations, etc."""
        pass

    def check_transitions(self, dt):
        best = None
        for decider in self.deciders:
            for decision in decider.choose(self.player_distance, dt):
                if not best or decision.score > best.score:
                    best = decision

        if best:            
            self.enter_state(best.next_state, **best.params)

    def enter_state(self, state_name, **kwargs):
        self.entity.currentstate.enter_state(state_name, **kwargs)

    def handle_input(self, input_type):
        if input_type == "Hurt" and self.entity.flags.get("hurt_able", True):
            self.enter_state("hurt")

    def modify_hit(self, effect):
        return effect

    def increase_phase(self):
        """Called when animation phase completes"""
        pass

    @property
    def player_distance(self):
        # Fetch from manager instead of storing locally
        return self.entity.currentstate.player_distance

class Idle(BaseState):#do nothing
    def __init__(self, entity):
        super().__init__(entity)

class Patrol(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("walk", 0.17)
        self.entity.velocity = [self.entity.patrol_speed, self.entity.velocity[1]]
        self.timer = self.entity.game_objects.timer_manager.start_timer(self.entity.patrol_timer, self.timeout)
        # Use PatrolDecider here
        self.deciders = [PatrolDecider(entity)]

    def update_logic(self, dt):
        self.entity.velocity[0] += self.entity.dir[0] * self.entity.patrol_speed

    def timeout(self):
        self.enter_state("wait", time=50, next_state="patrol")

    def enter_state(self, newstate, **kwargs):
        self.entity.game_objects.timer_manager.remove_timer(self.timer)
        super().enter_state(newstate, **kwargs)

class Wait(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.time = kwargs.get("time", 50)
        self.next_state = kwargs.get("next_state", "patrol")
        self.entity.animation.play("idle", 0.2)

    def update_logic(self, dt):
        self.time -= dt
        if self.time <= 0:
            # player nearby? attack/chase, else next_state
            if abs(self.player_distance[0]) < self.entity.attack_distance[0]:
                self.enter_state("attack_pre")
            elif abs(self.player_distance[0]) < self.entity.aggro_distance[0] and abs(self.player_distance[1]) < self.entity.aggro_distance[1]:
                self.enter_state("chase")
            else:
                self.enter_state(self.next_state)

    def handle_input(self, input_type):
        if input_type == "Hurt":
            self.enter_state("chase")

class Chase(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("walk")
        self.giveup = kwargs.get("giveup", 400)
        self.time = self.giveup

        cooldown = self.entity.config["cooldowns"]["jump_attack"]
        self.entity.currentstate.cooldowns.set("jump_attack", random.randint(0, cooldown))

        self.deciders = [AttackDecider(entity),ChaseGiveUpDecider(entity),GroundDecider(entity)]

    def update_logic(self, dt):
        self.look_target()
        self.entity.chase(self.player_distance)

    def look_target(self):
        self.entity.dir[0] = 1 if self.player_distance[0] > 0 else -1

class Hurt(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("hurt", 0.2)
        self.entity.flags["hurt_able"] = False
        self.entity.game_objects.timer_manager.start_timer(200, self.entity.on_hurt_timeout)

    def update_logic(self, dt):
        pass

    def increase_phase(self):
        # After hurt animation completes
        if random.random() < 0.5:
            self.enter_state("jump_back_pre")
        else:
            self.enter_state("chase")    

class JumpBackPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("jump_back_pre")

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def increase_phase(self):
        self.enter_state("jump_back_main")

class JumpBackMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("jump_back_main")
        self.entity.velocity[1] = -2
        self.time = 15  # sliding duration

    def update_logic(self, dt):
        self.entity.velocity[0] -= self.entity.dir[0] * 2
        self.time -= dt
        if self.time <= 0:
            self.enter_state("wait", time=40, next_state="chase")

class JumpAttackPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("jump_attack_pre")
        self.deciders = []

    def increase_phase(self):
        self.enter_state("jump_attack_main")

class JumpAttackMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("jump_attack_main")
        self.entity.velocity[1] = -5

        cooldown = self.entity.config["cooldowns"]["jump_attack"]
        self.entity.currentstate.cooldowns.set("jump_attack", cooldown)

    def update_logic(self, dt):
        self.entity.velocity[0] += self.entity.dir[0]
        if self.entity.collision_types["bottom"]:
            self.enter_state("jump_attack_post")

    def modify_hit(self, effect):
        effect.knockback[0] = 0
        return effect

class JumpAttackPost(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("jump_attack_post")

    def increase_phase(self):
        self.enter_state("wait", next_state="chase", time=10)

class Death(BaseState):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.play('death', 0.2)

    def update_logic(self, dt):
        self.entity.velocity = [0, 0]

    def enter_state(self, newstate, **kwarg):
        pass

    def increase_phase(self):
        self.entity.dead()

    def handle_input(self, input_type):
        pass        

class AttackPre(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("attack_pre", 0.25)

    def increase_phase(self):
        self.enter_state("attack_main")

class AttackMain(BaseState):
    def __init__(self, entity, **kwargs):
        super().__init__(entity)
        self.entity.animation.play("attack_main", 0.2)
        self.entity.attack()

        cooldown = self.entity.config["cooldowns"]["melee_attack"]
        self.entity.currentstate.cooldowns.set("melee_attack", cooldown)

    def increase_phase(self):
        self.enter_state("wait", time=10)
