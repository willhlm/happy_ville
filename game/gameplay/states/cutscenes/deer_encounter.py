from .base.cutscene_engine import CutsceneEngine

class DeerEncounter(CutsceneEngine):#first deer encounter in light forest by waterfall
    def __init__(self,game):
        super().__init__(game)
        pos = [2992, 848]
        self.entity = game.game_objects.registry.fetch('enemies', 'reindeer')(pos, game.game_objects)
        game.game_objects.enemies.add(self.entity)
        self.game.game_objects.camera_manager.set_camera('Deer_encounter')
        self.game.game_objects.player.currentstate.enter_state('Run_pre')#should only enter these states once
        self.stage = 0

    def update(self, dt):#write how you want things to act
        super().update()
        self.timer += dt
        if self.stage == 0:

            if self.timer < 50:
                self.game.game_objects.player.velocity[0] = 4

            elif self.timer > 50:
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.game.game_objects.player.acceleration[0] = 0
                self.stage  = 1
                
        elif self.stage ==1:
            if self.timer > 200:
                self.entity.currentstate.queue_task(task = 'walk', animation = 'walk_nice')   
                self.entity.currentstate.queue_task(task = 'idle')
                self.entity.currentstate.start_next_task()
                
                self.entity.velocity[0] = 5      
                self.entity.dir[0] *= -1
                self.stage = 2

        elif self.stage ==2:
            if self.timer > 200:                   
                self.entity.velocity[0] = 5

        if self.timer>300:
            self.game.state_manager.exit_state()

    def on_exit(self):
        self.game.game_objects.camera_manager.camera.exit_state()
        self.entity.kill()
        self.game.game_objects.world_state.cutscene_complete('deer_encounter')
        super().on_exit()
