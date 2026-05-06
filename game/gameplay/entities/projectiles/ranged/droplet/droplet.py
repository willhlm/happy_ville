import pygame
from gameplay.entities.projectiles.base.platform_projectile import PlatformProjectile
from engine.utils import read_files
from . import states_droplet
from gameplay.entities.shared.render.entity_shader_manager import EntityShaderManager

class ProjectileDroplet(PlatformProjectile):#droplet that can be placed, the source makes this and can hurt player
    def __init__(self,pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = ProjectileDroplet.sprites
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.currentstate = states_droplet.Idle(self)
        self.shader_state = EntityShaderManager(self)

        if game_objects.world_state.narrative.events.get('tjasolmai', False):#if water boss (golden fields) is dead
            self.dmg = 1#acid
            self.original_colour = [[46, 74,132, 255]]#can append more to replace more
            self.replace_colour = [[70, 210, 33, 255]]#new oclour. can append more to replace more
            self.shader_state.add_shader(
                'palette_swap',
                original_colour=self.original_colour,
                replace_colour=self.replace_colour,
            )
        else:
            self.dmg = 0#water

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_enemy(collision_enemy)

    def collision_platform(self, collision_plat):#collision platform
        self.currentstate.handle_input('death')
        if self.dmg == 0: return#do not do the stuff if dmg = 0
        super().collision_platform(collision_plat)

    def handle_platform_collision(self, collision):
        self.collision_platform(collision.collider)

    def pool(game_objects):
        ProjectileDroplet.sprites = read_files.load_sprites_dict('assets/sprites/entities/visuals/environments/droplet/', game_objects)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def draw(self,target):
        blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.shader_state.draw(self.image, target, blit_pos, flip = self.dir[0] > 0)
