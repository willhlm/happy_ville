import pygame
from gameplay.entities.projectiles.base.projectiles import Projectiles
from engine.utils import read_files
from . import states_droplet
from gameplay.entities.shared.states import states_shader

class ProjectileDroplet(Projectiles):#droplet that can be placed, the source makes this and can hurt player
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = ProjectileDroplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.currentstate = states_droplet.Idle(self)

        if game_objects.world_state.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            self.dmg = 1#acid
            self.shader_state = states_shader.Palette_swap(self)
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more
        else:
            self.dmg = 0#water
            self.shader_state = states_shader.Idle(self)

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_enemy(collision_enemy)

    def collision_platform(self, collision_plat):#collision platform
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_platform(collision_plat)

    def pool(game_objects):
        ProjectileDroplet.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/environments/droplet/', game_objects)

    def draw(self,target):
        self.shader_state.draw()
        super().draw(target)
