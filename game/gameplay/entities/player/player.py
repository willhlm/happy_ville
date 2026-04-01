import pygame

from gameplay.entities.base.character import Character
from engine.utils import read_files
from gameplay.entities.player.death_manager import DeathManager
from gameplay.entities.player.hazard_resolver import PlayerHazardResolver
from gameplay.entities.player.player_states.state_manager import StateManager
from gameplay.entities.player.backpack import backpack
from gameplay.entities.visuals.cosmetics.slash import Slash
from gameplay.entities.player.sword.sword import Sword
from gameplay.entities.player.abilities.ability_manager import AbilityManager
from gameplay.entities.shared.status.wet import Wet
from engine import constants as C
from gameplay.entities.visuals.cosmetics import Blood
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

        self.max_health = 20
        self.max_spirit = 4
        self.health = 20
        self.spirit = 2

        self.sword = Sword(self)
        self.abilities = AbilityManager(self)#spirit (thunder,migawari etc) and movement /dash, double jump and wall glide)

        self.flags = {'ground': False, 'shroompoline': False, 'attack_able': True, 'grounddash': True, 'sprint_chain_active': False}# flags to check if on ground (used for jumpåing), #a flag to make sure you can only swing sword when this is False
        self.currentstate = StateManager(self)#states_player.Idle_main(self)
        self.death_manager = DeathManager(self)
        self.hazard_resolver = PlayerHazardResolver(self)

        self.backpack = backpack.Backpack(self)

        self.timers = []#a list where timers are append whe applicable, e.g. wet status
        self.timer_jobs = {'wet': Wet(self, 60)}#these timers are activated when promt and a job is appeneded to self.timer.

        self.hit_component.set_invinsibility_time(C.invincibility_time_player)
        self.reset_movement()     
        
    def on_ramp_collision(self, side, ramp):
        super().on_ramp_collision(side, ramp)
        if side == 'bottom':
            self.movement_manager.handle_input('ground')
            self.flags['ground'] = True

    def on_platform_vertical_collision(self, side, block):
        super().on_platform_vertical_collision(side, block)
        if side == 'bottom':
            self.movement_manager.handle_input('ground')
            self.flags['ground'] = True

    def on_platform_side_collision(self, side, block, collision_type = 'Wall'):
        super().on_platform_side_collision(side, block, collision_type)
        self.movement_manager.handle_input('wall')

    def update_vel(self, dt):#called from hitsop_states
        context = self.movement_manager.resolve()

        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        if self.velocity[1] < 0:
            self.velocity[1] = max(self.velocity[1], -context.max_vel[1])

        self.velocity[0] += dt * (self.dir[0] * self.acceleration[0] - self.velocity[0] * context.friction[0]) + context.velocity[0]

    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        if self.health <= 0:
            return effect

        self.health = max(0, self.health - effect.damage)
        self.game_objects.ui.hud.meters.remove_hearts(effect.damage)# * self.dmg_scale)#update UI

        if self.health > 0:  # Still alive
            self.shader_state.handle_input('Hurt')#turn white and shake
            self.shader_state.handle_input('Invincibile')#blink a bit
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

    def start_death_effects(self):
        #self.animation.update()#make sure you get the new animation
        self.game_objects.cosmetics.add(Blood(self.hitbox.center, self.game_objects, dir = self.dir))#pause first, then slow motion
        self.game_objects.time_manager.modify_time(time_scale = 0.4, duration = 100)#sow motion
        self.game_objects.time_manager.modify_time(time_scale = 0, duration = 50)#freeze

    def dead(self):#called when death animation is finished
        self.game_objects.world_state.statistics_state.update_statistic('death')#count the number of times aila has died
        self.game_objects.game.state_manager.enter_state(state_name = 'death')

    def heal(self, health = 1):
        self.health += health
        self.game_objects.ui.hud.meters.update_hearts()#update UI

    def consume_spirit(self, spirit = 1):
        self.spirit -= spirit
        self.game_objects.ui.hud.meters.remove_spirits(spirit)#update UI

    def add_spirit(self, spirit = 1):
        self.spirit += spirit
        self.game_objects.ui.hud.meters.update_spirits()#update UI

    def reset_movement(self):#called when loading new map or entering conversations
        self.acceleration =  [0, C.acceleration[1]]
        self.friction = C.friction_player.copy()
        self.flags['sprint_chain_active'] = False
        #self.movement_manager.clear_modifiers()#TODO probably not all should be cleared

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
        self.currentstate.update(scaled_dt)#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update(scaled_dt)#need to be after currentstate since animation will animate the current state -> i suupose it should be in update_physcis?

        self.backpack.radna.update()#update the radnas
        self.update_timers(scaled_dt)

    def draw(self, target):#called in group
        alpha = self.game_objects.game.game_loop.alpha
        interp_x = self.prev_true_pos[0] + (self.true_pos[0] - self.prev_true_pos[0]) * alpha
        interp_y = self.prev_true_pos[1] + (self.true_pos[1] - self.prev_true_pos[1]) * alpha

        self.blit_pos = [interp_x - self.game_objects.camera_manager.camera.interp_scroll[0], interp_y - self.game_objects.camera_manager.camera.interp_scroll[1]]#save float position for screen manager
        blit_pos = [int(self.blit_pos[0]), int(self.blit_pos[1])]#bit at interget position, and let screen manager hanfle the sub pixel rendering
        self.shader_state.draw(self.image, target, blit_pos, flip = self.dir[0] > 0)

    def update_timers(self, dt):
        for timer in self.timers:
            timer.update(dt)

    def on_cayote_timeout(self):
        self.flags['ground'] = False
        self.standing_platform = None

    def on_shroomjump_timout(self):
        self.flags['shroompoline'] = False

    def on_grounddash_timout(self):
        self.flags['grounddash'] = True

    def on_crush(self, block):
        self.hazard_resolver.handle_crush(block)
