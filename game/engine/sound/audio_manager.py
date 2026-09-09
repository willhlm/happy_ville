import pygame
pygame.mixer.init()
from engine.utils import read_files
from engine.system.game_settings import GameSettings

class AudioManager:
    """Low-level audio channel and volume management"""
    def __init__(self, config):        
        self.config = config
        self.volume_settings = read_files.read_json('config/game_settings.json')['sounds']
        
        pygame.mixer.set_num_channels(config['total_channels'])
        self._setup_reserved_channels()
        
    def _setup_reserved_channels(self):
        self.reserved_channels = []
        for i in range(self.config['reserved_channels']):
            channel = pygame.mixer.Channel(i)
            pygame.mixer.set_reserved(i)
            self.reserved_channels.append(channel)
    
    def get_available_channel(self, force=True):
        return pygame.mixer.find_channel(force)
    
    def get_reserved_channel(self, index):
        if 0 <= index < len(self.reserved_channels):
            return self.reserved_channels[index]
        raise IndexError(f"Reserved channel {index} doesn't exist")
    
    def find_free_reserved_channel(self):
        for channel in self.reserved_channels:
            if not channel.get_busy():
                return channel
        return None
    
    def calculate_volume(self, base_volume, category):
        """Apply the player's 0--10 category and overall settings to a base volume."""
        category_multiplier = self.get_volume_multiplier(category)
        overall_multiplier = self.get_volume_multiplier("overall")
        return base_volume * category_multiplier * overall_multiplier

    def get_volume_multiplier(self, category):
        """Return a player-facing 0--10 setting as a 0.0--1.0 multiplier."""
        setting = self.volume_settings.get(category, 10)
        return max(0, min(10, setting)) / 10.0
    
    def update_volume_setting(self, category, amount):
        self.volume_settings[category] += amount
        self.volume_settings[category] = max(
            GameSettings.VOLUME_OPTIONS[0],
            min(GameSettings.VOLUME_OPTIONS[-1], self.volume_settings[category]),
        )
