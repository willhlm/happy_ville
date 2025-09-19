import pygame 
from gameplay.entities.enemies.base.enemy import Enemy
from engine.utils import read_files
from . import states_vatt

class Vatt(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/vatt/', game_objects)#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)

        self.health = 3
        self.spirit = 3
        self.flags['aggro'] = False

        self.currentstate = states_vatt.Idle(self)
        self.attack_distance = [60, 30]

    def turn_clan(self):#this is acalled when tranformation is finished
        for enemy in self.game_objects.enemies.sprites():
            if type(enemy).__name__ == 'Vatt':
                enemy.flags['aggro'] = True
                enemy.AI.handle_input('Hurt')

    def patrol(self, direction):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3 * direction[0]