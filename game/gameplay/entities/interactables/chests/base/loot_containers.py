import pygame, random
from engine.utils import read_files
from engine import constants as C
from gameplay.entities.interactables.base.interactables import Interactables
from . import loot_container_states

class LootContainers(Interactables):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/chests/' + type(self).__name__.lower() + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

        self.health = 3
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.flags = {'invincibility': False}

        if state:
            self.currentstate = loot_container_states.Interacted(self)
            self.flags['invincibility'] = True
        else:
            self.currentstate = loot_container_states.Idle(self)

    def update_render(self, dt):
        self.shader_state.update_render(dt)

    def loots(self):#this is called when the opening animation is finished
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = self.game_objects.registry.fetch('items', key)(self.hitbox.midtop, self.game_objects)
                obj.spawn_position()
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def on_invincibility_timeout(self):
        self.flags['invincibility'] = False
   
    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        self.health -= effect.damage
        self.flags['invincibility'] = True
        
        # Play hurt sound
        self.apply_hit_feedback(effect)
        self.shader_state.handle_input('Hurt', colour = [1,1,1,1], direction = [1,0.5])
        self.hit_loot()        
        
        if self.health > 0:  # Still alive
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
        else:  # dead
            self.currentstate.handle_input('open')
            self.game_objects.world_state.state[self.game_objects.map.level_name]['loot_container'][self.ID_key] = True#write in the state dict that this has been picked up
 
    def apply_hit_feedback(self, effect):
        """Execute defender callbacks"""
        attacker_dir = effect.meta.get('attacker_dir', [1, 0])        
        for callback in effect.defender_callbacks.values():# Execute all defender callbacks in order
            callback(self, effect, attacker_dir)

    def hit_loot(self):#sput out amvers when hit
        for i in range(0, random.randint(1,3)):
            obj = Amber_droplet(self.hitbox.midtop, self.game_objects)
            self.game_objects.loot.add(obj)