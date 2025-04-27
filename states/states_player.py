import entities, sys, random, math
from states_entity import Entity_States
import constants as C

def sign(number):
    if number > 0: return 1
    else: return -1

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_input(self, input, **kwarg):
        pass

    def enter_state(self, newstate, **kwarg):
        state = newstate[:newstate.rfind('_')]#get the name up to last _ (remove pre, main, post)
        if self.entity.states[state]:
            self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys
            return True

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_release_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay states
        value = event['l_stick']#the avlue of the press

        self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

    def do_ability(self):#called when pressing B (E). This is needed if all of them do not have pre animation, or vice versa
        if self.entity.abilities.equip == 'Thunder' or self.entity.abilities.equip == 'Slow_motion' or self.entity.abilities.equip == 'Bow':
            self.enter_state(self.entity.abilities.equip + '_pre')
        else:
            self.enter_state(self.entity.abilities.equip + '_main')

class Idle_main(Player_states):
    def __init__(self, entity):
        super().__init__(entity)
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_pre')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('Jump_main')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('Ground_dash_pre')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()        
        elif event[-1]=='rt':#depends on if the abillities have pre or main animation
            input.processed()
            self.enter_state('Heal_pre')              

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_input(self, input, **kwarg):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Run_pre')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] == 0:
            state = 'Sword_stand' + str(int(self.entity.sword.swing)+1) + '_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0:
            self.enter_state('Sword_up_main')

class Walk_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.particle_timer = 0
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            self.running_particles()
            self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'])

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('Fall_pre')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout,ID = 'cayote')

    def running_particles(self):
        #particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        #self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('Jump_main')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('Ground_dash_pre')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_input(self, input, **kwarg):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1])<0.8:
            state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1]>0.8:
            self.enter_state('Sword_up_main')

class Run_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.particle_timer = 0
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            self.running_particles()
            #self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'])

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('Fall_pre')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def increase_phase(self):
        self.enter_state('Run_main')

    def running_particles(self):
        #particle = self.entity.running_particles(self.entity.hitbox.midbottom, self.entity.game_objects)
        #self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('Jump_main')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('Ground_dash_pre')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_input(self, input, **kwarg):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] == 0:
            self.enter_state('Run_post')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1])<0.8:
            state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1]>0.8:
            self.enter_state('Sword_up_main')

class Run_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.particle_timer = 0
        self.sfx_loop_time = int(18 * self.entity.game_objects.game.dt)
        self.sfx_timer = 1

    def update(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            pass
            #self.running_particles()

        self.sfx_timer -= 1
        if self.sfx_timer == 0:
            self.entity.game_objects.sound.play_sfx(self.entity.sounds['run'][self.sfx_timer%2], vol = 0.8)
            self.sfx_timer = self.sfx_loop_time

        if not self.entity.collision_types['bottom']:#TODO disable this one while entering ramp
            self.enter_state('Fall_pre')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def enter_state(self, new_state):
        #self.sfx_channel.stop()
        super().enter_state(new_state)

    def running_particles(self):
        #particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        #self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('Jump_main')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('Ground_dash_pre')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()

    def handle_input(self, input, **kwarg):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] == 0:
            self.enter_state('Run_post')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1]) < 0.8:
            state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0.8:
            self.enter_state('Sword_up_main')

class Run_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_pre')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('Jump_main')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('Ground_dash_pre')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()

    def handle_input(self, input, **kwarg):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Run_pre')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1]==0:
            state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

        elif self.entity.dir[1]>0:
            self.enter_state('Sword_up_main')

    def increase_phase(self):
        self.enter_state('Idle_main')

