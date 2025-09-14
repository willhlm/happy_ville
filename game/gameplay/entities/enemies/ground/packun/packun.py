import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import packun_states

class Packun(Enemy):
    def __init__(self,pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/enteties/enemies/packun/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 32, 32)
        self.health = 3

        self.currentstate = packun_states.Idle(self)
        self.angle_state = getattr(packun_states, kwarg['direction'])(self)

    def knock_back(self, amp, dir):
        pass

    def attack(self):#called from states, attack main
        dir, amp = self.angle_state.get_angle()
        attack = Projectile_1(self.rect.topleft, self.game_objects, dir = dir, amp = amp)#make the object
        self.projectiles.add(attack)#add to group but in main phase

    def update_vel(self, dt):
        pass

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, angle = self.angle_state.angle, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

    def on_attack_timeout(self):
        self.flags['attack_able'] = True