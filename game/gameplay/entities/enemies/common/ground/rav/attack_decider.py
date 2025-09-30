class AttackDecider:
    def __init__(self, manager):
        self.manager = manager
        self.entity = manager.entity

    def choose_attack(self, player_distance):
        """Decide which attack to use based on player position and cooldowns"""
        # Jump attack if player is slightly above and within range
        if (abs(player_distance[0]) < self.entity.jump_distance[0] and player_distance[1] < -10):  # player is above (negative Y)
            if self.manager.cooldowns.get('jump_attack') <= 0:
                return 'jump_attack_pre'

        # Melee attack if player is very close
        if abs(player_distance[0]) < self.entity.attack_distance[0]:
            if self.manager.cooldowns.get('melee_attack') <= 0:
                return 'attack_pre'

        return None