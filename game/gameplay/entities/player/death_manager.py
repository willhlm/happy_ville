from gameplay.entities.visuals.cosmetics import Blood

class DeathManager:
    def __init__(self, entity):
        self.entity = entity
        self.override = None

    def die(self):
        if self.entity.currentstate.composite_state is self.entity.currentstate.states['death']:
            return

        if self.override:
            self.override()
            return

        self.entity.currentstate.enter_state('death')
        self._start_death_effects()

    def finish_death(self):#caleld from death animation when it finishes
        self.entity.game_objects.world_state.statistics_state.update_statistic('death')
        self.entity.game_objects.sequence_manager.start_sequence('death')

    def set_override(self, callback):
        self.override = callback

    def clear_override(self):
        self.override = None

    def _start_death_effects(self):
        #self.animation.update()#make sure you get the new animation
        self.entity.game_objects.cosmetics.add(Blood(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir))#pause first, then slow motion
        self.entity.game_objects.time_manager.modify_time(time_scale = 0.4, duration = 100)#sow motion
        self.entity.game_objects.time_manager.modify_time(time_scale = 0, duration = 50)#freeze
