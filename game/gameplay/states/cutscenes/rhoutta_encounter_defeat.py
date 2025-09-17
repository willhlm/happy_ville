from .base.cutscene_file import CutsceneFile

class RhouttaEncounterDefeat(CutsceneFile):#play the first cutscene encountering rhoutta
    def __init__(self,objects):
        super().__init__(objects)
        self.game_objects.load_map(None, 'wakeup_forest_1', fade = False)#load map without appending fade

    def reset_timer(self):#called when cutscene is finshed
        self.game_objects.state_manager.exit_state()
        self.game_objects.state_manager.enter_state('Title_screen')

#engine based
