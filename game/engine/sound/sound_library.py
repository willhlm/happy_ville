import pygame
from engine.utils import read_files

class SFXLibrary:
    """Manages game sound effects"""
    
    def __init__(self, sounds_path='assets/audio/sfx/entities/shared/'):
        self.sounds = read_files.load_sounds_dict(sounds_path)
        self._build_sound_maps()
    
    def _build_sound_maps(self):
        self.impact_sounds = {
            ("sword", "flesh"): self.sounds.get('sword_flesh'),
            ("bow", "flesh"): self.sounds.get('arrow_flesh'),
            ("sword", "metal"): self.sounds.get('sword_metal'),
            # Add more mappings as needed
        }
        
        self.ui_sounds = {
            "menu_select": self.sounds.get('menu_select'),
            "menu_confirm": self.sounds.get('menu_confirm'),
            # Add UI sounds
        }
    
    def get_impact_sound(self, weapon_type, material):
        return self.impact_sounds.get((weapon_type, material))
    
    def get_ui_sound(self, ui_event):
        return self.ui_sounds.get(ui_event)
    
    def get_sound(self, sound_type, *args):
        if sound_type == "impact":
            return self.get_impact_sound(*args)
        elif sound_type == "ui":
            return self.get_ui_sound(*args)
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