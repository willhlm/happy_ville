from gameplay.entities.player.base.ability import Ability
from engine.utils import read_files

class BeaivisTime(Ability):#slow motion -> sun god: Beaiviáigi in sami
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/attack/UI/beaivis_time/', entity.game_objects)
        self.duration = 200#slow motion duration, in time [whatever units]
        self.rate = 0.5#slow motion rate
        self.description = ['slow motion','longer slow motion','slow motion but aila','imba']

    def initiate(self):#called when using the ability from player states
        self.game_objects.time_manager.modify_time(time_scale = self.rate, duration = self.duration)#sow motion
        self.game_objects.post_process.append_shader('slowmotion', duration = self.duration)

    def upgrade_ability(self):#called from upgrade menu
        self.entity.slow_motion = 1/self.rate#can make aila move normal speed

