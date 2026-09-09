from .base_ability import Ability
from engine.utils import read_files

class HoragallesRage(Ability):#desolate dive:thunder god:
    id = 'thunder'
    name = 'Thunder'
    state_name = 'thunder'
    spirit_cost = 1
    selectable = True
    max_level = 2
    surface_radius = 240
    upgraded_surface_radius = 360
    traverse_speed = 40

    def __init__(self, entity):
        super().__init__(entity)
        self.sprites = read_files.load_sprites_dict('assets/sprites/ui/elements/abilities/horagalles_rage/',entity.game_objects)
        self.description = [
            'Aim at a nearby surface and rush into it with a thunder strike.',
            'Reach more distant surfaces with your thunder strike.',
        ]

    def uses_directional_aim(self):
        return True

    def get_dive_direction(self, aim_dir=None):
        if not self.uses_directional_aim() or aim_dir is None:
            return [0, 1]
        return aim_dir

    def get_surface_radius(self):
        return self.upgraded_surface_radius if self.is_at_least_level(2) else self.surface_radius

    def find_surface(self, direction):
        return self.game_objects.physics.collision_queries.find_surface_in_direction(self.entity, direction, self.get_surface_radius())

    def initiate(self, enemy_rect):
        thunder = Thunder(enemy_rect, self.entity.game_objects, lifetime =  1000)
        thunder.rect.midbottom = enemy_rect.midbottom
        thunder.hitbox = thunder.rect.copy()
        self.entity.game_objects.projectiles.add_friendly(thunder)#add attack to group
