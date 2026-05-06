class ContainedComponent:
    def __init__(self, entity, anchor_pos):
        self.entity = entity
        self.anchor_pos = list(anchor_pos)

    def enter_initial_state(self):
        self.entity.hit_component.set_invincibility(True)
        self.entity.flags['aggro'] = False
        self.entity.movement_manager.add_modifier('contained', authoritative=True)
        self.entity._apply_spawn_anchor(self.anchor_pos, self.entity.spawn_anchor)
        self.entity.true_pos = list(self.entity.rect.topleft)
        self.entity.currentstate.enter_state('contained')

    def release(self):
        self.entity.movement_manager.remove_modifier('contained')
        self.entity.hit_component.set_invincibility(False)
        self.entity.flags['aggro'] = True
        self.entity.currentstate.enter_state('fall')
