import pygame
pygame.mixer.init()#this one is needed to avoid a delay when playing the sounds
import Read_files

class Sound():#class for organising sound and music playback
    def __init__(self):#channels 0 - 4 is dedicated to        
        self.reserved_channels = 4
        self.initiate_channels(8)
        self.volume = game_settings = Read_files.read_json('game_settings.json')['sounds']     

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

    def intensity_music(self, int):
        self.volume['music'] += int
        self.volume['music'] = min(self.volume['music'],10)
        self.volume['music'] = max(self.volume['music'],0)        
        self.channels[0].set_volume(self.volume['music'] * 0.1)   

    def intensity_SFX(self, int):
        self.volume['SFX'] += int
        self.volume['SFX'] = min(self.volume['SFX'],10)
        self.volume['SFX'] = max(self.volume['SFX'],0)        

    def intensity_overall(self, int):
        self.volume['overall'] += int
        self.volume['overall'] = min(self.volume['overall'],10)
        self.volume['overall'] = max(self.volume['overall'],0)          
        self.intensity_SFX(int)
        self.intensity_music(int)

    def pause_bg_sound(self):
        self.channels[0].fadeout(700)

    def load_bg_sound(self, name):
        self.bg = pygame.mixer.Sound("Audio/maps/" + name + "/default.mp3")
        self.bg.set_volume(1)

    def play_sfx(self, sfx, loop = 0, vol = 0.2):#finds an available channel and playts SFX sounds, takes mixer.Sound objects
        channel = pygame.mixer.find_channel()
        try:
            channel.set_volume(vol * self.volume['SFX'] * 0.1)
            channel.play(sfx, loops = loop)
        except:
            print("No available channels")

        return channel

    def play_sound(self, sfx):
        pass

    def pause_sound(self, channel):
        pass

    def load_sound(self, name):
        pass

    #list general sounds that  can always be loaded and played
