from .progression_statue import ProgressionStatue


class AbilityUpgradeStatue(ProgressionStatue):
    ability_key = None

    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.progression = self.game_objects.player.progression
        self.refresh_state()

    def is_complete(self):
        return not self.progression.can_upgrade(self.ability_key)

    def grant_progression(self):
        self.progression.upgrade(self.ability_key)

    def get_text(self):
        if self.is_complete():
            return self.progression.get_current_description(self.ability_key)
        return self.progression.get_next_upgrade_description(self.ability_key)


class ThunderAbilityUpgradeStatue(AbilityUpgradeStatue):
    ability_key = 'thunder'
    sprite_path = 'assets/sprites/entities/interactables/statues/abilities/thunder_dive_statue/'
    preview_sprite = 'thunder_main'
