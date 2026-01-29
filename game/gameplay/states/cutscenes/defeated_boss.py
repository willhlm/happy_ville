from .base.cutscene_engine import CutsceneEngine
from gameplay.entities.visuals.particles import particles

class DefeatedBoss(CutsceneEngine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)
        self._spawn_particles()

    def _spawn_particles(self):
        for i in range(0, 10):#should maybe be the number of abilites Aila can aquire?
            particle = getattr(particles, 'Circle')(self.game.game_objects.player.hitbox.center, self.game.game_objects, distance=0, lifetime = -1, vel = {'linear':[7,15]}, dir='isotropic', scale=5, colour=[100,200,255,255], state = 'Circle_converge',gradient = 1)
            light = self.game.game_objects.lights.add_light(particle, colour = [100/255,200/255,255/255,255/255], radius = 20)
            particle.light = light#add light reference
            self.game.game_objects.cosmetics.add(particle)        

    def update(self, dt):
        super().update(dt)
        self.timer+=dt
        if self.timer > 200:
            self.game.state_manager.exit_state()

    def cinematic(self):#black box stuff
        pass        