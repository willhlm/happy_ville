import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class Valve(Interactables):
    """A one-shot, hit-activated switch for a stateful world object."""

    WORLD_STATE_GROUP = "valve"

    def __init__(self, pos, game_objects, id, target_state_group="windmill", target_state="active", target_level=None):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/valve/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.id = str(id)
        self.target_state_group = target_state_group
        self.target_state = target_state
        self.target_level = target_level or self.game_objects.map.biome_room_name

        self.activated = self.game_objects.world_state.objects.load_bool(self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP, self.id, initial=False)

    def take_dmg(self, effect):
        if self.activated: return effect
            
        self.activated = self.game_objects.world_state.objects.set_bool(self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP, self.id, True)

        object_state = self.game_objects.world_state.objects
        if not object_state.has_level(self.target_level):
            object_state.init_level(self.target_level)

        object_state.set_value(self.target_level, self.target_state_group, self.id, self.target_state)
        self.game_objects.signals.emit(self.id, state=self.target_state)
        self.game_objects.world_controller.refresh_all()

        return effect
