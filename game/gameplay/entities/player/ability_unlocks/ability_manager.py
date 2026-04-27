from .abilities import horagalles_rage, tjasolmais_embrace, juksakkas_blessing, bieggs_breath, beaivis_time

class AbilityManager():#Player movement abilities, handles them. Contains also spirit abilities
    ABILITY_TYPES = (
        horagalles_rage.HoragallesRage,
        tjasolmais_embrace.TjasolmaisEmbrace,
        juksakkas_blessing.JuksakkasBlessing,
        bieggs_breath.BieggsBreath,
        beaivis_time.BeaivisTime,
    )

    def __init__(self,entity):
        self.entity = entity
        self.abilities = {}
        self._equip = None

        for ability_type in self.ABILITY_TYPES:
            self.register(ability_type(entity))

        equippable_keys = self.get_equippable_keys()
        self._equip = equippable_keys[0] if equippable_keys else None
        self.install_unlocked_states()

        #temporary unlocks for testing
        self.unlock('thunder')
        self.unlock('bow')
        self.unlock('slow_motion')
        self.unlock('wind')
        self.unlock('shield')

    @property
    def equip(self):
        return self._equip

    @equip.setter
    def equip(self, ability_key):
        if ability_key is None:
            self._equip = None
            return
        ability_key = self.require_key(ability_key)
        if not self.get(ability_key).can_select():
            raise ValueError(f"Ability cannot be equipped: {ability_key}")
        self._equip = ability_key

    def register(self, ability):
        ability_id = getattr(ability, 'id', None)
        if not ability_id:
            raise ValueError(f"Ability {type(ability).__name__} is missing an id")
        self.abilities[ability_id] = ability

    def require_key(self, ability_key=None):
        if ability_key is None:
            return self._equip
        if ability_key not in self.abilities:
            raise KeyError(f"Unknown ability: {ability_key}")
        return ability_key

    def get(self, ability_key=None):
        return self.abilities[self.require_key(ability_key)]

    def get_equipped(self):
        return self.get()

    def get_all_keys(self):
        return list(self.abilities.keys())

    def get_equippable_keys(self):
        return [
            ability_key
            for ability_key, ability in self.abilities.items()
            if ability.can_select()
        ]

    def get_equippable_abilities(self):
        return [self.get(ability_key) for ability_key in self.get_equippable_keys()]

    def refresh_equip(self):
        if self._equip in self.get_equippable_keys():
            return
        equippable_keys = self.get_equippable_keys()
        self._equip = equippable_keys[0] if equippable_keys else None

    def install_state_for(self, ability):
        currentstate = getattr(self.entity, 'currentstate', None)
        install_state = getattr(currentstate, 'install_state', None)
        if install_state is None or ability.state_name is None:
            return
        install_state(ability.state_name)

    def install_unlocked_states(self):
        for ability in self.abilities.values():
            if ability.is_unlocked():
                self.install_state_for(ability)

    def get_state_name(self, ability_key=None):
        return self.get(ability_key).state_name

    def get_level(self, ability_key=None):
        return self.get(ability_key).level

    def is_unlocked(self, ability_key=None):
        return self.get(ability_key).is_unlocked()

    def can_unlock(self, ability_key=None):
        return self.get(ability_key).can_unlock()

    def unlock(self, ability_key=None):
        ability = self.get(ability_key).unlock()
        self.install_state_for(ability)
        self.refresh_equip()
        return ability

    def can_upgrade(self, ability_key=None):
        return self.get(ability_key).can_upgrade()

    def upgrade(self, ability_key=None):
        return self.get(ability_key).upgrade()

    def is_fully_upgraded(self, ability_key=None):
        return self.get(ability_key).is_fully_upgraded()

    def is_at_least_level(self, ability_key, level):
        return self.get(ability_key).is_at_least_level(level)

    def enter_equipped_state(self, enter_state):
        if self._equip is None:
            return
        enter_state(self.get_state_name())

    def consume_spirit(self, ability_key=None):
        ability = self.get(ability_key)
        spirit_cost = getattr(ability, 'spirit_cost', 0)
        if spirit_cost:
            self.entity.consume_spirit_cost(spirit_cost)
        return ability

    def activate(self, ability_key=None, spend_spirit=True, **kwargs):
        ability = self.get(ability_key)
        if spend_spirit:
            self.consume_spirit(ability_key)
        ability.initiate(**kwargs)
        return ability

    def get_current_description(self, ability_key=None):
        return self.get(ability_key).get_current_description()

    def get_next_upgrade_description(self, ability_key=None):
        return self.get(ability_key).get_next_upgrade_description()

    def notify_sword_attack(self):
        for ability in self.abilities.values():
            ability.on_sword_attack()

    def update(self, dt):
        for ability in self.abilities.values():
            ability.update(dt)
