import pygame, random
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.visuals.cosmetics.shock_wave import ShockWave

class BossStatue(Interactables):#interact with it to get air dash
    def __init__(self, pos, game_objects, boss, id = None, **kwargs):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/statues/boss/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.boss = boss
        self.id = id or boss
        self.interacted = False

        if self.game_objects.world_state.narrative.is_boss_defeated(self.id):
            self.interacted = True
            self.shader_state.add_shader('tint', colour=[0, 255, 0, 255])

    def update(self, dt):
        super().update(dt)
        self._emit_particles()

    def _emit_particles(self):
        rect = self.hitbox
        position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(rect[3]*0.1,rect[3]*0.5)]
        self.game_objects.particles.emit('spirit_wisp', position, colour =[0,0,0,255])
        
    def interact(self, player=None):#when player press t/y
        if self.interacted: return
        self.interacted = True
        self.game_objects.sequence_manager.start_sequence('boss_encounter', encounter=self.id, source=self)
        