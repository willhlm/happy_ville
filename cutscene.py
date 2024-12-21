import read_files
import animation
import states#maybe can code it so that we don't import states

class Cutscene_file():#cutscneens that will run based on file. The name of the file should be the same as the class name
    def __init__(self,parent_class):
        self.parent_class = parent_class
        self.game_objects = parent_class.game.game_objects
        self.animation = animation.Animation(self)
        self.sprites = {'idle': read_files.load_sprites_list('cutscene/'+type(self).__name__.lower(),parent_class.game.game_objects)}
        self.image = self.sprites['idle'][0]

    def update(self):
        self.animation.update()

    def render(self):
        self.parent_class.game.display.render(self.image,self.parent_class.game.screen)

    def reset_timer(self):#called when cutscene is finshed
        pass

    def handle_events(self,input):
        input.processed()

class Rhoutta_encounter(Cutscene_file):#play the first cutscene encountering rhoutta
    def __init__(self,objects):
        super().__init__(objects)
        self.parent_class.game.game_objects.load_map(None,'wakeup_forest_1',fade = False)#load map without appending fade

    def reset_timer(self):#called when cutscene is finshed
        self.parent_class.exit_state()
        new_state = states.Title_screen(self.parent_class.game)
        new_state.enter_state()
