import random
from gameplay.entities.base.static_entity import StaticEntity
from engine import constants as C

class DefeatedBoss(StaticEntity):
    def __init__(self, game_objects, boss):
        super().__init__([0, 0], game_objects)
        self.boss = boss
        self.game_objects.signals.subscribe('ability_ball', self.ability_ball_pickup)

        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.mark_boss_defeated(str(type(boss).__name__).lower())
        self.game_objects.world_state.cutscene_complete('boss_enconuter')#so not to trigger the cutscene again. TODO need to be spacific for the boss 
        
        self.time = 0    
        self.timescale = 1

    def release_texture(self):
        pass

    def draw(self, target):
        pass

    def update(self, dt):
        self.time += dt * self.timescale
        if self.time > 10:
            rect = self.boss.hitbox
            position = [rect.centerx + random.uniform(-rect[2] * 0.5, rect[2] * 0.5), rect.centery + random.uniform(rect[3]*0.1,rect[3]*0.5)]
            self.game_objects.particles.emit("spirit_wisp", pos=position, n=1, colour=C.spirit_colour)            
            #self.emit_particles(lifetime = 70, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 3,  number_particles = 1, vel = {'wave': [0, -1]})
            self.time = 0

    def ability_ball_pickup(self):#signal emiteed when abilty ball is pciked up
        self.game_objects.game.state_manager.enter_state(state_name = 'instructions')              
        self.game_objects.game.state_manager.enter_state(state_name = 'defeated_boss')#the particle stuff        
        self.timescale = 0