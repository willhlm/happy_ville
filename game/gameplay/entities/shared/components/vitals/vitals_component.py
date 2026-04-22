class VitalsComponent:
    def __init__(self, entity, max_health=0, health=None, max_spirit=0, spirit=None):
        self.entity = entity
        self.max_health = max_health
        self.health = max_health if health is None else health
        self.max_spirit = max_spirit
        self.spirit = max_spirit if spirit is None else spirit

    def set_health(self, value):
        self.health = max(0, min(value, self.max_health))
        return self.health

    def set_max_health(self, value):
        self.max_health = max(0, value)
        self.health = min(self.health, self.max_health)
        return self.max_health

    def damage(self, amount):
        self.health = max(0, self.health - amount)
        return self.health

    def heal(self, amount=1):
        self.health = min(self.max_health, self.health + amount)
        return self.health

    def set_spirit(self, value):
        self.spirit = max(0, min(value, self.max_spirit))
        return self.spirit

    def set_max_spirit(self, value):
        self.max_spirit = max(0, value)
        self.spirit = min(self.spirit, self.max_spirit)
        return self.max_spirit

    def add_spirit(self, amount=1):
        self.spirit = min(self.max_spirit, self.spirit + amount)
        return self.spirit

    def consume_spirit(self, amount=1):
        self.spirit = max(0, self.spirit - amount)
        return self.spirit
