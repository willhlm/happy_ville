from gameplay.states import Gameplay
from gameplay.ui.loaders import DashInstructionLoader

class Instructions(Gameplay):#when player obtaines a new ability, pick up inetractable item etc. It blits an image and text
    def __init__(self, game):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]
        self.fade = 0

        self.ui_loader = DashInstructionLoader(game.game_objects)
        self.game.game_objects.player.reset_movement()        

    def handle_movement(self):#every frame
        pass

    def render(self):
        super().render()
        self.render_fade[self.page]()
        
        self.render_text()
        self.game.game_objects.shaders['alpha']['alpha'] = self.fade
        self.game.display.render(self.ui_loader.bg, self.game.screen_manager.screen, shader = self.game.game_objects.shaders['alpha'])

        self.game.render_display(self.game.screen_manager.screen.texture)

    def render_text(self):
        for text in self.ui_loader.text:  
            text.render(self.game.screen_manager.screen)          

    def render_in(self):
        self.fade += 1
        self.fade = min(self.fade,150)

    def render_out(self):
        self.fade -= 1
        self.fade = max(self.fade, 0)

        if self.fade <= 0:
            self.game.state_manager.exit_state()

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.page = 1
            elif event[-1] == 'a':
                self.page = 1
