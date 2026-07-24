from engine.utils import read_files


class AbilityWheel:
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.ability_manager = game_objects.player.abilities
        self.abilities = self.ability_manager.get_equippable_keys()
        self.index = self.abilities.index(self.ability_manager.equip)

        self.sprites = read_files.load_sprites_list(
            'assets/sprites/ui/overlay/ability_hud/',
            game_objects,
        )
        self.coordinates = [(40, 0), (60, 50), (30, 60), (0, 40), (20, 0), (0, 0)]
        self.position = (250, 100)
        self.surface = game_objects.game.display.make_layer(game_objects.game.window_size)

    def release(self):
        self.surface.release()

    def select_next(self):
        self.index = (self.index + 1) % len(self.abilities)

    def select_previous(self):
        self.index = (self.index - 1) % len(self.abilities)

    def get_selected_ability(self):
        return self.abilities[self.index]

    def equip_selected(self):
        self.ability_manager.equip = self.get_selected_ability()

    def render(self):
        self.surface.clear(20, 20, 20, 100)

        hud = self.sprites[self.index]
        base_x, base_y = self.position

        for index, ability in enumerate(self.abilities):
            icon = self.ability_manager.get(ability).sprites['active_1'][0]
            offset_x, offset_y = self.coordinates[index]
            position = (base_x + offset_x, base_y + offset_y)
            self.game_objects.game.display.render(icon, self.surface, position=position)

        self.game_objects.game.display.render(hud, self.surface, position=self.position)
        self.game_objects.game.render_display(self.surface.texture)
