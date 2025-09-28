from .sound_library import SFXLibrary, MusicLibrary
from .audio_manager import AudioManager
from .sound_player import SoundPlayer
from .config import AUDIO_CONFIG

class GameAudio():
    """High-level game audio interface"""    
    def __init__(self):                    
        self.audio_manager = AudioManager(AUDIO_CONFIG)
        self.sound_player = SoundPlayer(self.audio_manager)
        
        # Sound libraries
        self.sfx_library = SFXLibrary()
        self.music_library = MusicLibrary()
    
    # High-level game audio methods
    def play_weapon_hit(self, weapon_type, material, volume=0.3):
        sound = self.sfx_library.get_impact_sound(weapon_type, material)
        self.sound_player.play_sfx(sound, volume)        
    
    def play_ui_sound(self, ui_event, volume=0.4):
        sound = self.sfx_library.get_ui_sound(ui_event)
        self.sound_player.play_sfx(sound, volume)
    
    def play_background_sound(self, track, volume = 0.7, index = 0, loop = -1, fade = 300):
        self.sound_player.play_priority_sound(track, volume, channel_index=index, fade_ms=fade, loops = loop)

    def change_volume(self, category, amount):
        self.audio_manager.update_volume_setting(category, amount)

    #use music objects directly
    def play_sfx(self, sfx, loop = 0, vol = 1, fade = 0):
        self.sound_player.play_sfx(sfx, loops = loop, volume = vol, fade_ms = fade)

    def get_sfx(self, weapon_type, material):
        return self.sfx_library.get_impact_sound(weapon_type, material)        

    def fade_all_music(self, fade_time=700):
        """Fade out all priority channels"""
        for channel in self.audio_manager.reserved_channels:
            self.fade_channel(channel, fade_time)

    def fade_channel(self, channel, fade_time=700):
        """Fade out a specific channel"""
        channel.fadeout(fade_time)

    def queue_sound(self, sound, channel_index):#it plays the new sound once without fade after the current one (current as in the one at index)
        """Queue a sound to play after current sound finishes"""
        channel = self.audio_manager.get_reserved_channel(channel_index)
        channel.queue(sound)        