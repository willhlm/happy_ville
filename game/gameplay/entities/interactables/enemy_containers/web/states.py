import sys


class BasicStates:
    def __init__(self, entity):
        self.entity = entity
        self.entity.animation.play(type(self).__name__.lower())

    def enter_state(self, newstate, **kwargs):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwargs)

    def increase_phase(self):
        pass

    def update(self, dt):
        pass

    def handle_input(self, input_type):
        pass


class Idle(BasicStates):
    def update(self, dt):
        player = self.entity.game_objects.player.hitbox
        dx = player.centerx - self.entity.anchor_pos[0]
        dy = player.centery - self.entity.anchor_pos[1]
        if abs(dx) < self.entity.trigger_distance[0] and abs(dy) < self.entity.trigger_distance[1]:
            self.entity.enemy.hanging_component.trigger_drop()
            self.enter_state('Dropped')


class Dropped(BasicStates):
    pass
