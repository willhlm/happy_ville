import pygame
from engine.utils import read_files
from .bg_block import BgBlock
from gameplay.entities.states import states_shader

class BgFade(BgBlock):
    def __init__(self, pos, game_objects, img, parallax, positions, ID):
        super().__init__(pos, game_objects, img, parallax)
        self.shader_state = states_shader.Idle(self)
        self.make_hitbox(positions, pos)
        self.interacted = False
        self.sounds = read_files.load_sounds_list('assets/audio/sfx/bg_fade/')
        self.children = []#will append overlapping bg_fade to make "one unit"
        self.id = str(ID)

        if self.game_objects.world_state.state[self.game_objects.map.level_name]['bg_fade'].get(self.id, False):#if it has been interacted with already
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
        self.shader_state.handle_input('alpha')
        self.interacted = True
        self.game_objects.world_state.state[self.game_objects.map.level_name]['bg_fade'][self.id] = True

    def add_child(self, child):
        self.children.append(child)
        if self.interacted: child.interact()

    def draw(self, target):#called before draw in group
        self.shader_state.draw()
        super().draw(target)

    def player_collision(self, player):
        if self.interacted: return
        self.game_objects.sound.play_sfx(self.sounds[0])
        self.interact()
        for child in self.children:
            child.interact()

