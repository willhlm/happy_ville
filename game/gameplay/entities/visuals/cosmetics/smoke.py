import pygame
from gameplay.entities.base.static_entity import StaticEntity

class Smoke(StaticEntity):#2D smoke
    def __init__(self, pos, game_objects, size, **properties):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.noise_layer = game_objects.game.display.make_layer(size)

        self.hitbox = pygame.Rect(pos, size)
        self.time = 0
        self.size = size

        self.colour = properties.get('colour', (1,1,1,1))
        self.spawn_rate = int(properties.get('spawn_rate', 10))
        self.radius = properties.get('radius', 0.03)
        self.speed = properties.get('speed', 0.2)
        self.horizontalSpread = properties.get('horizontalSpread', 0.5)
        self.lifetime = properties.get('lifetime', 2)
        self.spawn_position = properties.get('spawn_position', (0.5, 0.0))

    def release_texture(self):
        self.image.release()
        self.noise_layer.release()

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game_objects.shaders['noise_perlin']['u_time'] = self.time * 0.05
        self.game_objects.shaders['noise_perlin']['scroll'] = [0,0]#[self.game_objects.camera_manager.camera.scroll[0],self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.shaders['noise_perlin']['scale'] = [20,20]
        self.game_objects.game.display.render(self.image.texture, self.noise_layer, shader=self.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game_objects.shaders['smoke']['noiseTexture'] = self.noise_layer.texture
        self.game_objects.shaders['smoke']['time'] = self.time*0.01
        self.game_objects.shaders['smoke']['textureSize'] = self.size

        self.game_objects.shaders['smoke']['baseParticleColor'] = self.colour
        self.game_objects.shaders['smoke']['spawnRate'] = self.spawn_rate
        self.game_objects.shaders['smoke']['baseParticleRadius'] = self.radius
        self.game_objects.shaders['smoke']['baseParticleSpeed'] = self.speed
        self.game_objects.shaders['smoke']['horizontalSpread'] = self.horizontalSpread
        self.game_objects.shaders['smoke']['particleLifetime'] = self.lifetime
        self.game_objects.shaders['smoke']['spawnPosition'] = self.spawn_position

        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture,target, position = pos, shader = self.game_objects.shaders['smoke'])#shader render
