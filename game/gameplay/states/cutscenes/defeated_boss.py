from .base.cutscene_engine import CutsceneEngine
from gameplay.entities.visuals.particles import particles

class DefeatedBoss(CutsceneEngine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)
        self.step1 = False
        self.const = [0.5,0.5]#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once

    def update(self, dt):
        super().update(dt)
        self.timer+=dt
        if self.timer < 75:
            self.game.game_objects.player.velocity[1] = -2
        elif self.timer > 75:
            self.game.game_objects.player.velocity[1] = -1#compensates for gravity, levitates
            self.step1 = True

        if self.timer > 250:
            self.game.game_objects.player.velocity[1] = 2#go down again
            if self.game.game_objects.player.collision_types['bottom']:
                self.game.state_manager.exit_state()

    def render(self):
        super().render()
        if self.step1:
            particle = getattr(particles, 'Spark')(self.game.game_objects.player.rect.center, self.game.game_objects, distance = 400, lifetime = 60, vel = {'linear':[7,13]}, dir = 'isotropic', scale = 1, colour = [255,255,255,255])
            self.game.game_objects.cosmetics.add(particle)
