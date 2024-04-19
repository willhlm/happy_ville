import pygame, math, random

class Lights():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.ambient = (0,0,0,0)#ambient colour
        self.lights_sources = []#append lights
        self.shaders = {'light':game_objects.shaders['light'],'blur':game_objects.shaders['blur'],'blend':game_objects.shaders['blend']}

        self.shaders['light']['resolution'] = self.game_objects.game.window_size
        self.shaders['blur']['blurRadius'] = 5

        self.layer1 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer2 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer3 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.update()

    def new_map(self):#called when loading a new map from map loader
        self.clear_lights()
        self.ambient = (0,0,0,0)

    def update(self):
        self.points, self.positions, self.radius, self.colour = [], [], [], []
        for light in self.lights_sources:
            light.update()
            self.list_points(light)#sort the collisions points into a ligst
            self.positions.append((light.position[0],self.game_objects.game.window_size[1] - light.position[1]))#get te positions of the lights
            self.radius.append(light.radius)
            self.colour.append(light.colour)

    def list_points(self, light):
        if not light.interact: return
        platforms = self.game_objects.collisions.light_collision(light)#collision -> collision occures at coordinates as pe tiled position
        self.shaders['light']['num_rectangle'] = len(platforms)#update numbe rof rectanges -> works if it is only one source
        self.points = self.points + self.get_points(platforms)

    def get_points(self,platforms):
        l = []
        for rec in platforms:
            l = l + [(rec.hitbox.topleft[0] - self.game_objects.camera.scroll[0],rec.hitbox.topleft[1] - self.game_objects.camera.scroll[1]),(rec.hitbox.topright[0] - self.game_objects.camera.scroll[0],rec.hitbox.topright[1] - self.game_objects.camera.scroll[1]),(rec.hitbox.bottomright[0] - self.game_objects.camera.scroll[0],rec.hitbox.bottomright[1] - self.game_objects.camera.scroll[1]),(rec.hitbox.bottomleft[0] - self.game_objects.camera.scroll[0],rec.hitbox.bottomleft[1] - self.game_objects.camera.scroll[1])]
        return l

    def clear_lights(self):
        self.lights_sources = []

    def add_light(self, target, **properties):
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

        self.shaders['blend']['background'] = self.game_objects.game.screen.texture

        self.game_objects.game.display.use_alpha_blending(False)#need to turn of blending to remove black outline
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
        self.interact = properties.get('interact',False)#colour#if it should interact with platforms

        self.target = target

        self.position = target.hitbox.center#the blit position
        self.hitbox = pygame.Rect(self.position[0]-self.radius,self.position[1]-self.radius,self.radius*2,2*self.radius)
        self.rect = self.hitbox.copy()
        self.time = 0

        self.updates = [self.set_pos]#self.fade, self.pulsating#can decide what to do by appending things here
        update_functions = {'flicker': self.flicker, 'fade': self.fade, 'pulsating': self.pulsating}
        for prop, func in update_functions.items():
            if properties.get(prop, False):
                self.updates.append(func)

    def expand(self):
        self.radius += self.game_objects.game.dt*100
        self.radius = min(self.radius,300)

    def flicker(self):
        flickerrange = 0.1
        self.colour[-1] += random.uniform(-flickerrange, flickerrange)
        self.colour[-1] = max(0, min(1, self.colour[-1]))#clamp it between 0 and 1

    def fade(self, rate = 0.99):
        self.colour[-1] *= rate

    def pulsating(self):#
        self.time += self.game_objects.game.dt*0.01
        self.radius = 0.5 * self.init_radius * math.sin(self.time) + self.init_radius * 0.5

    def lifetime(self):
        if self.colour[-1] < 0.01:
            self.game_objects.lights.remove_light(self)
            self.target.state.handle_input('light_gone')

    def set_pos(self):#I think all should do this
        self.hitbox.center = self.target.hitbox.center
        self.position = [self.hitbox.center[0] - self.game_objects.camera.scroll[0],self.hitbox.center[1] - self.game_objects.camera.scroll[1]]#te shader needs tye position without the scroll (i.e. "on screen" values)

    def update(self):#if they e.g. fade
        for update in self.updates:
            update()
