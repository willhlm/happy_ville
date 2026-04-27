import pygame

from gameplay.entities.base.character import Character
from engine.utils import read_files
from gameplay.entities.player.combat_tracker import CombatTracker
from gameplay.entities.player.death_manager import DeathManager
from gameplay.entities.player.hazard_resolver import PlayerHazardResolver
from gameplay.entities.player.player_states.state_manager import StateManager
from gameplay.entities.player.backpack import backpack
from gameplay.entities.player.grounding import PlayerGrounding
from gameplay.entities.visuals.cosmetics.slash import Slash
from gameplay.entities.player.sword.sword import Sword
from gameplay.entities.player.ability_unlocks.progression_manager import PlayerProgressionManager
from gameplay.entities.shared.status.status_component import StatusComponent
from gameplay.entities.shared.status.wet import Wet
from engine import constants as C

class Player(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/player/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/player/default/', game_objects, normal_map = True)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes
        self.prev_true_pos = self.true_pos.copy()#to save the previous position

        self.vitals.set_max_health(20)
        self.vitals.set_max_spirit(4)
        self.vitals.set_health(2)
        self.vitals.set_spirit(2)

        self.combat_tracker = CombatTracker()
        self.sword = Sword(self)

        self._reset_flags()                
        self.grounding = PlayerGrounding(self)
        self.currentstate = StateManager(self)
        self.progression = PlayerProgressionManager(self)
        self.death_manager = DeathManager(self)
        self.hazard_resolver = PlayerHazardResolver(self)    

        self.backpack = backpack.Backpack(self)
        self.status_component = StatusComponent(self, registry={'wet': lambda entity: Wet(entity, 60)})

        self.hit_component.set_invincibility_time(C.invincibility_time_player)
        self.reset_movement()     
        
    def update_vel(self, dt):#called from hitsop_states
        context = self.movement_manager.resolve()
        self._movement_context = context

        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        if self.velocity[1] < 0:
            self.velocity[1] = max(self.velocity[1], -context.max_vel[1])

        self.velocity[0] += dt * (self.dir[0] * self.acceleration[0] - self.velocity[0] * context.friction[0]) + context.velocity[0]

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        if self.vitals.health <= 0:
            return effect

        self.vitals.damage(effect.damage)
        self.game_objects.ui.hud.meters.remove_hearts(effect.damage)# * self.dmg_scale)#update UI

        if self.vitals.health > 0:  # Still alive
            self.shader_state.handle_input('hurt')#turn white and shake
            self.shader_state.handle_input('invincibile')#blink a bit
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state or interupt attacks?
            effect.defender_callbacks.pop('particles', None)#remove any partitlce effect set by the projectile
            self.game_objects.particles.emit("burst", pos = self.hitbox.center, n=60, colour = [0, 0, 0, 255])
            #self.emit_particles(lifetime = 40, scale = 3, colour=[0,0,0,255], fade_scale = 7,  number_particles = 60 )
            self.game_objects.cosmetics.add(Slash(self.hitbox.center,self.game_objects))#make a slash animation

            self.game_objects.time_manager.modify_time(time_scale = 0, duration = 20)
            self.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 20, scale = 0.9)

            self.game_objects.post_process.append_shader('chromatic_aberration', duration = 20)
        else:  # dead
            self.game_objects.signals.emit('player_died')#emit a signal that player died
            self.death_manager.die()
        return effect

    def reset_movement(self):#called when loading new map or entering conversations
        self.acceleration =  [0, C.acceleration[1]]
        self.friction = C.friction_player.copy()
        self._reset_flags()        
        self.movement_manager.clear_modifiers()#maybe probably not all should be cleared?

    def heal_vitals(self, health=1):
        self.vitals.heal(health)
        self.game_objects.ui.hud.meters.update_hearts()#update UI

    def consume_spirit_cost(self, spirit=1):
        self.vitals.consume_spirit(spirit)
        self.game_objects.ui.hud.meters.remove_spirits(spirit)#update UI

    def gain_spirit(self, spirit=1):
        self.vitals.add_spirit(spirit)
        self.game_objects.ui.hud.meters.update_spirits()#update UI

    @property
    def abilities(self):
        return self.progression.abilities

    def _reset_flags(self):
        self.flags = {'ground': False, 'shroompoline': False, 'attack_able': True, 'grounddash': True, 'sprint_chain_active': False}# flags to check if on ground (used for jumpåing), #a flag to make sure you can only swing sword when this is False        

    def update_render(self, dt):#called in group
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.shader_state.update_render(scaled_dt)        

    def update(self, dt):
        self.prev_true_pos = self.true_pos.copy()#save previous position for interpolation
        self.hitstop.update(dt)
        scaled_dt = self.hitstop.get_sim_dt(dt)

        self.abilities.update(scaled_dt)
        self.movement_manager.update(scaled_dt)#update the movement manager: modifers 
        self.update_vel(scaled_dt)

    def post_physics_update(self, dt):
        scaled_dt = self.hitstop.get_sim_dt(dt)
        self.consume_contact_state()
        self.currentstate.update(scaled_dt)
        self.animation.update(scaled_dt)
        self.backpack.radna.update()
        self.status_component.update(scaled_dt)

    def consume_contact_state(self):
        super().consume_contact_state()
        self.grounding.consume_contact_state()
        self.movement_manager.consume_contact_state()

    def draw(self, target):#called in group
        alpha = self.game_objects.game.game_loop.alpha
        interp_x = self.prev_true_pos[0] + (self.true_pos[0] - self.prev_true_pos[0]) * alpha
        interp_y = self.prev_true_pos[1] + (self.true_pos[1] - self.prev_true_pos[1]) * alpha

        self.blit_pos = [interp_x - self.game_objects.camera_manager.camera.interp_scroll[0], interp_y - self.game_objects.camera_manager.camera.interp_scroll[1]]#save float position for screen manager
        blit_pos = [int(self.blit_pos[0]), int(self.blit_pos[1])]#bit at interget position, and let screen manager hanfle the sub pixel rendering
        self.shader_state.draw(self.image, target, blit_pos, flip = self.dir[0] > 0)

    def on_cayote_timeout(self):
        self.grounding.on_coyote_timeout()

    def begin_coyote_time(self):
        self.grounding.begin_coyote_time()

    def end_coyote_time(self):
        self.grounding.end_coyote_time()

    def on_shroomjump_timout(self):
        self.flags['shroompoline'] = False

    def on_grounddash_timout(self):
        self.flags['grounddash'] = True

    def on_crush(self, block):
        self.hazard_resolver.handle_crush(block)
