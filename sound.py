import pygame
pygame.mixer.init()#this one is needed to avoid a delay when playing the sounds

class Sound():#class for organising sound and music playback
    def __init__(self):#channels 0 - 4 is dedicated to
        self.reserved_channels = 4
        self.initiate_channels(8)

    def initiate_channels(self, quantity):#note channel 0 should be used for level bg music
        self.channels = []
        for i in range(quantity):
            self.channels.append(pygame.mixer.Channel(i))
            if i < self.reserved_channels:
                pygame.mixer.set_reserved(i)
        self.channels[0].set_volume(1)

    def play_bg_sound(self):
        self.channels[0].set_volume(1)
        self.channels[0].play(self.bg, loops = -1, fade_ms = 300)

    def pause_bg_sound(self):
        self.channels[0].fadeout(700)

    def load_bg_sound(self, name):
        self.bg = pygame.mixer.Sound("Audio/maps/" + name + "/default.mp3")
        self.bg.set_volume(1)

    @staticmethod
    def play_sfx(sfx):#finds an available channel and playts SFX sounds, takes mixer.Sound objects
        channel = pygame.mixer.find_channel()
        try:
            channel.set_volume(0.2)
            channel.play(sfx)
        except:
            print("No available channels")

    def play_sound(self, sfx):
        pass

    def pause_sound(self, channel):
        pass

    def load_sound(self, name):
        pass

    #list general sounds that  can always be loaded and played
