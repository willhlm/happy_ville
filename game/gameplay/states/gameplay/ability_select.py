from gameplay.states import Gameplay
from gameplay.ui.components import AbilityWheel

class AbilitySelect(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.ability_wheel = AbilityWheel(self.game.game_objects)

    def update(self, dt):
        dt *= 0.5#slow motion
        super().update(dt)

    def render(self):
        super().render()
        self.ability_wheel.render()

    def on_pop(self):
        self.ability_wheel.release()

    def handle_events(self, input):
        input.processed()
        if input.pressed and input.name == 'down':#down
            self.ability_wheel.select_next()
        elif input.pressed and input.name == 'up':#up
            self.ability_wheel.select_previous()
        elif input.released:#release
            if input.name == 'rb':
                self.ability_wheel.equip_selected()
                self.game.state_manager.exit_state()
