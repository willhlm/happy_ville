from .base.cutscene_engine import CutsceneEngine

class CultistEncounter(CutsceneEngine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.player.death_state.handle_input('cultist_encounter')
        self.game.game_objects.quests_events.initiate_quest('cultist_encounter', kill = 2)

        pos = [1420, 500]
        self.entity1 = game.game_objects.registry.fetch('enemies', 'cultist_warrior')(pos, game.game_objects)
        self.game.game_objects.enemies.add(self.entity1)
        
        self.stage = 0
        self.game.game_objects.camera_manager.set_camera('Cultist_encounter')
        self.game.game_objects.player.currentstate.enter_state('Run_pre')#should only enter these states once

    def update(self, dt):
        super().update(dt)
        self.timer+=dt
        if self.stage==0:#encounter Cultist_warrior
            if self.timer<50:
                self.game.game_objects.player.velocity[0]=-4
                self.game.game_objects.player.acceleration[0]=1

            elif self.timer > 50:
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                #self.game.game_objects.player.velocity[0]=0
                self.game.game_objects.player.acceleration[0] = 0

                self.stage = 1

        elif self.stage == 1:
            if self.timer > 200:#sapawn cultist_rogue

                spawn_pos = self.game.game_objects.player.rect.topright  
                self.entity2 = game.game_objects.registry.fetch('enemies', 'cultist_rogue')(spawn_pos, self.game.game_objects)
                self.entity2.dir[0] = -1
                self.entity2.currentstate.enter_state('Ambush_pre')    
                self.game.game_objects.enemies.add(self.entity2)

                self.stage=2
                self.timer=0

        elif self.stage==2:
            if self.timer>100:
                self.game.state_manager.exit_state()

    def on_exit(self):
        self.game.game_objects.camera_manager.camera.exit_state()
        super().on_exit()
