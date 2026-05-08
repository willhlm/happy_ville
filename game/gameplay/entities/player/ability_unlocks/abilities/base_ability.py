from engine.system import animation
from gameplay.entities.shared.states import states_basic

class Ability():#aila abilities
    id = None
    name = None
    state_name = None
    spirit_cost = 0
    selectable = False
    max_level = 1
    unlock_boss_id = None

    def __init__(self,entity):
        self.entity = entity
        self.game_objects = entity.game_objects        

        self.level = 1
        self.unlocked = False
        self.description = []

    def is_unlocked(self):
        return self.unlocked

    def can_unlock(self):
        return not self.is_unlocked()

    def unlock(self):
        if self.can_unlock():
            self.unlocked = True
            self.on_unlock()
        return self

    def lock(self):
        self.unlocked = False
        return self

    def can_upgrade(self):
        return self.is_unlocked() and self.level < self.max_level

    def upgrade(self):
        if self.can_upgrade():
            self.level += 1
            self.on_upgrade()
        return self

    def is_fully_upgraded(self):
        return self.is_unlocked() and self.level >= self.max_level

    def is_at_least_level(self, level):
        return self.is_unlocked() and self.level >= level

    def can_select(self):
        return self.selectable and self.is_unlocked()

    def get_current_description(self):
        if not self.is_unlocked():
            return None
        index = max(0, min(self.level - 1, len(self.description) - 1))
        if not self.description:
            return None
        return self.description[index]

    def get_next_upgrade_description(self):
        if not self.can_unlock() and not self.can_upgrade():
            return None
        if not self.description:
            return None
        index = 0 if self.can_unlock() else min(self.level, len(self.description) - 1)
        return self.description[index]

    def on_unlock(self):
        pass

    def on_upgrade(self):
        pass

    def initiate(self):#called when using the ability
        pass

    def update(self, dt):#called from ability manager
        pass

    def on_sword_attack(self):
        pass
