import random

class Decision:
    def __init__(self, next_state=None, score=0, priority = 0, params=None):
        self.next_state = next_state
        self.score = score
        self.priority = priority  # higher = overrides lower-priority deciders
        self.params = params or {}

class AttackDecider:
    def __init__(self, entity):
        self.entity = entity

    def choose(self, player_distance, dt):
        results = []

        # Jump attack
        if abs(player_distance[0]) < self.entity.jump_distance[0] and player_distance[1] < -10:
            if self.entity.currentstate.cooldowns.get("jump_attack") <= 0:
                results.append(Decision("jump_attack_pre", score=80, priority=1))

        # Melee attack
        if abs(player_distance[0]) < self.entity.attack_distance[0]:
            if self.entity.currentstate.cooldowns.get("melee_attack") <= 0:
                results.append(Decision("attack_pre", score=60, priority=1))

        return results

class ChaseGiveUpDecider:
    def __init__(self, entity):
        self.entity = entity
        self.giveup_timer = 400

    def choose(self, player_distance, dt):
        # Player is too far
        results = []
        if abs(player_distance[0]) > self.entity.aggro_distance[0] or abs(player_distance[1]) > self.entity.aggro_distance[1]:
            self.giveup_timer -= dt
            if self.giveup_timer <= 0:                
                results.append(Decision("wait", score=50, priority=1, params={"time": 20, "next_state": "patrol"}))
        else:
            self.giveup_timer = 400
        return results

class GroundDecider:
    def __init__(self, entity):
        self.entity = entity

    def choose(self, player_distance, dt):
        results = []
        # Check ground in front
        x = (self.entity.hitbox.centerx + self.entity.dir[0] * (self.entity.hitbox.width // 2 + 5))
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision("wait", score=90, priority=2 ,params={"time": 60, "next_state": "patrol", 'dir':-1}))
        return results

class PatrolDecider:
    def __init__(self, entity):
        self.entity = entity
        self.reset_patrol_timer()

    def reset_patrol_timer(self):# Patrol duration (in frames or ms depending on your dt)        
        self.time_left = random.randint(self.entity.patrol_timer[0], self.entity.patrol_timer[1])  # 1–2 seconds at 60 FPS

    def choose(self, player_distance, dt):
        results = []

        # Patrol duration countdown
        self.time_left -= dt
        if self.time_left <= 0:
            # Stop patrolling → Wait → Patrol again
            dir = random.choice([-1, 1])  # Flip or keep direction
            results.append(Decision(
                next_state="wait",
                score=50,
                priority=0,
                params={"time": 50, "next_state": "patrol", "dir": dir}
            ))
            self.reset_patrol_timer()

        # Player spotted → break patrol → chase
        if abs(player_distance[0]) < self.entity.aggro_distance[0] and abs(player_distance[1]) < self.entity.aggro_distance[1]:
            results.append(Decision(
                next_state="wait",
                score=90,
                priority=1,
                params={"time": 10, "next_state": "chase"}
            ))

        # Edge detected → stop patrol → wait
        x = (self.entity.hitbox.centerx + self.entity.dir[0] * (self.entity.hitbox.width // 2 + 5))
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision(
                next_state="wait",
                score=95,
                priority=2,
                params={"time": 60, "next_state": "patrol", "dir": -1}
            ))

        return results

class WaitDecider:
    def __init__(self, entity,**kwargs):
        self.entity = entity
        self.time = kwargs.get('time', 50)
        self.next_state = kwargs.get('next_state', 'patrol')
        self.dir = kwargs.get('dir', 1)

    def choose(self, player_distance, dt):
        """
        params: optional dict passed from Wait state, e.g., next_state
        Returns a list of Decision objects.
        """
        self.time -= dt
        results = []
        if self.time < 0:#after waiting:            
            # Check attack range
            if abs(player_distance[0]) < self.entity.attack_distance[0]:
                results.append(Decision(
                    next_state="attack_pre",
                    score=90,
                    priority=1
                ))

            # Check aggro range
            if (abs(player_distance[0]) < self.entity.aggro_distance[0] and abs(player_distance[1]) < self.entity.aggro_distance[1]):
                results.append(Decision(
                    next_state="chase",
                    score=80,
                    priority=1
                ))

            # Otherwise go to next state 
            results.append(Decision(
                next_state=self.next_state,
                score=50,
                priority=0,
                params={"dir": self.dir}
            ))

        return results