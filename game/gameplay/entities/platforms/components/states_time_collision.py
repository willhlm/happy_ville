import sys
import pygame

def _set_collidable(entity, on: bool):
    if on:
        entity.hitbox = entity.rect.copy()
    else:
        entity.hitbox = pygame.Rect(entity.hitbox.left, entity.hitbox.top, 0, 0)

class Basic_states:
    anim_name = None  # override in subclasses if name != class

    def __init__(self, entity):
        self.entity = entity
        name = self.anim_name or type(self).__name__.lower()
        self.entity.animation.play(name)

    def enter_state(self, newstate):
        self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)

    def update(self, dt):
        pass

    def handle_input(self, input):
        pass

    def increase_phase(self):
        pass

class Idle(Basic_states):
    anim_name = "idle"
    def __init__(self, entity):
        super().__init__(entity)
        _set_collidable(entity, True)

    def handle_input(self, input):
        if input == "warning":
            self.enter_state("Warning")

class Warning(Basic_states):
    anim_name = "warning"
    def __init__(self, entity):
        super().__init__(entity)
        _set_collidable(entity, True)

    def handle_input(self, input):
        if input == "dissapear":
            self.enter_state("Transition_1")     

class Transition_1(Basic_states):
    anim_name = "transition_1"
    def __init__(self, entity):
        super().__init__(entity)
        _set_collidable(entity, False)

    def increase_phase(self):
        self.enter_state("Gone")

class Gone(Basic_states):
    anim_name = "gone"
    def __init__(self, entity):
        super().__init__(entity)
        _set_collidable(entity, False)

    def handle_input(self, input):
        if input == "re_appear":
            self.enter_state("Transition_2")

class Transition_2(Basic_states):
    anim_name = "transition_2"
    def __init__(self, entity):
        super().__init__(entity)
        _set_collidable(entity, False)

    def increase_phase(self):
        self.enter_state("Idle")
