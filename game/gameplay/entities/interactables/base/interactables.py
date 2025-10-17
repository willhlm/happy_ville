from gameplay.entities.base.animated_entity import AnimatedEntity
from gameplay.entities.shared.states import states_shader

class Interactables(AnimatedEntity):#interactables
    def __init__(self, pos, game_objects, sfx = None):
        super().__init__(pos, game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft
        self.shader_state = states_shader.Idle(self)
        if sfx: self.sfx = pygame.mixer.Sound('assets/audio/sfx/environment/' + sfx + '.mp3')
        else: self.sfx = None # make more dynamic incase we want to use more than just mp3

    def update(self, dt):
        super().update(dt)
        self.group_distance()

    def update_render(self, dt):        
        self.shader_state.update_render(dt)

    def draw(self, target):#called just before draw in group
        self.shader_state.draw()
        super().draw(target)

    def play_sfx(self):
        self.game_objects.sound.play_sfx(self.sfx)

    def interact(self):#when player press T
        pass

    def player_collision(self, player):#player collision
        self.shader_state.handle_input('outline')

    def player_noncollision(self):#when player doesn't collide: for grass
        self.shader_state.handle_input('idle')

    def take_dmg(self, dmg = 1):#when player hits with e.g. sword
        pass

    def seed_collision(self, seed):#if seed hits
        pass

    def modify_hit(self, effects):#called when aila sword hit it
        return effects

    def apply_hitstop(self, lifetime=10, call_back=None):#called when aila sword hit it
        pass

    def emit_particles(self, **kwargs):#called when aila sword hit it
        pass        