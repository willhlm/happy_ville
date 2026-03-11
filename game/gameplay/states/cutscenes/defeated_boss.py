from .base.cutscene_engine import CutsceneEngine

class DefeatedBoss(CutsceneEngine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)        
        self._spawn_particles()
        self.game.game_objects.signals.subscribe('particles_absorbed', self.finish)#emmited each tiime particle collides with player     

    def _spawn_particles(self):
        self.number_particles = 10
        self.game.game_objects.particles.emit("converging_soul", pos=self.game.game_objects.player.hitbox.center, n=self.number_particles,player=self.game.game_objects.player)
  
    def finish(self):
        self.number_particles -= 1
        if self.number_particles == 0:
            self.game.state_manager.exit_state()

    def cinematic(self):#black box stuff
        pass        