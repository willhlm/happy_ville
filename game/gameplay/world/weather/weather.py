import pygame, random
from engine.utils import read_files
from . import weather_states, weatherfx_states
from gameplay.entities.visuals.particles.screen_particles import ScreenParticles

class Weather():#initialied in game_objects: a container of weather objects
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.wind = WindManager(game_objects)
        self.fog = FogManager(game_objects)
        self.rain = RainManager(game_objects)
        self.snow = SnowManager(game_objects)

    def update(self, dt):#called from game_obejcts
        self.wind.update(dt)
        self.fog.update(dt)
        self.rain.update(dt)
        self.snow.update(dt)

    def empty(self):#called from game_objects
        self.wind.empty()
        self.fog.empty()
        self.rain.empty()  
        self.snow.empty()    

    def flash(self):
        self.game_objects.cosmetics.add(FlashFX(self.game_objects))     

class WeatherManagers():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.fx_by_layer = {}
        self.configs = {}
        self.currentstate = weather_states.Idle(self)

    def update(self, dt):        
        self.currentstate.update(dt)

    def add_fx(self, fx):#called from maploader
        self.fx_by_layer.setdefault(fx.layer_name, []).append(fx)

    def configure(self, layer_name, config):
        self.configs[layer_name] = config.copy()

    def get_fx(self, layer_name):
        return self.fx_by_layer.get(layer_name, [])

    def empty(self):
        self.fx_by_layer = {}
        self.configs = {}

class WindManager(WeatherManagers):#will handle winds in all layers, and common things such as velocity, soudns etc.
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)
        self.active_wind = {}
        self.channel = None
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/environments/wind/')
        self.currentstate = weather_states.IdleWind(self)

    def get_velocity(self, layer_name):
        return self.active_wind.get(layer_name, {}).get('velocity', [0, 0])

    def get_lifetime(self, layer_name):
        return self.active_wind.get(layer_name, {}).get('lifetime', 0)

    def start_wind(self):#called from weather_states
        if self.channel is None:
            self.channel = self.game_objects.sound.play_sfx(self.sounds['idle'][0], loop = -1, fade = 1000, vol = 0.2)

        for layer_name, config in self.configs.items():
            duration_range = config.get('duration_range', [180, 420])
            self.active_wind[layer_name] = {
                'velocity': config.get('velocity', [0, 0]).copy(),
                'lifetime': random.randint(*duration_range),
            }
            for windfx in self.get_fx(layer_name):
                windfx.activate()

    def stop_wind(self, layer_name = None):#stopped from weather_states
        if layer_name is None:
            layers = list(self.active_wind.keys())
        else:
            layers = [layer_name]

        for current_layer in layers:
            self.active_wind.pop(current_layer, None)
            for windfx in self.get_fx(current_layer):
                windfx.deactivate()

        if not self.active_wind and self.channel is not None:
            self.game_objects.sound.fade_channel(self.channel)
            self.channel = None

    def empty(self):
        self.stop_wind()
        self.active_wind = {}
        self.currentstate = weather_states.IdleWind(self)
        super().empty()

class FogManager(WeatherManagers):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)

class RainManager(WeatherManagers):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)      

class SnowManager(WeatherManagers):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects)                     
    
class WeatherFX(pygame.sprite.Sprite):#make a layer on screen, then use shaders to generate stuff
    def __init__(self, game_objects, parallax, layer_name = ""):
        super().__init__()
        self.game_objects = game_objects
        self.parallax = parallax
        self.layer_name = layer_name
        self.currentstate = weatherfx_states.Idle(self)

    def update_render(self, dt):
        self.currentstate.update_render(dt)

    def draw(self, target):
        self.currentstate.draw(target)

    def release_texture(self):
        pass

class WindFX(WeatherFX):#the shader that will draw things: will be added in all_bg/fg s
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, kwarg.get('parallax', [1,1]), kwarg.get('layer_name', ""))
        self.image = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)

    def activate(self):
        self.currentstate.enter_state('wind')

    def deactivate(self):
        self.currentstate.enter_state('idle')

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

class FogFX(WeatherFX):
    def __init__(self, game_objects, parallax, **kwarg):
        super().__init__(game_objects, parallax, kwarg.get('layer_name', ""))
        self.image = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.noise_layer = game_objects.game.display.make_layer(game_objects.game.window_size)        
        self.time = 0
        self.colour = kwarg.get('colour', (1,1,1,1))

    def update_render(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.005
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.game_objects.game.window_size
        self.game_objects.shaders['noise_perlin']['scale'] = (10,10)
        self.game_objects.shaders['noise_perlin']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0]*self.parallax[0],self.game_objects.camera_manager.camera.scroll[1]*self.parallax[1]]

        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader = self.game_objects.shaders['noise_perlin'])
        self.game_objects.shaders['fog']['noise'] = self.noise_layer.texture
        self.game_objects.shaders['fog']['TIME'] = self.time * 0.001
        self.game_objects.shaders['fog']['fog_color'] = self.colour
        self.game_objects.shaders['fog']['scroll'] = [self.game_objects.camera_manager.camera.scroll[0]*self.parallax[0],self.game_objects.camera_manager.camera.scroll[1]*self.parallax[1]]
        
        self.game_objects.game.display.render(self.image.texture, target, shader = self.game_objects.shaders['fog'])                    

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

