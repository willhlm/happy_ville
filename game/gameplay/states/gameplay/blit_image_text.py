from gameplay.states import Gameplay

class BlitImageText(Gameplay):#when player obtaines a new ability, pick up inetractable item etc. It blits an image and text
    def __init__(self, game, image, text = '', callback = None):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]

        self.image = game.display.make_layer(image.size)
        self.game.display.render(image, self.image)#make a copy of the image
        self.text = text

        self.game.game_objects.player.reset_movement()

        self.fade = [0,0]
        self.callback = callback#a function to call when exiting
        self.should_exit = False

    def on_pop(self):
        self.image.release()

    def update(self, dt):
        super().update(dt)
        if self.should_exit:
            if self.callback:
                self.callback()
            self.game.state_manager.exit_state()

    def handle_movement(self):#every frame
        pass

    def render(self):
        super().render()
        self.render_fade[self.page]()

        self.game.game_objects.shaders['alpha']['alpha'] = self.fade[1]
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,self.fade[1])

        self.game.screen_manager.screen.clear(40, 40, 40, self.fade[0])

        self.game.display.render(self.image.texture, self.game.screen_manager.screen, position = (320, 120), shader = self.game.game_objects.shaders['alpha'])
        self.game.game_objects.font.render(
            self.game.screen_manager.screen,
            self.text,
            position=(320, 140),
            width=140,
            color=(255, 255, 255, self.fade[1]),
        )
        self.game.render_display(self.game.screen_manager.screen.texture)

    def render_in(self):
        self.fade[0] += 1
        self.fade[1] += 1
        self.fade[0] = min(self.fade[0],150)
        self.fade[1] = min(self.fade[1],255)

    def render_out(self):
        self.fade[0] -= 1
        self.fade[1] -= 1
        self.fade[0] = max(self.fade[0], 0)
        self.fade[1] = max(self.fade[1], 0)

        if self.fade[0] == 0:
            self.should_exit = True

    def handle_events(self,input):
        input.processed()
        if input.pressed:#press
            if input.name == 'start':
                self.page = 1
            elif input.name == 'a':
                self.page = 1
