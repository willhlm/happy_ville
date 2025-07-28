import pygame, math, random

class Lights():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.ambient = [0, 0, 0, 0]#ambient colour
        self.lights_sources = []#append lights
        self.shaders = {'light':game_objects.shaders['light'],'blur':game_objects.shaders['blur'],'blend':game_objects.shaders['blend']}

        self.shaders['light']['resolution'] = self.game_objects.game.window_size        

        self.layer1 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer2 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer3 = game_objects.game.display.make_layer(game_objects.game.window_size)

        self.normal_map = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.max_light_sources = 20#a valuehard coded in light shader
        self.update(0)

    def new_map(self):#called when loading a new map from map loader
        self.clear_lights()
        self.ambient = [0, 0, 0, 0]

    def clear_normal_map(self):#called at the begning of draw in game objects
        self.normal_map.clear(0, 0, 0, 0)

    def update(self, dt):
        self.normal_interact = [0] * self.max_light_sources
        self.num_rectangle = [0] * self.max_light_sources
        self.points = []
        self.positions = [(0, 0)] * self.max_light_sources
        self.radius = [0] * self.max_light_sources
        self.colour = [[0, 0, 0, 0]] * self.max_light_sources
        self.start_angle = [0] * self.max_light_sources
        self.end_angle = [0] * self.max_light_sources
        self.min_radius = [0] * self.max_light_sources

        for i, light in enumerate(self.lights_sources):        # Process each light source and update the lists
            light.update()  # Update the light source            
            
            self.positions[i] = (light.position[0], self.game_objects.game.window_size[1] - light.position[1])  # Get the positions of the lights
            self.radius[i] = light.radius
            self.colour[i] = light.colour
            self.start_angle[i] = light.start_angle
            self.end_angle[i] = light.end_angle
            self.min_radius[i] = light.min_radius
            self.normal_interact[i] = light.normal_interact
            self.list_points(light, i)  # Sort the collision points into a list
                
        self.points.extend([(0, 0)] * (self.max_light_sources * 4 - len(self.points)))# Add (0, 0) to the list until it reaches length self.max_light_sources*4

    def list_points(self, light, index):
        if not light.platform_interact: 
            self.num_rectangle[index] = 0  # Set num_rectangle[index] to 0 if no platform interaction
            self.points.extend([(0, 0)] * 4)
        else:
            platforms = self.game_objects.collisions.sprite_collide(light, self.game_objects.platforms)  # Collision -> collision occurs at coordinates as per tiled position
            self.num_rectangle[index] = len(platforms)  # Set num_rectangle[index] to the number of collided platforms            
            self.points.extend(self.get_points(platforms))  # Get the collision points and set them at index                       

    def get_points(self, platforms):
        l = []
        for rec in platforms:
            l += [
                (rec.hitbox.topleft[0] - self.game_objects.camera_manager.camera.scroll[0], rec.hitbox.topleft[1] - self.game_objects.camera_manager.camera.scroll[1]),
                (rec.hitbox.topright[0] - self.game_objects.camera_manager.camera.scroll[0], rec.hitbox.topright[1] - self.game_objects.camera_manager.camera.scroll[1]),
                (rec.hitbox.bottomright[0] - self.game_objects.camera_manager.camera.scroll[0], rec.hitbox.bottomright[1] - self.game_objects.camera_manager.camera.scroll[1]),
                (rec.hitbox.bottomleft[0] - self.game_objects.camera_manager.camera.scroll[0], rec.hitbox.bottomleft[1] - self.game_objects.camera_manager.camera.scroll[1])
            ]
        return l

    def clear_lights(self):
        self.lights_sources = []

    def add_light(self, target, **properties):
        if len(self.lights_sources) == self.max_light_sources: return#maximum 20
        light = Light(self.game_objects, target, **properties)
        self.lights_sources.append(light)
        self.shaders['light']['num_lights'] = len(self.lights_sources)  
        return light

    def remove_light(self, light):
        self.lights_sources.remove(light)
        self.shaders['light']['num_lights'] = len(self.lights_sources)

    def draw(self, target):    
        self.shaders['light']['rectangleCorners'] = self.points
        self.shaders['light']['lightPositions'] = self.positions
        self.shaders['light']['lightRadii'] = self.radius
        self.shaders['light']['colour'] = self.colour
        self.shaders['light']['ambient'] = self.ambient
        self.shaders['light']['angleStart'] = self.start_angle
        self.shaders['light']['angleEnd'] = self.end_angle
        self.shaders['light']['min_radius'] = self.min_radius
        self.shaders['light']['num_rectangle'] = self.num_rectangle
        self.shaders['light']['normal_interact'] = self.normal_interact
        self.shaders['light']['normal_map'] = self.normal_map.texture

        self.shaders['blend']['background'] = self.game_objects.game.screen.texture     
        self.shaders['blur']['blurRadius'] = 5

        self.game_objects.game.display.use_alpha_blending(False)#need to turn of blending to remove black outline in places with no ambient dark. It looks beter if it is always True for dark areas
        self.game_objects.game.display.render(self.layer1.texture, self.layer2, shader = self.shaders['light'])
        self.game_objects.game.display.render(self.layer2.texture, self.layer3, shader = self.shaders['blur'])
        self.game_objects.game.display.use_alpha_blending(True)#turn it back on for rendering on screen
        self.game_objects.game.display.render(self.layer3.texture, self.game_objects.game.screen, shader = self.shaders['blend'])

