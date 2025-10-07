import pygame
from engine.utils import read_files
from gameplay.entities.base.static_entity import StaticEntity

class UpStream(StaticEntity):#a draft that can lift enteties along a direction
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.image = game_objects.game.display.make_layer(size)
        self.hitbox = pygame.Rect(pos[0] + size[0]* 0.05, pos[1], size[0] * 0.9, size[1])#adjust the hitbox size based on texture
        self.time = 0
        self.accel_y = 0.8
        self.accel_x = 0.8
        self.max_speed = 5

        horizontal = kwarg.get('horizontal', 0)
        vertical = kwarg.get('vertical', 0)
        normalise = (horizontal**2 + vertical**2)**0.5
        self.dir = [horizontal/normalise, vertical/normalise]

        sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/visuals/enviroments/up_stream/')
        self.channel = game_objects.sound.play_sfx(sounds['idle'][0], loop = -1, vol = 0.5)
        self.interacted = False#for player collision

    def player_collision(self, player):#player collision
        if self.interacted: return
        self.interacted = True
        if self.dir[0] != 0:
            player.movement_manager.add_modifier('UpStreamHorizontal', speed = [self.dir[0] * self.accel_x, self.dir[1] * self.accel_y], max_speed = self.max_speed)
        elif self.dir[1] != 0:
            player.movement_manager.add_modifier('UpStreamVertical', speed = [self.dir[0] * self.accel_x, self.dir[1] * self.accel_y], max_speed = self.max_speed)#add modifier to player movement manager

        #context = player.movement_manager.resolve()
        #player.velocity[0] += self.dir[0] * self.accel_x * context.upstream
        #player.velocity[1] += self.dir[1] * self.accel_y * context.upstream + self.dir[1] * int(player.collision_types['bottom'])#a small inital boost if on ground
        #if (player.velocity[1]) < 0:
        #    player.velocity[1] = min(abs(player.velocity[1]), self.max_speed) * self.dir[1]

    def player_noncollision(self):
        if not self.interacted: return
        self.game_objects.player.movement_manager.remove_modifier('up_stream')
        self.interacted = False

    def release_texture(self):
        self.image.release()
        self.channel.fadeout(300)

    def update(self, dt):
        self.time += dt

    def draw(self, target):
        self.game_objects.shaders['up_stream']['dir'] = self.dir
        self.game_objects.shaders['up_stream']['time'] = self.time*0.1
        blit_pos = (int(self.true_pos[0]-self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1]-self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = blit_pos, shader = self.game_objects.shaders['up_stream'])#shader render

    def seed_collision(self, seed):
        pass
