from engine.utils import read_files
from gameplay.entities.interactables.chests.base.loot_containers import LootContainers
from gameplay.entities.shared.components.loot.item_loot_emitter import ItemLootEmitterComponent
from . import amber_bush_states

class AmberBushSmall(LootContainers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/interactables/amber_tree/')
        self.currentstate = amber_bush_states.Hit2(self)
        self.amber_per_hit = 5
        self.health = 1
        self.loot_emitter = ItemLootEmitterComponent(self, spawn_velocity=[0, -3.5], spawn_velocity_range=[2, 1])

    def on_collision(self, entity):#one time collision
        pass

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""

        if self.health > 0:
            self.health -= effect.damage

            # Play hurt sound
            self.shader_state.handle_input('hurt', colour = [1,0.9,0.7,0.3], direction = [1,0.5], frequency = 120, amplitude = 0.7)
            self.hit_loot()
            self.currentstate.handle_input('open')
            self.game_objects.world_state.objects.set_bool(self.game_objects.map.biome_room_name,'loot_container',self.ID_key,True)
        else:
            pass

        return effect

    def hit_loot(self):#sput out amvers when hit
        self.loot_emitter.emit_item('amber_droplet', quantity=self.amber_per_hit)
