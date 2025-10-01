class Decision:
    def __init__(self, next_state=None, score=0, params=None):
        self.next_state = next_state
        self.score = score
        self.params = params or {}

class AttackDecider:
    def __init__(self, entity):
        self.entity = entity

    def choose(self, player_distance, dt):
        results = []

        # Jump attack
        if abs(player_distance[0]) < self.entity.jump_distance[0] and player_distance[1] < -10:
            if self.entity.currentstate.cooldowns.get("jump_attack") <= 0:
                results.append(Decision("jump_attack_pre", score=80))

        # Melee attack
        if abs(player_distance[0]) < self.entity.attack_distance[0]:
            if self.entity.currentstate.cooldowns.get("melee_attack") <= 0:
                results.append(Decision("attack_pre", score=60))

        return results

class ChaseGiveUpDecider:
    def __init__(self, entity):
        self.entity = entity
        self.giveup_timer = 400

    def choose(self, player_distance, dt):
        # Player is too far
        if abs(player_distance[0]) > self.entity.aggro_distance[0] or abs(player_distance[1]) > self.entity.aggro_distance[1]:
            self.giveup_timer -= dt
            if self.giveup_timer <= 0:                
                return [Decision("wait", score=50, params={"time": 20, "next_state": "patrol"})]
        else:
            self.giveup_timer = 400
        return []

class GroundDecider:
    def __init__(self, entity):
        self.entity = entity

    def choose(self, player_distance, dt):
        results = []
        # Check ground in front
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5

        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision("wait", score=90, params={"time": 60, "next_state": "patrol", 'dir':-1}))
        return results

class PatrolDecider:
    def __init__(self, entity):
        self.entity = entity

    def choose(self, player_distance, dt):
        results = []

        # 1️⃣ Player spotted → switch to wait/chase
        if abs(player_distance[0]) < self.entity.aggro_distance[0] and abs(player_distance[1]) < self.entity.aggro_distance[1]:
            results.append(Decision(
                next_state="wait",
                score=80,
                params={"time": 10, "next_state": "chase"}
            ))

        # 2️⃣ Approaching edge of platform → stop/wait
        if self.entity.dir[0] < 0:
            x = self.entity.hitbox.left - 5
        else:
            x = self.entity.hitbox.right + 5

        if not self.entity.game_objects.collisions.check_ground([x, self.entity.hitbox.bottom + 5]):
            results.append(Decision(
                next_state="wait",
                score=90,
                params={"time": 60, "next_state": "patrol", 'dir':-1}
            ))

        return results