class Jump_main(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['jump'][random.randint(0,2)], vol = 0.1)
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.velocity[1] = C.jump_vel_player
        #self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.flags['ground'] = False
        self.wall_dir = kwarg.get('wall_dir', False)
        self.shroomboost = 1#if landing on shroompoline and press jump, this vakue is modified
        if self.entity.colliding_platform: self.air_timer = self.entity.colliding_platform.jumped()#jump charactereistics is set from the platform    
        self.entity.game_objects.cosmetics.add(entities.Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.dir, state = 'two'))#dust

    def update(self):
        self.jump_dash_timer -= self.entity.game_objects.game.dt
        self.air_timer -= self.entity.game_objects.game.dt
        if self.air_timer > 0:
            self.entity.velocity[1] = C.jump_vel_player * self.shroomboost
        if self.entity.velocity[1] > 0.7:
            self.enter_state('Fall_pre')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1]=='lb':
            input.processed()
            if self.jump_dash_timer > 0:
                if self.wall_dir:
                    self.entity.dir[0] = -self.wall_dir[0]#if the jmup came from wall glide, jump away
                self.enter_state('Dash_jump_main')
            else:
                self.enter_state('Air_dash_pre')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='a':
            input.processed()
            if self.entity.flags['shroompoline']:
                self.shroomboost = 2

    def handle_release_input(self,input):#when release space
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.entity.velocity[1] = 0.5*self.entity.velocity[1]
            self.enter_state('Fall_pre')

    def handle_input(self, input, **kwarg):
        if input == 'belt':
            self.enter_state('Belt_glide_main')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('Sword_up_main')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('Sword_down_main')
        else:#right or left
            state = 'Sword_jump' + str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

