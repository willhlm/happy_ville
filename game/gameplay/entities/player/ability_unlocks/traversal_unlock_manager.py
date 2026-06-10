class TraversalUnlockManager:
    BUNDLES = {
        'dash': ('sprint', 'dash_ground', 'dash_jump'),
        'air_dash': ('dash_air',),
        'climbing_gear': ('wall_jump',),
    }

    DEPENDENCIES = {
        'air_dash': ('dash',),
    }

    def __init__(self, entity):
        self.entity = entity
        self.unlocked = set()

        #temorary unlocks for testing
        self.unlock('dash')#Leaibolmmái's step
        self.unlock('climbing_gear')
        self.unlock('air_dash')

    def has_unlock(self, unlock_key):
        return unlock_key in self.unlocked

    def unlock(self, unlock_key):
        if unlock_key not in self.BUNDLES:
            raise KeyError(f"Unknown traversal unlock: {unlock_key}")
        if self.has_unlock(unlock_key):
            return

        for dependency in self.DEPENDENCIES.get(unlock_key, ()):
            self.unlock(dependency)

        self.entity.currentstate.install_states(self.BUNDLES[unlock_key])
        self.unlocked.add(unlock_key)
