import sound, entities, sys, random, math
from states_entity import Entity_States
import constants as C

def sign(number):
    if number > 0: return 1
    else: return -1

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate, **kwarg):
        state = newstate[:newstate.rfind('_')]#get the name up to last _ (remove pre, main, post)
        if self.entity.states[state]:
            self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys
            return True

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        pass

    def handle_release_input(self,input):#all states should inehrent this function, if it should be able to jump
        pass

    def handle_movement(self,input):#all states should inehrent this function
        #left stick and arrow keys 
        value = input[2]['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        if abs(value[0]) > 0.2:
            self.entity.dir[0] = sign(value[0])

    def do_ability(self):#called when pressing B (E). This is needed if all of them do not have pre animation, or vice versa
        if self.entity.abilities.equip == 'Thunder' or self.entity.abilities.equip == 'Slow_motion' or self.entity.abilities.equip == 'Migawari':
            self.enter_state(self.entity.abilities.equip + '_pre')
        else:
            self.enter_state(self.entity.abilities.equip + '_main')

class Idle_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()

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

    def handle_input(self,input):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')            

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Run_pre')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return 
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

    def update(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            self.running_particles()
            #self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'])

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()

    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
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

    def handle_input(self,input):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')                 

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return
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

    def update(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            self.running_particles()
            #self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'])

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()

    def increase_phase(self):
        self.enter_state('Run_main')

    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom, self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
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

    def handle_input(self,input):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')                  

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Run_post')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return
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
            self.entity.timer_jobs['ground'].activate()

    def enter_state(self, new_state):
        #self.sfx_channel.stop()
        super().enter_state(new_state)

    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
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

    def handle_input(self,input):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')                   

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Run_post')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return        
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
            self.entity.timer_jobs['ground'].activate()

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

    def handle_input(self,input):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')              

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Run_pre')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return
        if self.entity.dir[1]==0:
            state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

        elif self.entity.dir[1]>0:
            self.enter_state('Sword_up_main')

    def increase_phase(self):
        self.enter_state('Idle_main')

class Jump_main(Player_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.velocity[1] = C.jump_vel_player
        self.air_timer = C.air_timer 
        self.entity.flags['ground'] = False

    def update(self):
        self.jump_dash_timer -= self.entity.game_objects.game.dt
        self.air_timer -= self.entity.game_objects.game.dt
        if self.air_timer > 0:
            self.entity.velocity[1] = C.jump_vel_player
        if self.entity.velocity[1] > 0.7:
            self.enter_state('Fall_pre')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1]=='lb':
            input.processed()
            if self.jump_dash_timer > 0: self.enter_state('Dash_jump_main')
            else: self.enter_state('Air_dash_pre')               
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':
            input.processed()
            self.do_ability()

    def handle_release_input(self,input):#when release space
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.entity.velocity[1] = 0.5*self.entity.velocity[1]
            self.enter_state('Fall_pre')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return
        if self.entity.dir[1]>0:
            self.enter_state('Sword_up_main')
        elif self.entity.dir[1]<0:
            self.enter_state('Sword_down_main')
        else:#right or left
            state='Sword_jump'+str(int(self.entity.sword.swing)+1)+'_main'
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Double_jump_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()

    def init(self):
        self.entity.velocity[1] = C.jump_vel_player

    def update(self):
        if self.entity.velocity[1] > 0:#falling down            
            self.enter_state('Fall_pre')

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Double_jump_main')

class Double_jump_main(Double_jump_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def init(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Fall_pre(Player_states):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('Jump_main')        
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='lb':
            if self.enter_state('Air_dash_pre'):
                input.processed()
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()     

    def handle_input(self,input):
        if input == 'jump':#caööed from jump buffer timer
            self.enter_state('Jump_main')
        elif input == 'Wall':
            self.enter_state('Wall_glide_main')
        elif input == 'dash':#called from dash buffer timer
            self.enter_state('Ground_dash_pre')
        elif input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('Run_main')
            else:
                self.enter_state('Idle_main')

    def swing_sword(self):
        if self.entity.flags['sword_swinging']: return
        if self.entity.dir[1]>0:
            self.enter_state('Sword_up_main')
        elif self.entity.dir[1]<0:
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

class Wall_glide_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.friction[1] = 0.4
        self.entity.flags['ground'] = True#so that we can jump

    def update(self):
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            self.entity.velocity[0] = -self.dir[0]*10
            self.entity.velocity[1] = -7#to get a vertical velocity
            input.processed()            
            self.enter_state('Jump_main')
        elif event[-1] == 'right':
            self.entity.velocity[0] = self.entity.dir[0]*2            
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()
            input.processed()
        elif event[-1] == 'left':
            self.entity.velocity[0] = self.entity.dir[0]*2            
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()            
            input.processed()

    def handle_release_input(self,input):
        event = input.output()
        if event[-1] == 'right':
            input.processed()
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('Fall_pre')  
            self.entity.timer_jobs['ground'].activate()          
        elif event[-1] == 'left':
            input.processed()
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('Fall_pre')
            self.entity.timer_jobs['ground'].activate()

    def handle_input(self,input):#when hit the ground
        if input == 'Ground':
            self.enter_state('Run_main')

    def enter_state(self,input):#reset friction before exiting this state
        self.entity.friction[1] = C.friction_player[1]
        super().enter_state(input)

class Air_dash_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()
        self.dash_length = C.dash_length

    def update(self):
        self.entity.velocity[1] = 0
        self.entity.velocity[0] = self.dir[0]*max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def handle_input(self,input):#if hit wall
        if input == 'Wall':
            if self.entity.acceleration[0]!=0:
                self.enter_state('Wall_glide_main')
            else:
                self.enter_state('Idle_main')
        elif input == 'interrupt':
            self.enter_state('Idle_main')

    def increase_phase(self):
        self.enter_state('Air_dash_main')

class Air_dash_main(Air_dash_pre):#level one dash: normal
    def __init__(self,entity):
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
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Ground_dash_pre(Air_dash_pre):
    def __init__(self,entity):
        super().__init__(entity)   
        self.time = C.jump_dash_timer

    def update(self):
        super().update()
        self.time -= self.entity.game_objects.game.dt 

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            input.processed()            
            self.enter_state('Dash_jump_main')

    def handle_input(self,input):#if hit wall
        super().handle_input(input)
        if input == 'jump':
            if self.time >0:
                self.enter_state('Dash_jump_main')

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

    def increase_phase(self):
        self.enter_state('Ground_dash_post')

class Ground_dash_post(Air_dash_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        pass

    def increase_phase(self):
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
        self.entity.friction = [0.15,0.01]
        self.entity.flags['ground'] = False
        self.entity.velocity[1] = C.jump_vel_player

    def update(self):
        self.entity.velocity[0] = self.dir[0]*max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.exit_state()

    def increase_phase(self):
        self.enter_state('Dash_jump_post')

class Dash_jump_post(Air_dash_pre):#level one dash: normal
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.velocity[0] = self.dir[0]*max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.exit_state()

    def increase_phase(self):
        self.entity.friction = C.friction_player.copy()   
        if self.entity.flags['ground']:
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

    def handle_movement(self,input):
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

    def handle_movement(self,input):
        pass

    def handle_input(self,input):
        if input == 'Ground':#if hit ground
            self.enter_state('Death_main')

class Death_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.entity.dead()
        self.enter_state('Death_post')

class Death_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        pass

class Invisible_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,input):
        pass

class Stand_up_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Pray_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.special = False#a flag to chekc when the animation should finish (after interaction with e.g. rune stone, or when ability upgrade screen is exited)
        effect = entities.Pray_effect(self.entity.rect.center,self.entity.game_objects)
        effect.rect.bottom = self.entity.rect.bottom
        self.entity.game_objects.cosmetics.add(effect)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['pray'][0])
        self.entity.acceleration[0] = 0

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.enter_state('Pray_main')
        self.entity.currentstate.special = self.special#set the Pray_main flag

    def handle_input(self,input):
        if input == 'special':
            self.special = True

class Pray_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.special = False

    def handle_movement(self,input):
        pass

    def handle_input(self,input):#called from either when the ability scnreen is exited (special), or when the saving point/runestone animation is finshed
        if input == 'Pray_post':
            if not self.special:
                self.enter_state('Pray_post')
        elif input == 'Pray_spe_post':
                self.enter_state('Pray_post')
        elif input == 'special':
            self.special = True

class Pray_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Hurt_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.next_state = 'Idle_main'

    def increase_phase(self):
        self.enter_state(self.next_state)

    def update(self):
        if self.entity.acceleration[0] == 0:
            self.next_state = 'Idle_main'
        else:
            self.next_state ='Run_main'

class Spawn_main(Player_states):#enters when aila respawn after death
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.invincibile = False

    def handle_movement(self,input):
        pass

    def increase_phase(self):#when animation finishes
        self.entity.health = max(self.entity.health,0)#if negative, set it to 0
        self.entity.heal(self.entity.max_health)
        if len(self.entity.spawn_point) == 2:#if the respawn was a bone
            self.entity.spawn_point.pop()

        self.enter_state('Idle_main')

class Sword(Player_states):#main phases shold inheret this
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.timer_jobs['sword'].activate()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['sword'][0], vol = 0.7)
        self.slash()

    def slash(self):#if we have green infinity stone
        for stone in self.entity.sword.equip:
            self.entity.sword.stones[stone].slash()#call collision specific for stone

    def enter_state(self, input, **kwarg):
        self.entity.animation.framerate = C.animation_framerate
        super().enter_state(input, **kwarg)

class Sword_stand1_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.sword.dir[1] = 0
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
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.sword.currentstate.enter_state('Slash_' + str(int(self.entity.sword.swing)+1))#slash 1 and 2
        self.entity.state = 'fall_main'#animation name
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def increase_phase(self):
        self.enter_state('Fall_main')

    def handle_input(self,input):
        if input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('Run_main')
            else:
                self.enter_state('Idle_main')

class Sword_jump1_main(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.state = 'jump_main'
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def update(self):
        if self.entity.velocity[1] > 0.7:#when you start falling
            self.enter_state('Fall_pre')

    def increase_phase(self):
        if self.entity.flags['ground']:
            self.enter_state('Jump_main', frame = self.entity.animation.frame)
        else:
            self.enter_state('Fall_pre')

class Sword_jump2_main(Sword_jump1_main):
    def __init__(self,entity, **kwarg):
        super().__init__(entity, **kwarg)
        self.entity.sword.currentstate.enter_state('Slash_2')

class Air_sword1_main(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
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
        self.entity.sword.lifetime = 10#swrod hitbox duration
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
        self.entity.sword.lifetime = 10
        self.entity.sword.currentstate.enter_state('Slash_down')
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def increase_phase(self):
        self.enter_state('Fall_pre')        

class Plant_bone_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Abillitites(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()#animation direction

class Thunder_pre(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.acceleration[0] = 0
        self.init()

    def init(self):
        self.entity.thunder_aura = entities.Thunder_aura(self.entity.rect.center,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(self.entity.thunder_aura)

    def handle_movement(self,input):
        pass

    def handle_release_input(self,input):
        event = input.output()
        if event[-1]=='b':#when release the botton
            self.entity.thunder_aura.currentstate.handle_input('Death')
            input.processed()
            self.enter_state('Idle_main')

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Thunder_charge')

class Thunder_charge(Thunder_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['thunder'][0])

    def init(self):
        self.entity.consume_spirit()

    def handle_release_input(self,input):
        event = input.output()
        if event[-1]=='b':#when release the botton
            input.processed()
            self.attack()
            self.enter_state('Thunder_main')

    def attack(self):
        self.entity.thunder_aura.currentstate.enter_state('Death')

        collision_ene = self.entity.game_objects.collisions.thunder_attack(self.entity.thunder_aura)
        for enemy in collision_ene:
            self.entity.abilities.spirit_abilities['Thunder'].initiate(enemy.rect)

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Thunder_main(Thunder_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def init(self):
        pass

    def update(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Idle_main')

class Shield_main(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Shield'].initiate()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Migawari_pre(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_release_input(self,input):
        event = input.output()
        if event[-1]=='b':#when release the botton
            self.enter_state('Idle_main')
            input.processed()

    def increase_phase(self):
        self.enter_state('Migawari_main')

class Migawari_main(Migawari_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.abilities.spirit_abilities['Migawari'].initiate()

    def increase_phase(self):
        self.entity.consume_spirit()
        self.enter_state('Idle_main')

class Slow_motion_pre(Abillitites):
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

class Bow_main(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Bow'].initiate()

    def increase_phase(self):
        self.enter_state('Idle_main')
