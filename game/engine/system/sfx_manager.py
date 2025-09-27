from engine.utils import read_files

class SFXManager():
    def __init__(self):

        # Map of (weapon_type, material) -> hit sound
        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/shared/')
        self.impact_sounds = {
            ("sword", "flesh"): sounds['sword_flesh'],
        }

    def weapon_hit(self, weapon_type, material):
        key = (weapon_type, material)
        return self.impact_sounds[key]