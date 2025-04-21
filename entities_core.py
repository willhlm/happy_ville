import pygame
import animation, particles
import constants as C

from states import states_basic, states_shader, hitstop_states

class Staticentity(pygame.sprite.Sprite):#all enteties
    def __init__(self, pos, game_objects):
        super().__init__()
        self.game_objects = game_objects
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)
        self.true_pos = list(self.rect.topleft)
        self.blit_pos = self.true_pos.copy()

        self.bounds = [-200, 800, -100, 350]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.shader = None#which shader program to run
        self.dir = [-1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: needed when rendering the direction

    def group_distance(self):
        if self.blit_pos[0] < self.bounds[0] or self.blit_pos[0] > self.bounds[1] or self.blit_pos[1] < self.bounds[2] or self.blit_pos[1] > self.bounds[3]:
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause

    def draw(self, target):#called just before draw in group
        self.blit_pos = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]
        self.game_objects.game.display.render(self.image, target, position = self.blit_pos, flip = self.dir[0] > 0, shader = self.shader)#shader render

    def kill(self):
        self.release_texture()#before killing, need to release the textures (but not the onces who has a pool)
        super().kill()

class Animatedentity(Staticentity):#animated stuff, i.e. cosmetics
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):#called from aniumation when the animation is finished
        self.currentstate.increase_phase()

    def release_texture(self):#called when .kill() and empty group
        for state in self.sprites.keys():
            for frame in range(0,len(self.sprites[state])):
                self.sprites[state][frame].release()

class Platform_entity(Animatedentity):#Things to collide with platforms
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = {'ramp': True, 'one_way':True}#a flag for entities to go through ramps from side or top
        self.velocity = [0,0]

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    def update_rect_y(self):
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos[1] = self.rect.top

    def update_rect_x(self):
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos[0] = self.rect.left

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.true_pos = list(self.rect.topleft)
        self.hitbox.midbottom = self.rect.midbottom

    def update_true_pos_x(self):#called from Engine.platform collision. The velocity to true pos need to be set in collision if group distance should work proerly for enemies (so that the velocity is not applied when removing the sprite from gorup)
        self.true_pos[0] += self.slow_motion*self.game_objects.game.dt*self.velocity[0]
        self.rect.left = round(self.true_pos[0])#should be int -> round fixes gliding on bubble
        self.update_hitbox()

    def update_true_pos_y(self):#called from Engine.platform collision
        self.true_pos[1] += self.slow_motion*self.game_objects.game.dt*self.velocity[1]
        self.rect.top = round(self.true_pos[1])#should be int -> round fixes gliding on bubble
        self.update_hitbox()

    #ramp collisions
    def ramp_top_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.top = ramp.target
        self.collision_types['top'] = True
        self.velocity[1] = 2#need to have a value to avoid "dragin in air" while running
        self.velocity[0] = 0#need to have a value to avoid "dragin in air" while running

    def ramp_down_collision(self, ramp):#called from collusion in clollision_ramp
        self.hitbox.bottom = ramp.target
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')
        self.velocity[1] = C.max_vel[1] + 10#make aila sticj to ground to avoid falling animation: The extra gravity on ramp

    #pltform collisions.
    def right_collision(self, block, type = 'Wall'):
        self.hitbox.right = block.hitbox.left
        self.collision_types['right'] = True
        self.currentstate.handle_input(type)

    def left_collision(self, block, type = 'Wall'):
        self.hitbox.left = block.hitbox.right
        self.collision_types['left'] = True
        self.currentstate.handle_input(type)

    def down_collision(self, block):
        self.hitbox.bottom = block.hitbox.top
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')

    def top_collision(self, block):
        self.hitbox.top = block.hitbox.bottom
        self.collision_types['top'] = True
        self.velocity[1] = 0

    def limit_y(self):#limits the velocity on ground, onewayup. But not on ramps: it makes a smooth drop
        self.velocity[1] = 1.2/self.game_objects.game.dt

class Character(Platform_entity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0, C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()

        self.shader_state = states_shader.Idle(self)
        self.hitstop_states = hitstop_states.Idle(self)

    def update(self):
        self.update_vel()
        self.currentstate.update()#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update()#need to be after currentstate since animation will animate the current state
        self.shader_state.update()#need to be after animation

    def update_vel(self):#called from hitsop_states
        self.velocity[1] += self.slow_motion*self.game_objects.game.dt*(self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1],self.max_vel[1]*self.game_objects.game.dt)#set a y max speed#
        self.velocity[0] += self.slow_motion*self.game_objects.game.dt*(self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def take_dmg(self, dmg):
        if self.flags['invincibility']: return
        self.health -= dmg
        self.flags['invincibility'] = True

        try:#TODO add hit sounds to all enteties
            self.game_objects.sound.play_sfx(self.sounds['hit'][0], vol = 0.2)
        except:
            pass

        if self.health > 0:#check if dead
            self.game_objects.timer_manager.start_timer(C.invincibility_time_enemy, self.on_invincibility_timeout)
            self.shader_state.handle_input('Hurt')#turn white and shake
            self.AI.handle_input('Hurt')
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state -> can handle hitstop if we want
            self.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
        else:#if dead
            self.game_objects.camera_manager.camera_shake(amplitude = 15, duration = 15, scale = 0.9)
            self.flags['aggro'] = False
            self.AI.deactivate()
            self.currentstate.enter_state('Death')#overrite any state and go to deat
        return True#return truw to show that damage was taken

    def knock_back(self, dir):
        amp_x = 50
        self.velocity[0] = dir[0] * amp_x * (1 - abs(dir[1]))
        self.velocity[1] = -dir[1] * 10

    def emit_particles(self, type = 'Circle', number_particles = 20, **kwarg):
        for i in range(0, number_particles):
            obj1 = getattr(particles, type)(self.hitbox.center, self.game_objects, **kwarg)
            self.game_objects.cosmetics.add(obj1)

    def draw(self, target):
        self.shader_state.draw()#for entetirs to turn white
        super().draw(target)

    def on_invincibility_timeout(self):#runs when sword timer runs out
        self.flags['invincibility'] = False

    def on_attack_timeout(self):#when attack cooldown timer runs out
        self.flags['attack_able'] = True
