import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import larv_wall_states

class LarvWall(Enemy):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/ground/slime_wall/', game_objects, flip_x = True)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()#pygame.Rect(pos[0],pos[1],16,16)

        self.angle = 0
        self.friction = [0.1, 0.1]
        self.clockwise = 1#1 is clockqise, -1 is counter clockwise
        self.currentstate = larv_wall_states.Floor(self)
        self.dir[0] = -self.clockwise

    def update_vel(self, dt):
        pass

    def knock_back(self,dir):
        pass

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, angle = self.angle, flip = self.dir[0] > 0, shader = self.shader)#shader render