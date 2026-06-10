import pygame, random
from engine.utils import read_files
from engine import constants as C
from gameplay.entities.interactables.base.interactables import Interactables
from gameplay.entities.shared.components.loot.item_loot_emitter import ItemLootEmitterComponent
from . import loot_container_states

class LootContainers(Interactables):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/chests/' + type(self).__name__.lower() + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

        self.health = 1
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.loot_emitter = ItemLootEmitterComponent(self, spawn_velocity=[0, -2], spawn_velocity_range=[2, 0])

        if state:
            self.currentstate = loot_container_states.Interacted(self)
            #self.hit_component.set_invinsibility(True)
        else:
            self.currentstate = loot_container_states.Idle(self)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def loots(self):#this is called when the opening animation is finished
        self.loot_emitter.emit_inventory(self.inventory)

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        self.health -= effect.damage

        # Play hurt sound
        self.shader_state.handle_input('hurt', colour = [1,1,1,1], direction = [1,0.5])
        self.hit_loot()

        if self.health > 0:  # Still alive
            pass
        else:  # dead
            self.currentstate.handle_input('open')
            self.game_objects.world_state.objects.set_bool(self.game_objects.map.biome_room_name,'loot_container',self.ID_key,True)

        return effect

    def hit_loot(self):#sput out amvers when hit
        self.loot_emitter.emit_item('amber_droplet', quantity=random.randint(1,3))
