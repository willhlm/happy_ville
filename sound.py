import pygame

class Sound():
    def __init__(self):
        pass
        pygame.mixer.init()
        self.initiate_channels(8)

    def initiate_channels(self, quantity):
        self.channels = []
        for i in range(quantity):
            self.channels.append(pygame.mixer.Channel(i))
        self.channels[0].set_volume(1)

    #note channel 0 should be used for level bg music
    def play_sound(self, channel):
        pass

    def play_bg_sound(self):
        self.channels[0].play(self.bg, loops = -1, fade_ms = 500)

    def pause_bg_sound(self):
        self.channels[0].fadeout(1000)

    def remove_sounds(self, channel):
        pass

    def load_sound(self, name):
        pass

    def load_bg_sound(self, name):
        self.bg = pygame.mixer.Sound("Audio/maps/" + name + "/bg_1.mp3")

    #list general sounds that  can always be loaded and played
