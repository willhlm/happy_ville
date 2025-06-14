import pygame
import read_files
from states import weather_states, weatherfx_states

class Weather():#initialied in game_objects
    def __init__(self, game_objects):
        self.wind = WindManager(game_objects)
        self.fog = FogManager(game_objects)
        self.rain = RainManager(game_objects)

    def update(self):
        self.wind.update()
        self.fog.update()
        self.rain.update()

class WeatherManagers():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.fx_list = []#add windfx from map loader
        self.currentstate = weather_states.Idle(self)

    def update(self):        
        self.currentstate.update()

    def add_fx(self, fx):#called from maploader
        self.fx_list.append(fx)

class WindManager(WeatherManagers):#will handle winds in all layers, and common things such as velocity, soudns etc.
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.velocity = [0, 0]
        self.lifetime = 0
        self.sounds = read_files.load_sounds_dict('audio/SFX/environment/wind/')
        self.currentstate = weather_states.IdleWind(self)

    def start_wind(self, velocity, lifetime):#called from currentstate
        self.velocity = velocity
        self.lifetime = lifetime
        self.channel = self.game_objects.sound.play_sfx(self.sounds['idle'][0], loop = -1, fade = 1000, vol = 0.2)
        for windfx in self.fx_list:
            windfx.activate()

    def stop_wind(self):#stopped from currentstate
        self.velocity = [0, 0]
        self.lifetime = 0
        self.game_objects.sound.fade_sound(self.channel)
        for windfx in self.fx_list:
            windfx.deactivate()      

class FogManager(WeatherManagers):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)

class RainManager(WeatherManagers):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)              
    
class WeatherFX(pygame.sprite.Sprite):#make a layer on screen, then use shaders to generate stuff
    def __init__(self, game_objects, parallax):
        super().__init__()
        self.game_objects = game_objects
        self.parallax = parallax
        self.currentstate = weatherfx_states.Idle(self)

    def update(self):
        self.currentstate.update()

    def draw(self, target):
        self.currentstate.draw(target)

class WindFX(WeatherFX):#the shader that will draw things: will be added in all_bg/fg s
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, kwarg.get('parallax', [1,1]))
        self.image = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.shader = game_objects.shaders['wind']        

    def activate(self):
        self.currentstate.enter_state('wind')

    def deactivate(self):
        self.currentstate.enter_state('idle')
