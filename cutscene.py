import Read_files
import animation
import states#maybe can code it so that we don't import states

class Cutscene_file():#cutscneens that will run based on file. The name of the file should be the same as the class name
    def __init__(self,parent_class):
        self.parent_class = parent_class
        self.game_objects = parent_class.game.game_objects
        self.animation=animation.Simple_animation(self)
        self.sprites = Read_files.load_sprites('cutscene/'+type(self).__name__.lower())
        self.image=self.sprites[0]

    def update(self):
        self.animation.update()

    def render(self):
        self.parent_class.game.screen.blit(self.image,(0, 0))

    def reset_timer(self):#called when cutscene is finshed
        pass

    def handle_events(self,input):
        pass

class Rhoutta_encounter(Cutscene_file):#play the first cutscene encountering rhoutta
    def __init__(self,objects):
        super().__init__(objects)
        self.parent_class.game.game_objects.load_map('wakeup_forest_1',fade = False)#load map without appending fade

    def reset_timer(self):#called when cutscene is finshed
        self.parent_class.exit_state()
        new_state = states.Cutscenes(self.parent_class.game,'Title_screen')
        new_state.enter_state()
