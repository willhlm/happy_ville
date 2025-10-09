from .base_state import BaseState

class Idle(BaseState):#do nothing
    def __init__(self, entity, deciders):
        super().__init__(entity, deciders)