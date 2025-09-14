import pygame 
from gameplay.entities.enemies.base.boss import Boss
from engine.utils import read_files

class RhouttaEncounter(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.load_sprites_dict('assets/sprites/enteties/boss/rhoutta/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 3
        self.attack_distance = [100,10]
        self.attack = Sword
        self.dmg = 0

    def dead(self):
        self.game_objects.game.state_manager.exit_state()
        self.game_objects.player.reset_movement()
        self.game_objects.game.state_manager.enter_state(state_name = 'Defeated_boss', category = cutscenes, page = 'Rhoutta_encounter')