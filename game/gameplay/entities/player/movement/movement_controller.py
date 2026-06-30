from engine import constants as C

from .horizontal_movement import HorizontalMovement
from .jump_movement import JumpMovement
from .sprint_movement import SprintMovement

class MovementController:
    def __init__(self, entity):
        self.entity = entity
        #self.horizontal = HorizontalMovement(entity)
        self.jump = JumpMovement(entity)
        #self.sprint = SprintMovement(entity)

    def handle_movement(self, axes):
        self.entity.currentstate.handle_movement(axes)

    def handle_press_input(self, input):
        self.entity.currentstate.handle_press_input(input)

    def handle_release_input(self, input):
        if input.name == 'a':
            self.release_jump()
        self.entity.currentstate.handle_release_input(input)

    def update(self, dt):
        self.jump.update(dt)

    def reset(self):
        self.interrupt_jump()
        #self.sprint.reset()

    def apply_ground_movement(self, axes, allow_facing_update=True):
        self.horizontal.apply_ground_input(axes, allow_facing_update=allow_facing_update)

    def apply_air_movement(self, axes, allow_facing_update=True):
        self.horizontal.apply_air_input(axes, allow_facing_update=allow_facing_update)

    def has_horizontal_intent(self):
        return self.horizontal.has_intent()

    def get_horizontal_drive_direction(self, fallback_dir):
        return self.horizontal.get_drive_direction(fallback_dir)

    def start_jump(self, jump_boost=1, air_timer=None):
        if air_timer is None:
            air_timer = C.air_timer
        self.jump.start(jump_boost=jump_boost, air_timer=air_timer)

    def extend_jump(self, jump_boost=None, air_timer=None):
        self.jump.extend(jump_boost=jump_boost, air_timer=air_timer)

    def release_jump(self):
        self.jump.release()

    def interrupt_jump(self):
        self.jump.interrupt()

    def consume_contact_state(self):
        self.jump.consume_contact_state()

    def can_sprint(self):
        return self.sprint.can_sprint()

    def request_sprint_chain(self):
        self.sprint.request_chain()

    def clear_sprint_chain(self):
        self.sprint.clear_chain()

    def should_chain_sprint(self):
        return self.sprint.should_chain()
