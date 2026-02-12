import math
from engine.system import animation
from engine.utils import read_files
from gameplay.entities.platforms.dynamic.base_dynamic import BaseDynamic
from gameplay.entities.shared.states import states_basic

class TallTrees2(BaseDynamic):#dynamic one: #shoudl be added to platforms and dynamic_platforms groups
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/platforms/dynamic/tall_trees_2/', game_objects)        
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        self.old_hitbox = self.hitbox.copy()

        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#s

        direction = kwarg.get('direction', '0,0')#standing still
        string_list = direction.split(',')
        self.direction = [int(num) for num in string_list]
        self.distance = int(kwarg.get('distance', 10))/16
        self.speed = float(kwarg.get('speed', 0.01))

        self.velocity = [0, 0]
        self.time = 0

    def update_vel(self, dt):
        self.velocity[0] = self.direction[0] * self.distance * math.cos(self.speed * self.time)
        self.velocity[1] = self.direction[1] * self.distance * math.sin(self.speed * self.time + math.pi*0.5)

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.currentstate.update(dt)

    def group_distance(self):
        pass