class Fall_pre(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.wall_dir = kwarg.get('wall_dir', False)

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('Jump_main', wall_dir = self.wall_dir)
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='lb':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('Ground_dash_pre', wall_dir = self.wall_dir)
            elif self.enter_state('Air_dash_pre'):
                input.processed()
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_input(self, input, **kwarg):
        if input == 'Wall':
            self.enter_state('Wall_glide_main', **kwarg)
        elif input == 'belt':
            self.enter_state('Belt_glide_main')
        elif input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('Run_main')
            else:
                self.enter_state('Idle_main')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('Sword_up_main')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('Sword_down_main')
        else:#right or left
            self.enter_state('Sword_fall_main', frame = self.entity.animation.frame)
            self.entity.sword.swing = not self.entity.sword.swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Fall_main')

class Fall_main(Fall_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Heal_pre(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def handle_release_input(self, input):
        event = input.output()  
        if event[-1] == 'rt':#if releasing the button
            input.processed()   
            self.enter_state('Idle_main')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_state('Heal_main')    

class Heal_main(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)     
        self.heal_cost = 1   

    def handle_release_input(self, input):
        event = input.output()        
        if event[-1] == 'rt':#if releasing the button
            input.processed()   
            self.enter_state('Idle_main')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.entity.heal()
        self.entity.backpack.inventory.remove('amber_droplet', self.heal_cost)
        self.enter_state('Heal_main')   

class Wall_glide_main(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.flags['ground'] = True#used for jumping: sets to false in cayote timer and in jump state
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.movement_manager.add_modifier('Wall_glide')        
        if self.entity.collision_types['right']:
            self.dir = [1,0]
        else:
            self.dir = [-1,0]

    def update(self):#is needed
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('Fall_pre', wall_dir = self.dir)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            #self.entity.dir[0] *= -1#if we want to jump vertically
            self.entity.velocity[0] = -self.dir[0]*10
            self.entity.velocity[1] = -7#to get a vertical velocity
            input.processed()
            self.enter_state('Jump_main', wall_dir = self.dir)
        elif event[-1] == 'lb':
            input.processed()
            self.entity.dir[0] *= -1
            self.enter_state('Ground_dash_pre')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        curr_dir = self.entity.dir[0]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

        if value[0] * curr_dir < 0:#change sign
            self.entity.velocity[0] = self.entity.dir[0]*2
            self.enter_state('Fall_pre', wall_dir = self.dir)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')
        elif abs(value[0]) == 0:#release
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('Fall_pre', wall_dir = self.dir)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('Run_main')

    def enter_state(self, input, **kwarg):#reset friction before exiting this state
        self.entity.movement_manager.remove_modifier('Wall_glide')  
        super().enter_state(input, **kwarg)

class Belt_glide_main(Player_states):#same as wall glide but only jump if wall_glide has been unlocked
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.movement_manager.add_modifier('Wall_glide')  
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        if self.entity.states['Wall_glide']:#can jump if wall glide has been unlocked
            self.entity.flags['ground'] = True

    def update(self):#is needed
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('Fall_pre')
            if self.entity.states['Wall_glide']:
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.entity.states['Wall_glide']:
                self.entity.velocity[0] = -self.dir[0]*10
                self.entity.velocity[1] = -7#to get a vertical velocity
                self.enter_state('Jump_main')
            else:
                self.entity.velocity[0] = -self.entity.dir[0]*10
                self.enter_state('Fall_pre')
        elif event[-1] == 'lb':
            if self.entity.states['Wall_glide']:
                self.entity.dir[0] *= -1
                input.processed()
                self.enter_state('Ground_dash_pre')

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        curr_dir = self.entity.dir[0]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

        if value[0] * curr_dir < 0:#change sign
            self.entity.velocity[0] = self.entity.dir[0]*2
            self.enter_state('Fall_pre')
            if self.entity.states['Wall_glide']:
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')
        elif value[0] == 0:#release
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('Fall_pre')
            if self.entity.states['Wall_glide']:
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('Run_main')

    def enter_state(self,input):#reset friction before exiting this state
        self.entity.movement_manager.remove_modifier('Wall_glide')  
        super().enter_state(input)

class Air_dash_pre(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()
        self.dash_length = C.dash_length
        self.entity.shader_state.handle_input('motion_blur')        

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        pass

    def update(self):
        self.entity.velocity[1] = 0
        self.entity.velocity[0] = self.dir[0]*max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:            
            self.increase_phase()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            self.entity.shader_state.handle_input('idle')
            if self.entity.acceleration[0] != 0:
                state = input.capitalize() + '_glide_main'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('Idle_main')            
        elif input == 'interrupt':
            self.entity.shader_state.handle_input('idle')
            self.enter_state('Idle_main')

    def increase_phase(self):
        self.enter_state('Air_dash_main')

class Air_dash_main(Air_dash_pre):#level one dash: normal
    def __init__(self, entity):
        super().__init__(entity)
        self.entity.velocity[0] = C.dash_vel*self.dir[0]
        self.entity.consume_spirit(1)        
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])

    def exit_state(self):
        if self.dash_length < 0:
            self.enter_state('Air_dash_post')

    def increase_phase(self):
        pass#self.enter_state('Air_dash_post')

class Air_dash_post(Air_dash_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        pass

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Ground_dash_pre(Air_dash_pre):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.time = C.jump_dash_timer
        wall_dir = kwarg.get('wall_dir', False)
        if wall_dir:
            self.entity.dir[0] = -wall_dir[0]
            self.dir[0] = -wall_dir[0]

    def update(self):
        super().update()        
        self.time -= self.entity.game_objects.game.dt    

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.time >0: self.enter_state('Dash_jump_main')

    #def handle_input(self, input, **kwarg):
    #    print(input)
    #    if input == 'jump':
    #        if self.time >0:
    #            self.enter_state('Dash_jump_main')
    #    elif input == 'interrupt':
    #        self.enter_state('Idle_main')

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def increase_phase(self):
        self.enter_state('Ground_dash_main')

class Ground_dash_main(Air_dash_pre):#level one dash: normal
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[0] = C.dash_vel*self.dir[0]
        self.entity.consume_spirit(1)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.game_objects.cosmetics.add(entities.Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.dir, state = 'one'))#dust

    def increase_phase(self):
        self.enter_state('Ground_dash_post')

class Ground_dash_post(Air_dash_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        pass

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Dash_jump_main(Air_dash_pre):#enters from ground dash pre
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[0] = C.dash_vel*self.dir[0]
        self.entity.consume_spirit(1)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.movement_manager.add_modifier('Dash_jump', entity = self.entity)  
        self.entity.flags['ground'] = False
        self.entity.velocity[1] = C.dash_jump_vel_player
        self.buffer_time = C.jump_dash_wall_timer

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay states
        pass

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input =='belt':
            if self.entity.collision_types['right'] and self.entity.dir[0] > 0 or self.entity.collision_types['left'] and self.entity.dir[0] < 0:
                if self.entity.acceleration[0] != 0:
                    if self.buffer_time < 0:
                        self.entity.shader_state.handle_input('idle')
                        state = input.capitalize() + '_glide_main'
                        self.enter_state(state, **kwarg)
        elif input == 'interrupt':
            self.enter_state('Idle_main')

    def update(self):
        self.entity.velocity[0] = self.entity.dir[0]*max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.buffer_time -= self.entity.game_objects.game.dt
        self.exit_state()

    def increase_phase(self):
        self.enter_state('Dash_jump_post')

class Dash_jump_post(Air_dash_pre):#level one dash: normal
    def __init__(self,entity):
        super().__init__(entity)
        self.buffer_time = C.jump_dash_wall_timer

    def update(self):
        self.entity.velocity[0] = self.entity.dir[0] * max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.buffer_time -= self.entity.game_objects.game.dt
        self.exit_state()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            if self.entity.collision_types['right'] and self.entity.dir[0] > 0 or self.entity.collision_types['left'] and self.entity.dir[0] < 0:
                if self.entity.acceleration[0] != 0:
                    if self.buffer_time < 0:
                        state = input.capitalize() + '_glide_main'
                        self.entity.shader_state.handle_input('idle')
                        self.enter_state(state, **kwarg)
        elif input == 'interrupt':
            self.entity.shader_state.handle_input('idle')
            self.enter_state('Idle_main')

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')
        #self.entity.friction = C.friction_player.copy()
        if self.entity.collision_types['bottom']:
            if self.entity.acceleration[0] == 0:
                self.enter_state('Idle_main')
            else:
                self.enter_state('Run_main')
        else:
            self.enter_state('Fall_pre')

class Death_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.cosmetics.add(entities.Player_Soul([self.entity.rect[0],self.entity.rect[1]],self.entity.game_objects))
        self.entity.velocity[1] = -3
        self.entity.acceleration[0] = 0#don't move
        if self.entity.velocity[0]<0:
            self.dir[0]=1
        else:
            self.dir[0]=-1

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        if self.entity.collision_types['bottom']:#if on the ground when dying
            self.enter_state('Death_main')
        else:
            self.enter_state('Death_charge')

class Death_charge(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.time = 100

    def update(self):
        self.time -= self.entity.game_objects.game.dt
        self.entity.invincibile = True
        if self.time < 0:
            self.entity.dead()
            self.enter_state('Death_post')

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input == 'Ground':#if hit ground
            self.enter_state('Death_main')

class Death_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.entity.dead()
        self.enter_state('Death_post')

class Death_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        pass

class Invisible_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

class Stand_up_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Pray_pre(Player_states):
    def __init__(self, entity):
        super().__init__(entity)
        effect = entities.Pray_effect(self.entity.rect.center,self.entity.game_objects)
        effect.rect.bottom = self.entity.rect.bottom
        self.entity.game_objects.cosmetics.add(effect)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['pray'][0])
        self.entity.acceleration[0] = 0

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Pray_main')

class Pray_main(Player_states):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input == 'Pray_post':
            self.enter_state('Pray_post')

class Pray_post(Player_states):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Hurt_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        if entity.collision_types['bottom']:
            self.next_state = 'Idle_main'            
        else:
            self.next_state = 'Fall_pre'

    def increase_phase(self):
        self.enter_state(self.next_state)

    def update(self):
        if entity.collision_types['bottom']:
            if self.entity.acceleration[0] == 0:
                self.next_state = 'Idle_main'
            else:
                self.next_state ='Run_pre'          
        else:
            self.next_state = 'Fall_pre'

class Spawn_main(Player_states):#enters when aila respawn after death
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.invincibile = False

    def handle_movement(self,event):
        pass

    def increase_phase(self):#when animation finishes
        self.entity.health = max(self.entity.health,0)#if negative, set it to 0
        self.entity.heal(self.entity.max_health)
        if self.entity.backpack.map.spawn_point.get('bone', False):#if bone, remove it        
            self.entity.backpack.map.spawn_point.pop()

        self.enter_state('Idle_main')

class Sword(Player_states):#main phases shold inheret this
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['sword'][0], vol = 0.7)
        self.entity.sword.stone_states['slash'].slash_speed()

    def enter_state(self, input, **kwarg):
        self.entity.animation.framerate = C.animation_framerate
        super().enter_state(input, **kwarg)

class Sword_stand1_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Sword_stand2_main(Sword_stand1_main):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_2')

class Sword_fall_main(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_' + str(int(self.entity.sword.swing)+1))#slash 1 and 2
        self.entity.state = 'fall_main'#animation name
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def increase_phase(self):
        self.enter_state('Fall_main')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('Run_main')
            else:
                self.enter_state('Idle_main')

class Sword_jump1_main(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.state = 'jump_main'
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def update(self):
        if self.entity.velocity[1] > 0.7:#when you start falling
            self.enter_state('Fall_pre')

    def increase_phase(self):
        if self.entity.flags['ground']:
            if self.entity.acceleration[0] == 0:
                self.enter_state('Idle_main')
            else:
                self.enter_state('Run_main')
        self.enter_state('Fall_pre')

class Sword_jump2_main(Sword_jump1_main):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.entity.sword.currentstate.enter_state('Slash_2')

class Air_sword1_main(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def increase_phase(self):
        self.enter_state('Fall_main')

class Air_sword2_main(Air_sword1_main):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_2')

class Sword_up_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_up')
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def increase_phase(self):
        if self.entity.flags['ground']:
            if self.entity.acceleration[0] == 0:
                self.enter_state('Idle_main')
            else:
                self.enter_state('Run_main')
        else:
            self.enter_state('Fall_pre')

class Sword_down_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_down')
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def increase_phase(self):
        self.enter_state('Fall_pre')

class Plant_bone_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Thunder_pre(Player_states):
    def __init__(self, entity):
        super().__init__(entity)
        self.duration = 100
        if self.entity.abilities.spirit_abilities['Thunder'].level == 2:
            self.arrow = entities.Arrow_UI(self.entity.rect.topleft, self.entity.game_objects)
            self.entity.game_objects.cosmetics.add(self.arrow)

    def update(self):
        self.duration -= self.entity.game_objects.game.dt
        self.entity.velocity = [0, 0]

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        if self.entity.abilities.spirit_abilities['Thunder'].level == 1:
            self.enter_state('Thunder_main', dir = [0,1])
        else:
            self.arrow.kill()
            self.enter_state('Thunder_main', dir = [self.arrow.dir[0],-self.arrow.dir[1]])

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='b':
            input.processed()
            self.exit_state()

    def handle_movement(self, event):
        if self.entity.abilities.spirit_abilities['Thunder'].level == 2:
            value = event['l_stick']#the avlue of the press
            if value[0] != 0 or value[1] != 0:
                self.arrow.dir = [value[0],-value[1]]

class Thunder_main(Player_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.dir = kwarg.get('dir', [0, 1])
        self.time = 30
        self.entity.flags['invincibility'] = True

    def update(self):
        self.entity.velocity = [8*self.dir[0], 8*self.dir[1]]
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.enter_state('Thunder_post')

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input in ['Ground', 'Wall', 'belt']:
            self.entity.game_objects.camera_manager.camera_shake()
            self.enter_state('Thunder_post')

class Thunder_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity = [0,0]

    def handle_movement(self,event):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        self.entity.flags['invincibility'] = False
        self.enter_state('Idle_main')

class Shield_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Shield'].initiate()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Wind_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Wind'].initiate()

    def increase_phase(self):
        self.enter_state('Idle_main')

class Slow_motion_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Slow_motion_main')

class Slow_motion_main(Slow_motion_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.abilities.spirit_abilities['Slow_motion'].initiate()

    def increase_phase(self):
        self.enter_state('Idle_main')

class Bow_pre(Player_states):
    def __init__(self, entity):
        super().__init__(entity)
        self.duration = 100#charge times
        self.arrow = entities.Arrow_UI(self.entity.rect.topleft, self.entity.game_objects, dir = self.entity.dir.copy())
        self.entity.game_objects.cosmetics.add(self.arrow)
        self.time = 0    

    def update(self):
        self.duration -= self.entity.game_objects.game.dt
        self.time += self.entity.game_objects.game.dt
        self.entity.velocity = [0, 0]        

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.arrow.kill()
        self.enter_state('Bow_main', dir = [self.arrow.dir[0], -self.arrow.dir[1]], time = self.time)

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='b':
            input.processed()
            self.exit_state()

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        if value[0] != 0 or value[1] != 0:
            self.arrow.dir = [value[0],-value[1]]

class Bow_main(Player_states):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.consume_spirit()        
        self.entity.abilities.spirit_abilities['Bow'].initiate(dir = kwarg['dir'], time = kwarg['time'])

    def increase_phase(self):
        self.enter_state('Idle_main')