class RainFX(ScreenParticles):
    def __init__(self, game_objects, parallax, number_particles = 20, layer_name = "", **kwarg):
        super().__init__(game_objects, parallax, number_particles)
        self.layer_name = layer_name
        size = 5
        width = int(game_objects.game.window_size[0] + 2*size)#size of the canvas
        height = int(game_objects.game.window_size[1] + 2*size)#size of the canvas
        self.image = game_objects.game.display.make_layer((width, height))        

        self.shader = self.game_objects.shaders['screen_rectangle']
        self.shader['size'] = self.image.texture.size
        self.shader['number_particles'] = self.number_particles
        self.shader['angle'] = 0#rotation angle of the rectangle
        colours=[(10,191,255,255),(152,245,255,255),(61,89,171,255),(100,149,237,255)]
        self.shader['colour'] = colours[random.randint(0, len(colours)-1)]
        self.shader['scale'] = (self.parallax[0], self.parallax[0])

    def set_parameters(self):#parameters needed for the shader
        self.canvas_size = self.parallax[0]
        self.centers, self.velocity = [], []#make a list of stuff keep info as "attributes"
        for i in range(0, self.number_particles):
            x = random.uniform(-self.canvas_size, self.game_objects.game.window_size[0] + self.canvas_size)
            y = random.uniform(-self.canvas_size, self.game_objects.game.window_size[1] + self.canvas_size)
            self.centers.append([x,y])
            self.velocity.append([0,0])

    def draw(self, target):
        self.shader['parallax'] = self.parallax
        self.shader['centers'] = self.centers
        self.shader['scroll'] = self.game_objects.camera_manager.camera.scroll
        self.game_objects.game.display.render(self.image.texture, target, shader = self.shader)#shader render

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [-1, 5]        

class SnowFX(RainFX):
    def __init__(self, game_objects, parallax, number_particles, layer_name = "", **kwarg):
        super().__init__(game_objects, parallax, number_particles, layer_name = layer_name, **kwarg)
        self.shader['colour'] = (255,255,255,255)
        self.shader['scale'] = (self.parallax[0]*2,self.parallax[0]*0.33)#to make it square

    def draw(self, target):
        self.shader['centers'] = self.centers
        super().draw(target)

    def update_vel(self, i):#how it should move
        self.velocity[i]  = [0.5*math.cos(self.time*0.01), 1]

class FlashFX(WeatherFX):#white colour fades out and then in
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, kwarg.get('parallax', [1,1]))
        self.fade_length = 100
        self.image.clear(255,255,255,int(170/self.fade_length))
        self.add_light_source()
        self.time = 0
 
    def update_render(self, dt):
        self.time += dt
        self.update_image()
        if self.time > self.fade_length:
            self.kill()
            self.game_objects.lights.remove_light(self.light)         

    def add_light_source(self):
        radius = self.game_objects.game.window_size[0] * 0.5
        position = [self.game_objects.camera_manager.camera.scroll[0] + self.game_objects.game.window_size[0] * 0.5, self.game_objects.camera_manager.camera.scroll[1] + self.game_objects.game.window_size[1]*0.5]#put a bg light in center
        self.hitbox = pygame.Rect(0, 0, self.game_objects.game.window_size[0], self.game_objects.game.window_size[1])#for the light source
        self.hitbox.center = position
        self.light = self.game_objects.lights.add_light(target = self ,radius = radius, fade = True, lifetime = True)#put a bg light in center        

    def update_image(self):
        alpha = int((self.fade_length - self.time)*(255/self.fade_length))
        self.image.clear(255,255,255,alpha)
        self.hitbox.center = [self.game_objects.camera_manager.camera.scroll[0] + self.game_objects.game.window_size[0] * 0.5, self.game_objects.camera_manager.camera.scroll[1] + self.game_objects.game.window_size[1]*0.5]#put a bg light in center       

    def draw(self, target):
        self.game_objects.game.display.render(self.image.texture, target)#shader render

    @classmethod
    def pool(cls, game_objects):
        cls.image = game_objects.game.display.make_layer(game_objects.game.window_size)
