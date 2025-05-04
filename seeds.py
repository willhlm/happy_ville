import pygame
import platforms, read_files, animation
from states import states_basic

class SeedSpawner():
    def __init__(self, arrow):
        self.arrow = arrow

    def spawn_ground(self, dir):#default
        platform = Seed_platform(self.arrow, self.arrow.game_objects, dir)
        self.arrow.game_objects.platforms.add(platform)

    def spawn_bubble(self):#called from twoDliquid collisions with arrow
        platform = platforms.Bubble(self.arrow.hitbox.midbottom, self.arrow.game_objects, lifetime = 200)
        self.arrow.game_objects.platforms.add(platform)

    def spawn_mushroom(self, dir, block):
        pass

    def spawn_seed(self, block, dir = None):
        material = getattr(block, 'type', 'ground')
        spawn_method = getattr(self, f"spawn_{material}", self.spawn_ground)  # Default to ground
        spawn_method(dir)           

class Seed_platform(platforms.Collision_texture):
    def __init__(self, arrow, game_objects, dir):
        super().__init__(arrow.hitbox.center, game_objects)
        self.lifetime = 200
        self.sprites = Seed_platform.sprites        
        self.image = self.sprites['grow'][0]

        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Once(self, next_state = 'Idle', animation_name = 'grow')
        self.get_hitbox(arrow, dir)

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt
        if self.lifetime < 0:
            self.kill()

    def release_texture(self):#called when .kill() and empty group
        pass

    def pool(game_objects):
        Seed_platform.sprites = read_files.load_sprites_dict('Sprites/animations/seeds/platform/', game_objects)

    def get_hitbox(self, arrow, dir):
        if dir == [-1, 0]:#left
            self.angle = 90
            pos = [arrow.hitbox.midleft[0], arrow.hitbox.bottomleft[1] - self.image.height * 0.5]
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.height, self.image.width )       
        elif dir == [1, 0]:#right
            self.angle = -90
            pos = [arrow.hitbox.midright[0] - self.image.width, arrow.hitbox.topright[1]]
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.height, self.image.width )       
        elif dir == [0, -1]:#down
            self.angle = 0
            pos = [arrow.hitbox.midleft[0], arrow.hitbox.midleft[1] - self.image.height + arrow.hitbox[3] * 0.5]
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.width , self.image.height)       
        elif dir == [0, 1]:#up
            self.angle = 180
            pos = arrow.hitbox.topleft
            self.hitbox = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)       
            
        self.rect = self.hitbox.copy() 

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, angle = self.angle, position = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])))#int seem nicer than round
