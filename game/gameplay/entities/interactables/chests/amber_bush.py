from engine.utils import read_files
from gameplay.entities.interactables.chests.base.loot_containers import LootContainers
from . import amber_bush_states

class AmberBush(LootContainers):#amber source
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects, state, ID_key)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/interactables/amber_tree/')
        self.amber_per_hit = 10
        self.currentstate = amber_bush_states.Idle(self)
        self.health = 3

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""

        if self.health > 0:
            self.health -= effect.damage

            # Play hurt sound
            self.shader_state.handle_input('hurt', colour = [1,1,1,1], direction = [1,0.5])
            self.hit_loot()
            self.currentstate.handle_input('open')
            self.game_objects.world_state.objects.set_bool(self.game_objects.map.biome_room_name,'loot_container',self.ID_key,True)
        else:
            pass

        return effect

    def hit_loot(self):#sput out amvers when hit
        self.loot_emitter.emit_item('amber_droplet', quantity=self.amber_per_hit)
