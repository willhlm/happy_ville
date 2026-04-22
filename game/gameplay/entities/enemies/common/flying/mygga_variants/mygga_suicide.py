import pygame 
from gameplay.entities.enemies.base.flying_enemy import FlyingEnemy
from engine.utils import read_files

class MyggaSuicide(FlyingEnemy):#torpedo and explode
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/enemies/common/flying/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/common/flying/mygga_torpedo/',game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 16)
        self.vitals.set_max_health(1)
        self.vitals.set_health(self.vitals.max_health)

        self.aggro_distance = [180,130]
        self.attack_distance = self.aggro_distance.copy()

    def chase(self, position = [0,0]):#called from AI: when chaising
        pass

    def patrol(self, position = [0,0]):#called from AI: when patroling
        pass

    def player_collision(self, player):#when player collides with enemy
        self.suicide()

    def killed(self):#called when death animation starts playing
        self.suicide()

    def suicide(self):#called from states
        self.game_objects.projectiles.add_enemy(Explosion(self))
        self.game_objects.camera_manager.camera_shake(amp = 2, duration = 30)#amplitude and duration

    def handle_platform_collision(self, collision):
        self.currentstate.handle_input('collision')#for suicide
