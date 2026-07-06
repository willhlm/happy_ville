import random
from engine.utils import read_files

class SFXLibrary:
    """Manages game sound effects"""
    
    def __init__(self):
        impact_sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/shared/impact/')
        enemy_shared_sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/shared/')
        spawn_sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/shared/spawn/')
        ui_sounds = read_files.load_sounds_dict('assets/audio/sfx/ui/')
        item_sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/shared/items/')
        self._build_sound_maps(impact_sounds, enemy_shared_sounds, spawn_sounds, ui_sounds, item_sounds)
    
    def _build_sound_maps(self, impact_sounds, enemy_shared_sounds, spawn_sounds, ui_sounds, item_sounds):
        self.impact_sounds = {
            ("sword", "flesh"): impact_sounds.get('sword_flesh'),
            ("bow", "flesh"): impact_sounds.get('arrow_flesh'),
            ("sword", "metal"): impact_sounds.get('sword_metal'),
            ("sword", "wood"): impact_sounds.get('sword_wood'),
            ("stone", "flesh"): impact_sounds.get('stone_flesh'),
            ("sword", "stone"): impact_sounds.get('sword_stone'),
        }

        self.item_sounds = {
            'interact': item_sounds.get('interact'),
        }        

        self.enemy_death_sounds = {
            "killed": enemy_shared_sounds.get('killed'),
            "dead": enemy_shared_sounds.get('dead'),
        }

        self.spawn_sounds = {
            "enemy_spawn": spawn_sounds.get("enemy_spawn"),
        }
        
        self.ui_sounds = {
            "select": ui_sounds.get('select'),
            "confirm": ui_sounds.get('confirm'),
            "on_select": ui_sounds.get('on_select'),
            "narrative_text": ui_sounds.get('narrative_text'),
            # Add UI sounds
        }

    def _pick_sound(self, sound_or_list):
        return random.choice(sound_or_list)
    
    def get_item_sound(self, event):
        return self._pick_sound(self.item_sounds.get(event))

    def get_impact_sound(self, weapon_type, material):
        return self._pick_sound(self.impact_sounds.get((weapon_type, material)))

    def get_enemy_death_sound(self, event):
        return self._pick_sound(self.enemy_death_sounds.get(event))

    def get_spawn_sound(self, event):
        return self._pick_sound(self.spawn_sounds.get(event))
    
    def get_ui_sound(self, ui_event):
        return self._pick_sound(self.ui_sounds.get(ui_event))
    
    def get_sound(self, sound_type, *args):
        if sound_type == "impact":
            return self.get_impact_sound(*args)
        elif sound_type == "enemy_death":
            return self.get_enemy_death_sound(*args)
        elif sound_type == "spawn":
            return self.get_spawn_sound(*args)
        elif sound_type == "ui":
            return self.get_ui_sound(*args)
        elif sound_type == "item":
            return self.get_item_sound(*args)            
        return None

class MusicLibrary:
    """Manages background music and ambient sounds"""
    
    def __init__(self, music_path='assets/audio/music/'):
        self.music_tracks = read_files.load_sounds_dict(music_path)
        self.ambient_sounds = {}
    
    def get_track(self, track_name):
        return self.music_tracks.get(track_name)
    
    def get_ambient(self, ambient_name):
        return self.ambient_sounds.get(ambient_name)
    
    def get_sound(self, sound_type, name):
        if sound_type == "track":
            return self.get_track(name)
        elif sound_type == "ambient":
            return self.get_ambient(name)
        return None