class Light():#light source
    def __init__(self, game_objects, target, **properties):
        self.game_objects = game_objects
        self.init_radius = properties.get('radius',150)#colour
        self.radius = properties.get('radius',150)#colour
        self.colour = properties.get('colour',[1,1,1,1])#colour
        self.start_angle = properties.get('start_angle',0)
        self.end_angle = properties.get('end_angle', 360)
        self.min_radius = properties.get('min_radius',0)
        self.max_radius = properties.get('max_radius',300)
        self.expand_speed = properties.get('expand_speed',100)
        self.parallax = properties.get('parallax',[1,1])

        self.platform_interact = properties.get('platform_interact', False)#colour#if it should interact with platforms
        self.normal_interact = float(properties.get('normal_interact', True))#a flag to check if it should interact with normal maps
        self.shadow_interact = properties.get('shadow_interact', False)#a flag to check if it should collide with light based stuff (dark forest platform, enemy)

        self.time = 0

        self.target = target
        self.position = target.hitbox.center#the blit position                     
        self.hitbox = pygame.Rect(self.position[0]-self.radius,self.position[1]-self.radius,self.radius*2,2*self.radius)
        self.rect = self.hitbox.copy()            

        self.updates = [self.follow_target]#self.fade, self.pulsating#can decide what to do by appending things here
        self.update_functions = {'flicker': self.flicker, 'fade': self.fade, 'pulsating': self.pulsating, 'expand': self.expand, 'lifetime': self.lifetime}
        for prop, func in self.update_functions.items():
            if properties.get(prop, False):
                self.updates.append(func)

    def expand(self):
        self.radius += self.game_objects.game.dt*self.expand_speed
        self.radius = min(self.radius, self.max_radius)
        self.hitbox[2], self.hitbox[3] = 2*self.radius, 2*self.radius

    def flicker(self):
        flickerrange = 0.1
        self.colour[-1] += random.uniform(-flickerrange, flickerrange)
        self.colour[-1] = max(0, min(1, self.colour[-1]))#clamp it between 0 and 1

    def fade(self, rate = 0.99):
        self.colour[-1] *= rate

    def pulsating(self):#
        self.time += self.game_objects.game.dt * 0.01
        self.radius = 0.5 * self.init_radius * math.sin(self.time) + self.init_radius * 0.5

    def lifetime(self):
        if self.colour[-1] < 0.01:
            self.game_objects.lights.remove_light(self)
            #self.target.state.handle_input('light_gone')

    def follow_target(self):
        self.hitbox.center = self.target.hitbox.center
        self.position = [self.hitbox.center[0] - self.parallax[0] * self.game_objects.camera_manager.camera.scroll[0],self.hitbox.center[1] - self.parallax[1] * self.game_objects.camera_manager.camera.scroll[1]]#te shader needs tye position without the scroll (i.e. "on screen" values)

    def add_decorator(self, key):
        self.updates.append(self.update_functions[key])

    def update(self, dt):#if they e.g. fade
        for update in self.updates:
            update()