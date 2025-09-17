from engine.utils import read_files
from gameplay.states import Gameplay

class AbilitySelect(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.abilities = list(self.game.game_objects.player.abilities.spirit_abilities.keys())
        self.index = self.abilities.index(self.game.game_objects.player.abilities.equip)

        self.sprites = read_files.load_sprites_list('assets/sprites/ui/ability_hud/', game.game_objects)#TODO
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]
        self.surface = self.game.display.make_layer(self.game.window_size)#TODO

    def update(self, dt):
        dt *= 0.5#slow motion
        super().update(dt)

    def render(self):
        super().render()
        self.surface.clear(20,20,20,100)

        hud = self.sprites[self.index]
        for index, ability in enumerate(self.abilities):
            pos = [self.coordinates[index][0] + 250, self.coordinates[index][1] + 100]
            self.game.display.render(self.game.game_objects.player.abilities.spirit_abilities[ability].sprites['active_1'][0], self.surface,position =pos)

        self.game.display.render(hud, self.surface,position = (250,100))
        self.game.render_display(self.surface.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] > 0:#dwpn
            self.index += 1
            if self.index > len(self.abilities)-1:
                self.index = 0
        elif event[2]['l_stick'][1] < 0:#up
            self.index-=1
            if self.index<0:
                self.index=len(self.abilities)-1
        elif event [1]:#release
            if event[-1]=='rb':
                self.game.game_objects.player.abilities.equip=self.abilities[self.index]
                self.game.state_manager.exit_state()

