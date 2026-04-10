from .progression_statue import ProgressionStatue


class AirDashUpgradeStatue(ProgressionStatue):
    sprite_path = 'assets/sprites/entities/interactables/statues/abilities/air_dash_statue/'
    preview_sprite = 'air_dash_main'

    def is_complete(self):
        return self.game_objects.player.progression.is_unlocked('air_dash')

    def grant_progression(self):
        self.game_objects.player.progression.unlock('air_dash')

    def get_text(self):
        return 'dash in air'
