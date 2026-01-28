import random
from gameplay.entities.visuals.particles import particles
from gameplay.entities.base.static_entity import StaticEntity
from engine import constants as C

class DefeatedBoss(StaticEntity):
    def __init__(self, game_objects, boss):
        super().__init__([0, 0], game_objects)
        self.boss = boss
        self.game_objects.signals.subscribe('ability_ball', self.ability_ball_pickup)

        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.mark_boss_defeated(str(type(boss).__name__).lower())
        self.game_objects.world_state.cutscene_complete('boss_enconuter')#so not to trigger the cutscene again        

    def draw(self, target):
        pass

    def emit_particles(self, type = 'Circle', number_particles = 20, **kwarg):
        for i in range(0, number_particles):
            rect = self.boss.hitbox
            position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(-rect[3] * 0.5, rect[3] * 0.5)]

            obj1 = getattr(particles, type)(position, self.game_objects, **kwarg)
            self.game_objects.cosmetics_bg.add(obj1)#_bg is behind entities

    def update(self, dt):
        self.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [0, -2]})

    def ability_ball_pickup(self):#signal emiteed when abilty ball is pciked up
        self.game_objects.game.state_manager.enter_state(state_name = 'blit_image_text', image = self.game_objects.player.sprites[self.boss.ability][0], text = self.boss.ability)#the explanation image
        self.game_objects.game.state_manager.enter_state(state_name = 'defeated_boss')#the particle stuff        