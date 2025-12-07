from .base_ability import Ability
from engine.utils import read_files

class Counter(Ability):#just a counter abilty
    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities//beaivis_time/',entity.game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/enteties/projectiles/beaivis_time/')
        self.duration = 10#slow motion duration, in time [whatever units]
        self.rate = 0.5#slow motion rate
        self.description = ['slow motion','slow motion but aila']
        self.channels = []

    def initiate(self):#called when using the ability from player states
        self.entity.game_objects.fprojectiles.add(Counter(self.entity, dir = (0,0), lifetime = self.duration))

    def counter(self):#called from counter if sucsesfully countered
        self.channels.append(self.entity.game_objects.sound.play_sfx(self.sounds['counter'][0], loop = -1, vol = 0.5))
        self.channels.append(self.entity.game_objects.sound.play_sfx(self.sounds['woosh'][0], vol = 0.5))

        self.game_objects.time_manager.modify_time(time_scale = self.rate, duration = self.duration)#sow motion
        self.game_objects.time_manager.modify_time(time_scale = 0, duration = 20)#freeze
        self.entity.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 20, scale = 0.9)
        self.entity.emit_particles(lifetime = 40, scale=3, colour=C.spirit_colour, fade_scale = 7, number_particles = 60 , gradient = 1)
        self.entity.game_objects.cosmetics.add(Slash(self.entity.hitbox.center,self.game_objects))#make a slash animation

        self.entity.currentstate.enter_state('Air_dash_pre')#what should the player do?
        self.game_objects.shader_render.append_shader('white_balance', temperature = 0.2)#change the tone of screen
        #self.game_objects.shader_render.append_shader('zoom', scale = 0.8)

        #maybe make attacks double the damage?
        #get spirit?
        #add particles, screen shaske, bloom? zoom in?
        #add echo FX, heart beat, slow pitch drop
        # ability symbol pulses
        #reposigion behind the enemy/projectile?
        #give free dash?
        #summon a phantom copy that repeats your last attack when time resumes.
        #upgrade, freeze enemy?

    def exit(self):
        self.game_objects.shader_render.remove_shader('white_balance')
        for channel in self.channels:
            self.entity.game_objects.sound.fade_sound(channel)

    def upgrade_ability(self):#called from upgrade menu
        self.entity.slow_motion = 1/self.rate#can make aila move normal speed