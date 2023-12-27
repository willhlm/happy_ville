import pygame

class Lights():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.ambient = (0,0,0,1)#ambient colour
        self.lights_sources = [Light(game_objects)]#append lights
        self.shaders = {'light':game_objects.shaders['light'],'blur':game_objects.shaders['blur'],'blend':game_objects.shaders['blend']}

        self.shaders['light']['resolution'] = self.game_objects.game.window_size
        self.shaders['blur']['blurRadius'] = 5

        self.layer1 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer2 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.layer3 = game_objects.game.display.make_layer(game_objects.game.window_size)
        self.update()

    def update(self):
        self.points, self.positions, self.radius, self.colour = [], [], [], []
        for light in self.lights_sources:
            light.update()
            self.list_points(light)#sort the collisions points into a ligst
            self.positions.append((light.position[0],self.game_objects.game.window_size[1] - light.position[1]))#get te positions of the lights
            self.radius.append(light.radius)
            self.colour.append(light.colour)

    def list_points(self, light):
        platforms = self.game_objects.collisions.light_collision(light)#collision -> collision occures at coordinates as pe tiled position
        self.shaders['light']['num_rectangle'] = len(platforms)#update numbe rof rectanges
        self.points = self.points + self.get_points(platforms)
        light.position = [light.position[0] - self.game_objects.camera.scroll[0],light.position[1] - self.game_objects.camera.scroll[1]]#te shader needs tye position without the scroll (i.e. "on screen" values)

    def get_points(self,platforms):
        l = []
        for rec in platforms:
            l = l + [(rec.hitbox.topleft[0] - self.game_objects.camera.scroll[0],rec.hitbox.topleft[1] - self.game_objects.camera.scroll[1]),(rec.hitbox.topright[0] - self.game_objects.camera.scroll[0],rec.hitbox.topright[1] - self.game_objects.camera.scroll[1]),(rec.hitbox.bottomright[0] - self.game_objects.camera.scroll[0],rec.hitbox.bottomright[1] - self.game_objects.camera.scroll[1]),(rec.hitbox.bottomleft[0] - self.game_objects.camera.scroll[0],rec.hitbox.bottomleft[1] - self.game_objects.camera.scroll[1])]
        return l

    def add_light(self, light):#not implemented
        self.lights_sources.append(light)

    def draw(self):
        self.layer1.clear(0,0,0,1)
        self.layer2.clear(0,0,0,1)
        self.layer3.clear(0,0,0,1)

        self.shaders['light']['rectangleCorners'] = self.points
        self.shaders['light']['lightPositions'] = self.positions
        self.shaders['light']['lightRadii'] = self.radius
        self.shaders['light']['colour'] = self.colour
        self.shaders['light']['num_lights'] = 1

        self.shaders['blend']['ambient'] = self.ambient
        self.shaders['blend']['background'] = self.game_objects.game.screen.texture

        self.game_objects.game.display.render(self.layer1.texture, self.layer2, shader = self.shaders['light'])
        self.game_objects.game.display.render(self.layer2.texture, self.layer3, shader = self.shaders['blur'])
        self.game_objects.game.display.render(self.layer3.texture, self.game_objects.game.screen, shader = self.shaders['blend'])

class Light():#light source
    def __init__(self,game_objects):
        self.game_objects = game_objects
        self.radius = 200
        self.colour = (1,1,1)
        self.position = [0,0]
        self.hitbox = pygame.Rect(self.position[0]-self.radius,self.position[1]-self.radius,self.radius*2,2*self.radius)
        self.rect = self.hitbox.copy()

    def update(self):#for collision
        self.position = self.game_objects.player.hitbox.center#[self.positions[0] + self.game_objects.camera.scroll[0],self.positions[1] + self.game_objects.camera.scroll[1]]
        self.hitbox.center = self.position
