from .base.cutscene_engine import CutsceneEngine

class TitleScreen(CutsceneEngine):#screen played after waking up from boss dream
    def __init__(self,game):
        super().__init__(game)
        self.title_name = self.game.game_objects.font.render(text = 'Happy Ville')
        self.text1 = self.game.game_objects.font.render(text = 'A game by Hjortron games')
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.cosmetics.empty()

    def update(self, dt):
        super().update()
        self.timer += dt

    def render(self):
        super().render()
        if self.timer>250:
            self.game.display.render(self.title_name,self.game.screen_manager.screen,position = (190,150))

        if self.timer>500:
            self.game.display.render(self.text1,self.game.screen_manager.screen,position = (190,170))

        if self.timer >700:
            self.game.game_objects.player.acceleration[0] *= 2#bacl to normal speed
            self.game.state_manager.exit_state()
        
        self.game.render_display(self.game.screen_manager.screen.texture)  

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] == 'a':
                self.press = True

        if event[-1]=='right' or event[-1]=='left' or event[-1] == None or event[-1]=='down' or event[-1]=='up':#left stick and arrow keys
            if event[2]['l_stick'][0] > 0: return#can only go left
            event[2]['l_stick'][0] *= 0.5#half the speed
            self.game.game_objects.player.currentstate.handle_movement(event)
