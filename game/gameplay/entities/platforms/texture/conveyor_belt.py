import pygame
from .textured_platform import TexturedPlatform
from engine.system import animation
from engine.utils import read_files
from gameplay.entities.shared.states import states_basic
from gameplay.entities.platforms.components.geometry import CollisionSample

class ConveyorBelt(TexturedPlatform):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.tile_size = [16,16]

        if kwarg.get('vertical', False):#default is horizontal belft
            angle = 90
            size[1] = max(size[1], self.tile_size[1] * 3)#assert at least 3 tiles
            if kwarg.get('up', False):#default is up down betls
                self.direction = [0, -1]
            else:#down
                self.direction = [0, 1]
            animation_direction =  self.direction[1]
        else:#horizontal
            angle = 0
            size[0] = max(size[0], self.tile_size[0] * 3)#assert at least 3 tiles
            if kwarg.get('right', False):#default is left moving belts
                self.direction = [1,0]
            else:#left
                self.direction = [-1, 0]
            animation_direction =  -self.direction[0]

        self.make_belt(size, angle)
        self.animation = animation.Animation(self, direction = animation_direction)#can revert the animation direction
        self.currentstate = states_basic.Idle(self)

        self.rect = pygame.Rect(pos, size)
        self.true_pos = list(self.rect.topleft)
        if angle == 0:
            self.hitbox = pygame.Rect(pos[0], pos[1], (self.rect[2] - 16), self.rect[3] * 0.55)
        else:
            self.hitbox = pygame.Rect(pos[0], pos[1], (self.rect[2]) * 0.55, (self.rect[3]-16))
        self.hitbox.center = self.rect.center

    def make_belt(self, size, angle = 0):#the spits are divided into left, middle and right. Merge them here
        sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/conveyor_belt/', self.game_objects)

        self.sprites = {'idle' : []}
        self.layers = []#store each layer so that it can be released
        principle_sections = ['left', 'middle','right']#the middle will be placed multiple times depending on the size

        if angle == 0:
            sections = [principle_sections[0]] + [principle_sections[1]] * (int(size[0]/self.tile_size[0]) - 2) + [principle_sections[2]]
        else:#90
            sections = [principle_sections[0]] + [principle_sections[1]] * (int(size[1]/self.tile_size[1]) - 2) + [principle_sections[2]]

        for frame in range(0, len(sprites[sections[0]]) - 1):
            self.layers.append(self.game_objects.game.display.make_layer(size))
            for index, section in enumerate(sections):
                if angle == 0:
                    pos = [sprites[sections[index - 1]][frame].width * index , 0]
                else:#vertical
                    pos = [0, sprites[sections[index - 1]][frame].height * index ]

                self.game_objects.game.display.render(sprites[section][frame], self.layers[-1], position = pos, angle = angle)#int seem nicer than round

            self.sprites['idle'].append(self.layers[-1].texture)
        self.image =  self.sprites['idle'][0]

        for state in sprites.keys():
            for frame in range(0,len(sprites[state])):
                sprites[state][frame].release()

    def release_texture(self):
        super().release_texture()
        for layer in self.layers:
            layer.release()

    def get_contact_metadata(self, entity, side, axis, collision_kind):
        return {}

    def get_wall_samples(self, entity):
        if not (
            entity.hitbox.bottom > self.hitbox.top and
            entity.hitbox.top < self.hitbox.bottom
        ):
            return ()

        return (
            CollisionSample('right', self.hitbox.left, self, self, collision_kind='belt'),
            CollisionSample('left', self.hitbox.right, self, self, collision_kind='belt'),
        )

#shadow light platforms: platforms that appear under shadow light
