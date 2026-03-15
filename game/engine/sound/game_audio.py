from __future__ import annotations

import pygame
from typing import Callable, Dict

from .sound_library import SFXLibrary, MusicLibrary
from .audio_manager import AudioManager
from .sound_player import SoundPlayer
from .config import AUDIO_CONFIG
from .spatial_emitter import SpatialAudioSystem

class GameAudio:
    """High-level game audio interface + simple spatial emitters."""
    def __init__(self):
        self.audio_manager = AudioManager(AUDIO_CONFIG)
        self.sound_player = SoundPlayer(self.audio_manager)
        self.spatial = SpatialAudioSystem(self.sound_player.play_sfx)

        # Sound libraries
        self.sfx_library = SFXLibrary()
        self.music_library = MusicLibrary()

    # ----------------------------
    # Existing high-level methods
    # ----------------------------
    def play_weapon_hit(self, weapon_type, material, volume=0.3):
        sound = self.sfx_library.get_impact_sound(weapon_type, material)
        return self.sound_player.play_sfx(sound, volume)

    def play_ui_sound(self, ui_event, volume=0.4):
        sound = self.sfx_library.get_ui_sound(ui_event)
        return self.sound_player.play_sfx(sound, volume)

    def play_background_sound(self, track, volume=0.7, index=0, loop=-1, fade=300):
        return self.sound_player.play_priority_sound(track, volume, channel_index=index, fade_ms=fade, loops=loop)

    def change_volume(self, category, amount):
        self.audio_manager.update_volume_setting(category, amount)

    def play_sfx(self, sfx, loop=0, vol=1, fade=0):
        return self.sound_player.play_sfx(sfx, loops=loop, volume=vol, fade_ms=fade)

    def get_sfx(self, weapon_type, material):
        return self.sfx_library.get_impact_sound(weapon_type, material)

    def fade_all_music(self, fade_time=700):
        for channel in self.audio_manager.reserved_channels:
            self.fade_channel(channel, fade_time)

    def fade_channel(self, channel, fade_time=700):
        channel.fadeout(fade_time)

    def queue_sound(self, sound, channel_index):
        channel = self.audio_manager.get_reserved_channel(channel_index)
        channel.queue(sound)

    # ----------------------------
    # Spatial audio API
    # ----------------------------
    def register_spatial_point(self, sound, get_point, **kwargs):
        return self.spatial.register_point(sound, get_point, **kwargs)

    def register_spatial_rect(self, sound, get_rect, **kwargs):
        return self.spatial.register_rect(sound, get_rect, **kwargs)

    def unregister_emitter(self, emitter_id, fade_ms = 1000):
        return self.spatial.unregister(emitter_id, fade_ms=fade_ms)

    def update_render(self, listener_pos):
        return self.spatial.update(listener_pos)