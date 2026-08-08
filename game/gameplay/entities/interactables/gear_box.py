import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables


class GearBox(Interactables):
    """Installs an inventory gear and activates the stateful object with this ID."""

    WORLD_STATE_GROUP = "gear_box"
    def __init__(self, pos, game_objects, id, item_id="gear", target_state_group="windmill", target_state="active", target_level=None):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/gear_box/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        
        self.id = str(id)#the id of this gear box, which should be the same as the target stateful object
        self.item_id = item_id#the thing to put in
        self.target_state_group = target_state_group
        self.target_state = target_state#what state to set the target to when this is installed
        self.target_level = target_level or self.game_objects.map.biome_room_name#where the target exists
        
        self.installed = self.game_objects.world_state.objects.load_bool(self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP, self.id, initial=False)

    def interact(self, player=None):
        if self.installed: return False
            
        player = player or self.game_objects.player
        inventory = player.backpack.inventory
        if inventory.get_quantity(self.item_id) <= 0: return False
            
        inventory.remove(self.item_id)
        self.installed = self.game_objects.world_state.objects.set_bool(self.game_objects.map.biome_room_name, self.WORLD_STATE_GROUP, self.id, True)

        object_state = self.game_objects.world_state.objects
        if not object_state.has_level(self.target_level):
            object_state.init_level(self.target_level)

        object_state.set_value(self.target_level, self.target_state_group, self.id, self.target_state)
        self.game_objects.signals.emit(self.id, state=self.target_state)
        return True
