import random

class Decision:
    def __init__(self, next_state, score=0, priority = 0, params=None):
        self.next_state = next_state
        self.score = score
        self.priority = priority  # higher = overrides lower-priority deciders
        self.params = params or {}

class AttackDecider:
    def __init__(self, entity):
        self.entity = entity
        self.dec_cfg = entity.config['decisions']

    def choose(self, player_distance, dt):
        results = []

        # Jump attack
        jump_cfg = self.dec_cfg['jump_attack']
        if abs(player_distance[0]) < self.entity.jump_distance[0] and player_distance[1] < self.entity.jump_distance[1]:
            if self.entity.currentstate.cooldowns.get(jump_cfg['cooldown']) <= 0:
                results.append(Decision(
                    next_state="jump_attack_pre",
                    score=jump_cfg['score'],
                    priority=jump_cfg['priority']
                ))

        # Melee attack
        melee_cfg = self.dec_cfg['melee_attack']
        if abs(player_distance[0]) < self.entity.attack_distance[0]:
            if self.entity.currentstate.cooldowns.get(melee_cfg['cooldown']) <= 0:
                results.append(Decision(
                    next_state="attack_pre",
                    score=melee_cfg['score'],
                    priority=melee_cfg['priority']
                ))

        return results

class ChaseGiveUpDecider:
    def __init__(self, entity):
        self.entity = entity
        # Get config for giveup decision
        self.cfg = self.entity.config['decisions']['chase_giveup']
        self.giveup_timer = self.cfg['time']

    def choose(self, player_distance, dt):
        results = []

        # Check if player is out of aggro range
        if abs(player_distance[0]) > self.entity.aggro_distance[0] or abs(player_distance[1]) > self.entity.aggro_distance[1]:
            self.giveup_timer -= dt
            if self.giveup_timer <= 0:
                results.append(Decision(
                    next_state="wait",
                    score=self.cfg['score'],
                    priority=self.cfg['priority'],
                    params={"time": self.cfg.get('wait_time', 20), "next_state": self.cfg['next_state']}
                ))
        else:
            self.giveup_timer = self.cfg['time']

        return results

class GroundDecider:
    def __init__(self, entity):
        self.entity = entity
        self.cfg = self.entity.config['decisions']['edge_wait']

    def choose(self, player_distance, dt):
        results = []

        # Check ground in front
        x = self.entity.hitbox.centerx + self.entity.dir[0] * (self.entity.hitbox.width // 2 + 5)
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision(
                next_state="wait",
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                params={"time": self.cfg['time'], "next_state": self.cfg['next_state'], "dir": self.cfg['dir']}
            ))

        return results


class PatrolDecider:
    def __init__(self, entity):
        self.entity = entity
        self.cfg = self.entity.config['decisions']['patrol_end_wait']
        self.reset_patrol_timer()

    def reset_patrol_timer(self):
        self.time_left = random.randint(*self.cfg.get('time_range', [80,220]))

    def choose(self, player_distance, dt):
        results = []

        # Patrol timer countdown
        self.time_left -= dt
        if self.time_left <= 0:
            dir = random.choice([-1, 1])
            results.append(Decision(
                next_state="wait",
                score=self.cfg['score'],
                priority=self.cfg['priority'],
                params={"time": 50, "next_state": "patrol", "dir": dir}
            ))
            self.reset_patrol_timer()

        # Player spotted → chase
        chase_cfg = self.entity.config['decisions']['wait_to_chase']
        if abs(player_distance[0]) < self.entity.aggro_distance[0] and abs(player_distance[1]) < self.entity.aggro_distance[1]:
            results.append(Decision(
                next_state="wait",
                score=chase_cfg['score'],
                priority=chase_cfg['priority'],
                params={"time": chase_cfg.get('time',10), "next_state": "chase"}
            ))

        # Edge detected → wait
        edge_cfg = self.entity.config['decisions']['edge_wait']
        x = self.entity.hitbox.centerx + self.entity.dir[0] * (self.entity.hitbox.width // 2 + 5)
        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision(
                next_state="wait",
                score=edge_cfg['score'],
                priority=edge_cfg['priority'],
                params={"time": edge_cfg['time'], "next_state": edge_cfg['next_state'], "dir": edge_cfg['dir']}
            ))

        return results

class WaitDecider:
    def __init__(self, entity, **kwargs):
        self.entity = entity
        self.time = kwargs.get('time', 50)
        self.next_state = kwargs.get('next_state', 'patrol')
        self.dir = kwargs.get('dir', 1)

    def choose(self, player_distance, dt):
        results = []
        self.time -= dt
        if self.time <= 0:
            # Attack range
            attack_cfg = self.entity.config['decisions']['melee_attack']
            if abs(player_distance[0]) < self.entity.attack_distance[0]:
                results.append(Decision(
                    next_state="attack_pre",
                    score=attack_cfg['score'],
                    priority=attack_cfg['priority']
                ))

            # Aggro range
            chase_cfg = self.entity.config['decisions']['wait_to_chase']
            if abs(player_distance[0]) < self.entity.aggro_distance[0] and abs(player_distance[1]) < self.entity.aggro_distance[1]:
                results.append(Decision(
                    next_state="chase",
                    score=chase_cfg['score'],
                    priority=chase_cfg['priority']
                ))

            # Default next state
            results.append(Decision(
                next_state=self.next_state,
                score=50,
                priority=0,
                params={"dir": self.dir}
            ))

        return results