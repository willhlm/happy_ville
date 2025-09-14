import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles

class Wind(Projectiles):
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.image = Wind.image
        self.rect = pygame.Rect(pos[0], pos[1], self.image.texture.width, self.image.texture.height)
        self.hitbox = self.rect.copy()
        self.dmg = 0

        self.time = 0

        self.dir = kwarg.get('dir', [1,0])
        self.velocity = [self.dir[0] * 10, self.dir[1] * 10]

    def collision_platform(self, platform):
        self.velocity = [0,0]
        self.kill()

    def pool(game_objects):
        size = [32, 32]
        Wind.image = game_objects.game.display.make_layer(size)

    def collision_enemy(self, collision_enemy):#if hit something
        self.velocity = [0,0]
        collision_enemy.velocity[0] = self.dir[0]*40#abs(push_strength[0])
        collision_enemy.velocity[1] = -1
        self.kill()

    def update(self, dt):
        self.time += dt
        self.lifetime -= dt
        self.destroy()

    def draw(self, target):
        self.game_objects.shaders['up_stream']['dir'] = self.dir
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture,target, position = pos, shader = self.game_objects.shaders['up_stream'])#shader render
