import pygame

from gameplay.entities.base.character import Character
from engine.utils import read_files
from gameplay.entities.player.entity_shader_manager import EntityShaderManager
from gameplay.entities.player.player_states import PlayerStates
from gameplay.entities.player import states_death
from gameplay.entities.player.backpack import backpack
from gameplay.entities.shared.modifiers import modifier_damage, modifier_movement
from gameplay.entities.visuals.cosmetics.slash import Slash
from gameplay.entities.player.sword import Sword
from gameplay.entities.player.abilities.ability_manager import AbilityManager
from gameplay.entities.shared.status.wet import Wet
from engine import constants as C

class Player(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sounds = read_files.load_sounds_dict('assets/audio/sfx/entities/player/')
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/player/texture/', game_objects)
        self.normal_maps = read_files.load_sprites_dict('assets/sprites/entities/player/normal/', game_objects)
        self.image = self.sprites['idle'][0]
        self.shader_state = EntityShaderManager(self)
        self.shader_state.define_size(self.image.size)
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = pygame.Rect(pos[0], pos[1], 16, 35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes
        self.prev_true_pos = self.true_pos.copy()#to save the previous position

        self.max_health = 15
        self.max_spirit = 4
        self.health = 6
        self.spirit = 2

        self.projectiles = game_objects.fprojectiles
        self.sword = Sword(self)
        self.abilities = AbilityManager(self)#spirit (thunder,migawari etc) and movement /dash, double jump and wall glide)

        self.flags = {'ground': True, 'invincibility': False, 'shroompoline': False, 'attack_able': True}# flags to check if on ground (used for jumpåing), #a flag to make sure you can only swing sword when this is False
        self.currentstate = PlayerStates(self)#states_player.Idle_main(self)
        self.death_state = states_death.Idle(self)#this one can call "normal die" or specifal death (for example cultist encounter)

        self.backpack = backpack.Backpack(self)

        self.timers = []#a list where timers are append whe applicable, e.g. wet status
        self.timer_jobs = {'wet': Wet(self, 60)}#these timers are activated when promt and a job is appeneded to self.timer.

        self.damage_manager = modifier_damage.DamageManager(self)
        self.movement_manager = modifier_movement.MovementManager()
        self.reset_movement()                

        self.colliding_platform = None#save the last collising platform

    def ramp_down_collision(self, ramp):#when colliding with platform beneth
        super().ramp_down_collision(ramp)
        self.colliding_platform = ramp#save the latest platform

    def down_collision(self, block):#when colliding with platform beneth
        super().down_collision(block)
        self.movement_manager.handle_input('ground')
        self.colliding_platform = block#save the latest platform

    def right_collision(self, block, type = 'Wall'):
        super().right_collision(block, type)
        self.movement_manager.handle_input('wall')
        self.colliding_platform = block#save the latest platform

    def left_collision(self, block, type = 'Wall'):
        super().left_collision(block, type)
        self.movement_manager.handle_input('wall')
        self.colliding_platform = block#save the latest platform

    def update_vel(self, dt):#called from hitsop_states
        context = self.movement_manager.resolve()

        self.velocity[1] += dt * (context.gravity - self.velocity[1] * context.friction[1]) + context.velocity[1]
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0] * self.acceleration[0] - self.velocity[0] * context.friction[0]) + context.velocity[0]

    def take_dmg(self, dmg = 1, effects = []):#called from collisions
        return self.damage_manager.take_dmg(dmg, effects)#called from damage_manager: trturns true or false dependign on apply damaage was called or not

    def apply_damage(self, context):#called from damage_manager
        self.flags['invincibility'] = True
        self.health -= context.dmg
        self.game_objects.ui.hud.remove_hearts(context.dmg)# * self.dmg_scale)#update UI

        if self.health > 0:#check if dead¨
            self.game_objects.timer_manager.start_timer(C.invincibility_time_player, self.on_invincibility_timeout)#adds a timer to timer_manager and sets self.invincible to false after a while
            self.shader_state.handle_input('Hurt')#turn white and shake
            self.shader_state.handle_input('Invincibile')#blink a bit
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state or interupt attacks?
            self.emit_particles(lifetime = 40, scale = 3, colour=[0,0,0,255], fade_scale = 7,  number_particles = 60 )
            self.game_objects.cosmetics.add(Slash(self.hitbox.center,self.game_objects))#make a slash animation

            self.game_objects.time_manager.modify_time(time_scale = 0, duration = 20)
            self.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 20, scale = 0.9)

            self.game_objects.post_process.append_shader('chromatic_aberration', duration = 20)

            for effect in context.effects:#e.g. knock back
                effect()#apply the effects

        else:#if health < 0
            self.game_objects.signals.emit('player_died')#emit a signal that player died
            self.death_state.die()#depending on gameplay state, different death stuff should happen

    def die(self):#called from idle death_state, also called from vertical acid
        #self.animation.update()#make sure you get the new animation
        self.game_objects.cosmetics.add(Blood(self.hitbox.center, self.game_objects, dir = self.dir))#pause first, then slow motion
        self.game_objects.time_manager.modify_time(time_scale = 0.4, duration = 100)#sow motion
        self.game_objects.time_manager.modify_time(time_scale = 0, duration = 50)#freeze

    def dead(self):#called when death animation is finished
        self.game_objects.world_state.update_statistcis('death')#count the number of times aila has died
        self.game_objects.game.state_manager.enter_state(state_name = 'death')

    def heal(self, health = 1):
        self.health += health
        self.game_objects.ui.hud.update_hearts()#update UI

    def consume_spirit(self, spirit = 1):
        self.spirit -= spirit
        self.game_objects.ui.hud.remove_spirits(spirit)#update UI

    def add_spirit(self, spirit = 1):
        self.spirit += spirit
        self.game_objects.ui.hud.update_spirits()#update UI

    def reset_movement(self):#called when loading new map or entering conversations
        self.acceleration =  [0, C.acceleration[1]]
        self.friction = C.friction_player.copy()
        #self.movement_manager.clear_modifiers()#TODO probably not all should be cleared

    def update_render(self, dt):#called in group
        self.hitstop_states.update_render(dt)        

    def update(self, dt):
        self.prev_true_pos = self.true_pos.copy()#save previous position for interpolation
        self.movement_manager.update(dt)#update the movement manager
        self.hitstop_states.update(dt)
        self.backpack.radna.update()#update the radnas
        self.update_timers(dt)

    def draw(self, target):#called in group
        alpha = self.game_objects.game.game_loop.alpha
        interp_x = self.prev_true_pos[0] + (self.true_pos[0] - self.prev_true_pos[0]) * alpha
        interp_y = self.prev_true_pos[1] + (self.true_pos[1] - self.prev_true_pos[1]) * alpha

        self.blit_pos = [interp_x - self.game_objects.camera_manager.camera.interp_scroll[0], interp_y - self.game_objects.camera_manager.camera.interp_scroll[1]]#save float position for screen manager
        blit_pos = [int(self.blit_pos[0]), int(self.blit_pos[1])]#bit at interget position, and let screen manager hanfle the sub pixel rendering
        self.shader_state.draw(self.image, target, blit_pos, flip = self.dir[0] > 0)
        #self.game_objects.game.display.render(self.image, target, position = blit_pos , flip = self.dir[0] > 0, shader = self.shader)#shader render

        #normal map draw
        self.game_objects.shaders['normal_map']['direction'] = -self.dir[0]#the normal map shader can invert the normal map depending on direction
        self.game_objects.game.display.render(self.normal_maps[self.animation.animation_name][self.animation.image_frame], self.game_objects.lights.normal_map, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.game_objects.shaders['normal_map'])#should be rendered on the same position, image_state and frame as the texture

    def update_timers(self, dt):
        for timer in self.timers:
            timer.update(dt)

    def on_cayote_timeout(self):
        self.flags['ground'] = False
        self.colliding_platform = None

    def on_shroomjump_timout(self):
        self.flags['shroompoline'] = False