from engine import constants as C
from gameplay.entities.shared.states import hitstop_states, states_shader

from gameplay.entities.base.platform_entity import PlatformEntity
from gameplay.visuals.particles import particles

class Character(PlatformEntity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0, C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()

        self.shader_state = states_shader.Idle(self)
        self.hitstop_states = hitstop_states.Idle(self)

    def update(self, dt):
        self.update_vel(dt)
        self.currentstate.update(dt)#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update(dt)#need to be after currentstate since animation will animate the current state

    def update_render(self, dt):        
        self.shader_state.update_render(dt)

    def update_vel(self, dt):#called from hitsop_states
        self.velocity[1] += dt * (self.acceleration[1] - self.velocity[1] * self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1], self.max_vel[1])#set a y max speed#
        self.velocity[0] += dt * (self.dir[0]*self.acceleration[0] - self.friction[0] * self.velocity[0])

    def take_dmg(self, dmg = 1, effects = []):
        if self.flags['invincibility']: return
        self.health -= dmg#take damage
        self.flags['invincibility'] = True

        try:#TODO add hurt sounds to all enteties
            self.game_objects.sound.play_sfx(self.sounds['hit'][0], vol = 0.2)
        except:
            pass

        if self.health > 0:#check if dead
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)            
            self.shader_state.handle_input('Hurt')#turn white and shake
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            self.game_objects.camera_manager.camera_shake(amplitude = 10, duration = 15, scale = 0.9)
            
            for effect in effects:#e.g. knock back
                effect()
        else:#if dead
            self.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
            self.flags['aggro'] = False
            self.currentstate.enter_state('Death')#overrite any state and go to deat
        return True#return truw to show that damage was taken

    def knock_back(self, amp, dir):
        self.velocity[0] = dir[0] * amp[0] * (1 - abs(dir[1]))
        self.velocity[1] = -dir[1] * amp[1]

    def emit_particles(self, type = 'Circle', number_particles = 20, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, type)(self.hitbox.center, self.game_objects, **kwarg)
            self.game_objects.cosmetics.add(obj1)

    def draw(self, target):        
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.shader)#shader render        

    def on_invincibility_timeout(self):#runs when sword timer runs out
        self.flags['invincibility'] = False

    def on_attack_timeout(self):#when attack cooldown timer runs out
        self.flags['attack_able'] = True

    def on_hurt_timeout(self):#starts when entering hurt state, and make sure that you don't eneter again until timer runs out
        self.flags['hurt_able'] = False