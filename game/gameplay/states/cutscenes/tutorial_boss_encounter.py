from .base.cutscene_engine import CutsceneEngine

class TutorialBossEncounter(CutsceneEngine):#boss fight cutscene
    def __init__(self, game):
        super().__init__(game)
        pos = [5888, 500]
        self.entity = game.game_objects.registry.fetch('enemies', 'wolfies')(pos, game.game_objects)        
        game.game_objects.enemies.add(self.entity)

        self.game.game_objects.camera_manager.set_camera('Deer_encounter')
        self.stage = 0
        
        self.game.game_objects.player.shader_state.handle_input('idle')        
        self.game.game_objects.player.acceleration[0]  = 1#start walking        

    def update(self, dt):#write how you want the player/group to act
        super().update(dt)
        self.timer += dt
        if self.stage == 0:
            if self.timer > 120:
                self.stage = 1
                self.game.game_objects.player.currentstate.enter_state('idle')#should only enter these states once
                self.game.game_objects.player.acceleration[0] = 0

        elif self.stage==1:#transform
            if self.timer > 200:
                self.entity.currentstate.queue_task(task = 'transform')
                self.entity.currentstate.queue_task(task = 'idle', animation = 'idle')
                self.entity.currentstate.start_next_task()                
                self.game.game_objects.player.velocity[0] = -20
                self.stage = 2

        elif self.stage==2:#roar
            if self.timer > 350:#make it long enought so that transform animation has time to finish                
                self.entity.currentstate.queue_task(task = 'roar_pre')
                self.entity.currentstate.queue_task(task = 'roar_main')
                self.entity.currentstate.queue_task(task = 'roar_post')
                self.entity.currentstate.queue_task(task = 'idle', animation = 'idle')                
                self.entity.currentstate.start_next_task()
                self.stage = 3

        elif self.stage==3:
            if self.timer > 600:
                self.game.game_objects.camera_manager.camera.exit_state()#exsiting deer encounter camera
                self.entity.currentstate.queue_task(task = 'think')
                self.entity.currentstate.start_next_task()
                self.game.state_manager.exit_state()
