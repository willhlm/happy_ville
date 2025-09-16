from .spirit import Spirit

class SpiritFrame(Spirit):#gameplay UI
    def __init__(self,game_objects):
        super().__init__(game_objects, 'assets/sprites/ui/gameplay/spirit_frame/')

