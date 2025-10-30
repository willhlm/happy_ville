from .base_state import BaseState

class Idle(BaseState):#do nothing
    def __init__(self, entity, deciders, config_key):
        super().__init__(entity, deciders, config_key)