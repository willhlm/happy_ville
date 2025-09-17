from .base.cutscene_engine import CutsceneEngine

class ButterflyEncounter(CutsceneEngine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.stage = 0
        self.game.game_objects.signals.emit('who_is_cocoon', callback = self.set_entity) 
        self.const[1] = 0.9

    def set_entity(self, entity):#the entity to control, set through signals
        self.entity = entity

    def update(self, dt):
        super().update(dt)
        self.timer+=dt
        if self.stage ==0:#approch
            if self.timer<50:
                self.game.game_objects.player.velocity[0]=4
                self.game.game_objects.player.acceleration[0] = 1

            elif self.timer > 150:#stay
                self.game.game_objects.player.currentstate.enter_state('Idle_main')
                self.game.game_objects.player.acceleration[0]=0
                self.stage = 1

        elif self.stage == 1:#aggro

            if self.timer > 200:
                self.game.game_objects.camera_manager.camera_shake(duration = 200)
                self.stage = 2

        elif self.stage == 2:#spawn
            self.entity.particle_release()
            if self.timer > 400:
                self.game_objects.quests_events.initiate_quest('butterfly_encounter')
                self.game.state_manager.exit_state()
