from engine.utils import read_files
from gameplay.entities.base.animated_entity import AnimatedEntity

class BgAnimated(AnimatedEntity):
    def __init__(self, game_objects, pos, sprite_folder_path, parallax = (1,1)):
        super().__init__(pos,game_objects)
        self.sprites = {'idle': read_files.load_sprites_list(sprite_folder_path, game_objects)}
        self.image = self.sprites['idle'][0]
        self.parallax = parallax

    def update(self, dt):
        self.animation.update(dt)

    def reset_timer(self):#animation need it
        pass            