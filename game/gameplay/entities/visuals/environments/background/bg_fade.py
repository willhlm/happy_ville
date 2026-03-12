import pygame
from engine.utils import read_files
from .bg_block import BgBlock
from gameplay.entities.shared.states import states_shader

'''costume properties accepted from tiled:
ID: str
sfx: bool
'''

class BgFade(BgBlock):
    def __init__(self, pos, game_objects, img, parallax, positions, tiled_id, **properties):
        super().__init__(pos, game_objects, img, parallax)
        self.shader_state = states_shader.Idle(self)
        self.make_hitbox(positions, pos)
        self.interacted = False
        self.sounds = read_files.load_sounds_list('assets/audio/sfx/entities/visuals/environments/bg_fade/')
        self.children = []#will append overlapping bg_fade to make "one unit"
        self.id = str(tiled_id)

        self.sound_on = properties.get('sfx', True)
        self.signal_id = properties.get('ID', False)

        if self.signal_id:
            self.trigger = 'signal'
            self.game_objects.signals.subscribe(self.signal_id, self._on_signal)
        else:
            self.trigger = 'collision'
        
        if self.game_objects.world_state.load_bool(self.game_objects.map.level_name, 'bg_fade', self.id, initial = False):#if it has been interacted with already
            self.interact()

    def make_hitbox(self, positions, offset_position):#the rect is the whole screen, need to make it correctly cover the surface part, some how
        x, y = [],[]
        for pos in positions:
            x.append(pos[0]+offset_position[0])
            y.append(pos[1]+offset_position[1])
        width = max(x) - min(x)
        height = max(y) - min(y)
        self.hitbox = pygame.Rect(min(x),min(y),width,height)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def interact(self):
        if self.interacted: return            
        self.shader_state.handle_input('alpha')
        self.interacted = True
        self.game_objects.world_state.set_bool(self.game_objects.map.level_name, 'bg_fade', self.id,  True)

    def add_child(self, child):
        self.children.append(child)
        if self.interacted: child.interact()

    def draw(self, target):#called before draw in group
        self.shader_state.draw()    
        pos = (int(self.true_pos[0] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[0]),int(self.true_pos[1] - self.parallax[0] * self.game_objects.camera_manager.camera.interp_scroll[1]))
        self.game_objects.game.display.render(self.image, target, position = pos, shader = self.shader)  # Shader render

    def _play_sound(self):
        if self.sound_on and self.sounds:
            self.game_objects.sound.play_sfx(self.sounds[0])

    def _trigger_fade(self):
        if self.interacted: return
            
        self._play_sound()
        self.interact()
        for child in self.children:
            child.interact()

    def _on_signal(self, **kwargs):
        if self.trigger != 'signal': return            
        self._trigger_fade()

    def player_collision(self, player):
        if self.trigger != 'collision': return            
        self._trigger_fade()
