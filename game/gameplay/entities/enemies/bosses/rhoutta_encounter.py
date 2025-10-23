import pygame 
from gameplay.entities.enemies.base.boss import Boss
from engine.utils import read_files
from gameplay.entities.projectiles import HurtBox
class RhouttaEncounter(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/enemies/bosses/rhoutta/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 3
        self.attack_distance = [100,10]
        self.attack = HurtBox
        self.dmg = 0

    def dead(self):
        self.game_objects.game.state_manager.exit_state()
        self.game_objects.player.reset_movement()
        self.game_objects.game.state_manager.enter_state(state_name = 'defeated_boss', page = 'Rhoutta_encounter')