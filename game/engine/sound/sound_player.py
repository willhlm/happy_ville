import pygame

class SoundPlayer():
    """Handles the actual playing of sounds with different strategies"""
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self._priority_channel_index = 0
    
    def play_sfx(self, sound, volume=0.2, loops=0, fade_ms=0):
        """Play a sound effect on any available channel"""
        channel = self.audio_manager.get_available_channel(True)
        final_volume = self.audio_manager.calculate_volume(volume, 'SFX')

        channel.set_volume(final_volume)
        channel.play(sound, loops=loops, fade_ms=fade_ms)
        return channel
    
    def play_priority_sound(self, sound, volume=0.7, channel_index=None, loops=-1, fade_ms=300):
        """Play sound on reserved channel with priority management"""
        if channel_index is None:
            # Find free channel or use round-robin
            channel = self.audio_manager.find_free_reserved_channel()
            if channel is None:
                channel = self.audio_manager.get_reserved_channel(self._priority_channel_index)
                self._priority_channel_index = (self._priority_channel_index + 1) % self.audio_manager.config['reserved_channels']
        else:
            channel = self.audio_manager.get_reserved_channel(channel_index)
        
        channel.stop()  # Stop any existing sound
        final_volume = self.audio_manager.calculate_volume(volume, 'music')
        channel.set_volume(final_volume)
        channel.play(sound, loops=loops, fade_ms=fade_ms)
        return channel
