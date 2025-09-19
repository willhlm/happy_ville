from engine.system import animation
from engine.utils import read_files
from gameplay.entities.platforms.dynamic.base_dynamic import BaseDynamic
from . import states_smacker

class Smacker(BaseDynamic):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/traps/smacker/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.hole = kwarg.get('hole', None)

        self.frequency = int(kwarg.get('frequency', 100))#infinte -> idle - active
        self.distance = kwarg.get('distance', 4*16)
        self.original_pos = pos

        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_smacker.Idle(self)

    def update(self, dt):
        self.currentstate.update()
    
    def update_render(self, dt):
        self.animation.update(dt)

    def collide_entity_y(self,entity):#plpaotfrom mobings
        self.currentstate.collide_entity_y(entity)

    def collide_y(self,entity):#entity moving
        self.currentstate.collide_y(entity)
