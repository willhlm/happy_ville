from engine.utils import read_files
from .base.cutscene_file import CutsceneFile

class RhouttaEncounterDefeat(CutsceneFile):#play the first cutscene encountering rhoutta
    def __init__(self,game):
        super().__init__(game)        
        self.sprites = {'idle': read_files.load_sprites_list('assets/cutscene/rhoutta_encounter_defeat/', game.game_objects)}
        self.image = self.sprites['idle'][0]        
        game.game_objects.map.load_map(self, 'wakeup_forest_2', spawn = '2')#load map without appending fade

    def reset_timer(self):#called when cutscene is finshed
        self.game.state_manager.exit_state()        