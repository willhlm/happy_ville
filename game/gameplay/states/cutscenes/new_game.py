from engine.utils import read_files
from gameplay.states.base.game_state import GameState

class NewGame(GameState):
    def __init__(self, game):
        self.game = game
        self.sprites = read_files.load_sprites_list('assets/cutscene/new_game', game.game_objects)
        self.frame = 0                    

    def render(self):
        self.game.display.render(self.sprites[self.frame], self.game.screen_manager.screen) 
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self,input):
        event = input.output()
        input.processed()

        if event[0]:
          if event[-1] == 'a':
                self.frame+= 1
                self.frame = min(self.frame, len(self.sprites) )
                if self.frame == len(self.sprites) :                                          
                    self.game.state_manager.exit_state()

    def on_exit(self):
        self.game.state_manager.enter_state('gameplay')
        self.game.game_objects.load_map(self.game.state_manager.state_stack[-1], 'wakeup_forest_1', spawn = '1', fade = False)                                        


                    


