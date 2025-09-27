import pygame
pygame.mixer.init()#this one is needed to avoid a delay when playing the sounds
from engine.utils import read_files
from engine.system.sfx_manager import SFXManager

class Sound():#class for organising sound and music playback
    def __init__(self):
        self.volume = read_files.read_json('saves/game_settings.json')['sounds']
        pygame.mixer.set_num_channels(20)#create X channels, #number of sounds we will simultanioulsy play
        self.reserved_channels = 4
        self.initiate_channels(self.reserved_channels)#need to be smaller than numver of channels
        self.index = 0#a pointer so that priority sounds to not overlap
        self._sfx_manager = SFXManager()

    def initiate_channels(self, reserved_channels = 4):#note channel 0 should be used for level bg music
        self.channels = []
        for i in range(reserved_channels):
            channel = pygame.mixer.Channel(i)
            channel.set_volume(self.volume['music'] * 0.1)
            pygame.mixer.set_reserved(i)
            self.channels.append(channel)

    def play_priority_sound(self, sfx, vol = 0.7, index = 0, loop = -1, fade = 300):
        if self.index == index:#look for an empty priority channel. If it doesn't exits, take the supplised index
            for i in range(self.reserved_channels):
                channel = self.channels[i]
                if not channel.get_busy():
                    self.index = i
                    break
            else:
                self.index = index
        else:
            self.index = index
            channel = self.channels[self.index]

        channel.stop()#to avoid any lingering fade effect
        channel.set_volume(vol * self.volume['music'] * 0.1)
        channel.play(sfx, loops=loop, fade_ms = fade)
        return channel

    def play_sfx(self, sfx, loop = 0, vol = 0.2, fade = 0):#finds an available channel and playts SFX sounds, takes mixer.Sound objects
        channel = pygame.mixer.find_channel(True)#force it to always find a channel. If no available, it will take the channel that has been alive the longest time
        channel.set_volume(vol * self.volume['SFX'] * 0.1)#the 0.1 normalise it to 1
        channel.play(sfx, loops = loop, fade_ms = fade)
        return channel

    def put_in_queue(self,  new_sound, index):#it plays the new sound once without fade after the current one (current as in the one at index)
        self.channels[index].queue(new_sound)

    def fade_sound(self, channel, time = 700):
        channel.fadeout(time)

    def fade_all_sounds(self, time = 700):#when changing biomes
        for i in range(self.reserved_channels):
            channel = self.channels[i]
            self.fade_sound(channel, time)

    def set_volume(self, channel, vol):
        channel.set_volume(vol * self.volume['SFX'] * 0.1)

    def change_volume(self, category, amount):
        self.volume[category] += amount
        self.volume[category] = min(self.volume[category], 10)
        self.volume[category] = max(self.volume[category], 0)

        if category == 'music':
            self.channels[0].set_volume(self.volume['music'] * 0.1)
        elif category == 'SFX':
            pass
        elif category == 'overall':
            self.intensity_music(amount)
            self.intensity_SFX(amount)

    def intensity_music(self, amount):
        self.volume['music'] += amount
        self.volume['music'] = min(self.volume['music'], 10)
        self.volume['music'] = max(self.volume['music'], 0)
        self.channels[0].set_volume(self.volume['music'] * 0.1)

    def intensity_SFX(self, amount):
        self.volume['SFX'] += amount
        self.volume['SFX'] = min(self.volume['SFX'], 10)
        self.volume['SFX'] = max(self.volume['SFX'], 0)

    def get_weapon_hit(self, weapon, material):
        return self._sfx_manager.weapon_hit(weapon, material)