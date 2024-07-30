import sound, Entities, sys, random
from states_entity import Entity_States
import constants as C

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate, **kwarg):
        state = newstate[:newstate.rfind('_')]#get the name up to last _ (remove pre, main, post)
        if self.entity.states[state]:
             self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        if input[-1] == 'a':
            self.entity.timer_jobs['shroomjump'].activate()
            self.entity.timer_jobs['jump'].activate()
            self.entity.timer_jobs['wall'].handle_input('a')

    def handle_release_input(self,input):#all states should inehrent this function, if it should be able to jump
        if input[-1] == 'a':
            self.entity.timer_jobs['air'].deactivate()
            self.entity.timer_jobs['jump'].deactivate()
            if self.entity.velocity[1] < 0:#if going up
                self.entity.velocity[1] = 0.5*self.entity.velocity[1]

    def handle_movement(self,input):#all states should inehrent this function
        #left stick and arrow keys
        value = input[2]['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0]*abs(value[0])#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        if value[0] > 0.2:#x, even if value goes to 0, the direction is maintained
            self.entity.dir[0] = 1
        elif value[0] < -0.2:#x
            self.entity.dir[0] = -1

    def do_ability(self):#called when pressing B (E). This is needed if all of them do not have pre animation, or vice versa
        if self.entity.abilities.equip=='Thunder' or self.entity.abilities.equip=='Slow_motion' or self.entity.abilities.equip=='Migawari':
            self.enter_state(self.entity.abilities.equip + '_pre')
        else:
            self.enter_state(self.entity.abilities.equip + '_main')

class Idle_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_pre')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_stand_main')
        elif input[-1]=='lb':
            self.enter_state('Ground_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation
            self.do_ability()
        elif input[-1] == 'rt':
            self.enter_state('Counter_pre')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Run_pre')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1] == 0:
                state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword.swing = not self.entity.sword.swing

            elif self.entity.dir[1]>0:
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
            self.enter_state('Fall_run_pre')

    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_run_main')
        elif input[-1]=='lb':
            self.enter_state('Ground_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation. Should all have pre?
            self.do_ability()

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
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
            self.enter_state('Fall_run_pre')

    def increase_phase(self):
        self.enter_state('Run_main')

    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom, self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_run_main')
        elif input[-1]=='lb':
            self.enter_state('Ground_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation
            self.do_ability()

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Run_post')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if abs(self.entity.dir[1])<0.8:
                state='Sword_run'+str(int(self.entity.sword.swing)+1)+'_main'
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
            self.running_particles()

        self.sfx_timer -= 1
        if self.sfx_timer == 0:
            self.entity.game_objects.sound.play_sfx(self.entity.sounds['run'][self.sfx_timer%2], vol = 0.8)
            self.sfx_timer = self.sfx_loop_time

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('Fall_run_pre')

    def enter_state(self, new_state):
        #self.sfx_channel.stop()
        super().enter_state(new_state)


    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_run_main')
        elif input[-1]=='lb':
            self.enter_state('Ground_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation
            self.do_ability()

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Run_post')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if abs(self.entity.dir[1])<0.8:
                state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword.swing = not self.entity.sword.swing
            elif self.entity.dir[1]>0.8:
                self.enter_state('Sword_up_main')

class Run_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_pre')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_stand_main')
        elif input[-1]=='lb':
            self.enter_state('Ground_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation
            self.do_ability()
        elif input[-1] == 'rt':
            self.enter_state('Counter_pre')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Run_pre')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]==0:
                state='Sword_stand'+str(int(self.entity.sword.swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword.swing = not self.entity.sword.swing

            elif self.entity.dir[1]>0:
                self.enter_state('Sword_up_main')

    def increase_phase(self):
        self.enter_state('Idle_main')

class Jump_stand_main(Player_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.frame = kwarg.get('frame', 0)

    def update(self):
        if self.entity.velocity[1] > 0.7:#when you start falling
            self.enter_state('Fall_stand_pre')
        elif self.entity.acceleration[0] != 0:#if you start moving
            self.enter_state('Jump_run_main')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='lb':
            self.enter_state('Air_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.do_ability()

    def handle_release_input(self,input):#when release space
        super().handle_release_input(input)
        if input[-1]=='a':
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand_pre')

    def swing_sword(self):
        if not self.entity.sword_swinging:
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

class Jump_run_main(Player_states):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.animation.frame = kwarg.get('frame', 0)

    def update(self):
        if self.entity.velocity[1] > 0.7:
            self.enter_state('Fall_run_pre')
        elif self.entity.acceleration[0] == 0:
            self.enter_state('Jump_stand_main')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='lb':
            self.enter_state('Air_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.do_ability()

    def handle_release_input(self,input):#when release space
        super().handle_release_input(input)
        if input[-1]=='a':
            if self.entity.acceleration[0]!=0:
                self.enter_state('Fall_run_pre')

    def swing_sword(self):
        if not self.entity.sword_swinging:
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
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand_pre')
            else:
                self.enter_state('Fall_run_pre')

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Double_jump_main')

class Double_jump_main(Double_jump_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def init(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Fall_run_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()

    def init(self):
        self.entity.timer_jobs['ground'].activate()
        #self.entity.velocity[1] = 1#so that the falling from platform looks natural, 0 looks strange

    def update(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Fall_stand_pre')#TODO, it should start at a specific animation frame, depending on the current one

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='b':
            self.do_ability()
        elif input[-1]=='lb':
            self.enter_state('Air_dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='a':
            self.enter_state('Double_jump_pre')

    def handle_input(self,input):
        if input == 'Wall':
            self.enter_state('Wall_glide_main')
        elif input == 'Ground':
            self.enter_state('Run_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]>0:
                self.enter_state('Sword_up_main')
            elif self.entity.dir[1]<0:
                self.enter_state('Sword_down_main')
            else:#right or left
                self.enter_state('Sword_fall_main', frame = self.entity.animation.frame)
                self.entity.sword.swing = not self.entity.sword.swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Fall_run_main')

class Fall_run_main(Fall_run_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Fall_stand_main')

    def init(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Fall_stand_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()

    def init(self):
        self.entity.timer_jobs['ground'].activate()
        #self.entity.velocity[1] = 1#so that the falling from platform looks natural, 0 looks strange

    def update(self):
        if self.entity.acceleration[0] != 0:
            self.enter_state('Fall_run_pre')#TODO, it should start at a specific animation frame, depending on the current one

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='b':
            self.do_ability()
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='lb':
            self.enter_state('Air_dash_pre')
        elif input[-1]=='a':
            self.enter_state('Double_jump_pre')

    def handle_input(self,input):
        if input == 'Ground':
            self.enter_state('Idle_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]==1:
                self.enter_state('Sword_up_main')
            elif self.entity.dir[1]==-1:
                self.enter_state('Sword_down_main')
            else:#right or left
                self.enter_state('Sword_fall_main', frame = self.entity.animation.frame)
                self.entity.sword.swing = not self.entity.sword.swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Fall_stand_main')

class Fall_stand_main(Fall_stand_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        if self.entity.acceleration[0] != 0:
            self.enter_state('Fall_run_main')

    def init(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Wall_glide_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.friction[1] = 0.4
        self.entity.ground = True#so that we can jump

    def update(self):
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.timer_jobs['wall'].activate()
            self.enter_state('Fall_stand_pre')

    def handle_press_input(self,input):
        #super().handle_press_input(input)
        if input[-1] == 'a':
            self.entity.velocity[0] = -self.dir[0]*10
            self.entity.velocity[1] = -7#to get a vertical velocity
            self.entity.timer_jobs['wall_2'].activate(self.dir)
            self.enter_state('Jump_run_main')
        elif input[-1] == 'right' or input[-1] == 'left':
            self.entity.velocity[0] = self.entity.dir[0]*2
            self.entity.timer_jobs['wall'].activate()
            self.enter_state('Fall_run_pre')

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1] == 'right' or input[-1] == 'left':
            self.entity.timer_jobs['wall'].activate()
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('Fall_stand_pre')

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
        self.entity.velocity[0] = self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(Entities.Dash_effect(self.entity,100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.exit()

    def exit(self):
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

    def exit(self):
        if self.dash_length < 0:
            self.increase_phase()

    def increase_phase(self):
        self.enter_state('Air_dash_post')

class Air_dash_post(Air_dash_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        pass

    def handle_press_input(self,input):
        pass

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Ground_dash_pre(Air_dash_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def exit(self):
        if self.dash_length < 0:
            self.increase_phase()

    def increase_phase(self):
        self.enter_state('Ground_dash_main')

class Ground_dash_main(Air_dash_main):#level one dash: normal
    def __init__(self,entity):
        super().__init__(entity)

    def exit(self):
        if self.dash_length < 0:
            self.increase_phase()

    def increase_phase(self):
        self.enter_state('Ground_dash_post')

class Ground_dash_post(Air_dash_post):
    def __init__(self,entity):
        super().__init__(entity)

class Dash_attack_main(Player_states):#enters from pre dash
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()

        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.sword.dir[1] = 0
        self.entity.sword.dir = self.dir.copy()#sword direction
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def update(self):
        self.entity.velocity[1]=0
        self.entity.velocity[0]=self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

    def increase_phase(self):
        self.enter_state('Dash_attack_post')

class Dash_attack_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        if self.entity.acceleration[0]!=0:
            self.enter_state('Wall_glide_main')
        else:
            self.enter_state('Idle_main')

class Counter_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()

    def increase_phase(self):
        self.enter_state('Counter_main')

class Counter_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()
        self.entity.consume_spirit()
        shield=Entities.Shield(self.entity)
        self.entity.projectiles.add(shield)#add sword to group

    def increase_phase(self):
        self.enter_state('Idle_main')

class Death_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.cosmetics.add(Entities.Player_Soul([self.entity.rect[0],self.entity.rect[1]],self.entity.game_objects))
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

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
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

    def handle_press_input(self,input):#all states should inehrent this function
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

    def handle_press_input(self,input):#all states should inehrent this function
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

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def increase_phase(self):
        pass

class Invisible_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def handle_movement(self,input):
        pass

class Stand_up_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Pray_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.special = False#a flag to chekc when the animation should finish (after interaction with e.g. rune stone, or when ability upgrade screen is exited)
        effect = Entities.Pray_effect(self.entity.rect.center,self.entity.game_objects)
        effect.rect.bottom = self.entity.rect.bottom
        self.entity.game_objects.cosmetics.add(effect)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['pray'][0])
        self.entity.acceleration[0] = 0

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

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

    def handle_press_input(self,input):
        pass

    def handle_release_input(self,input):
        pass

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

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

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

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

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
        self.dir = self.entity.dir.copy()#animation direction
        self.entity.sword.dir = self.dir.copy()#sword direction
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['sword'][0], vol = 1)
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

class Sword_run1_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.currentstate.enter_state('Slash_1')

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Sword_run2_main(Sword_run1_main):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_2')

class Sword_fall_main(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.sword.currentstate.enter_state('Slash_' + str(int(self.entity.sword.swing)+1))#slash 1 and 2
        self.entity.state = 'fall_stand_main'#animation name
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def increase_phase(self):
        if self.entity.acceleration[0]==0:
            self.enter_state('Fall_stand_main')
        else:
            self.enter_state('Fall_run_main')

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
        self.entity.state = 'jump_stand_main'
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def update(self):
        if self.entity.velocity[1] > 0.7:#when you start falling
            self.enter_state('Fall_stand_pre')

    def increase_phase(self):
        if self.entity.acceleration[0]==0:
            self.enter_state('Jump_stand_main', frame = self.entity.animation.frame)
        else:
            self.enter_state('Jump_run_main', frame = self.entity.animation.frame)

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
        if self.entity.acceleration[0]==0:
            self.enter_state('Fall_stand_main')
        else:
            self.enter_state('Fall_run_main')

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
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Sword_down_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime = 10
        self.entity.sword.currentstate.enter_state('Slash_down')
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def increase_phase(self):
        if self.entity.acceleration[0]==0:
            self.enter_state('Fall_stand_pre')
        else:
            self.enter_state('Fall_run_pre')

class Plant_bone_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,input):
        pass

    def handle_press_input(self,input):
        pass

    def handle_release_input(self,input):
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
        self.entity.thunder_aura = Entities.Thunder_aura(self.entity.rect.center,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(self.entity.thunder_aura)

    def handle_movement(self,input):
        pass

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1]=='b':#when release the botton
            self.entity.thunder_aura.currentstate.handle_input('Death')
            self.enter_state('Idle_main')

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Thunder_charge')

class Thunder_charge(Thunder_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['thunder'])

    def init(self):
        self.entity.consume_spirit()

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1]=='b':#when release the botton
            self.attack()
            self.enter_state('Thunder_main')

    def attack(self):
        self.entity.thunder_aura.currentstate.enter_state('Death')

        collision_ene = self.entity.game_objects.collisions.thunder_attack(self.entity.thunder_aura)
        for enemy in collision_ene:
            self.entity.abilities.spirit_abilities['Thunder'].initiate(enemy.rect)
            self.entity.projectiles.add(self.entity.abilities.spirit_abilities['Thunder'])#add attack to group

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

class Force_main(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Force'].initiate()
        self.entity.projectiles.add(self.entity.abilities.spirit_abilities['Force'])#add force to group
        self.force_jump()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

    def force_jump(self):
        if self.dir[1]<0:
            self.entity.velocity[1] = -10

class Migawari_pre(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1]=='b':#when release the botton
            self.enter_state('Idle_main')

    def increase_phase(self):
        self.enter_state('Migawari_main')

class Migawari_main(Migawari_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.abilities.spirit_abilities['Migawari'].spawn(self.entity.rect.center)

    def handle_release_input(self,input):
        pass

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
        self.entity.abilities.spirit_abilities['Slow_motion'].spawn()

    def increase_phase(self):
        self.enter_state('Idle_main')

class Arrow_main(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Arrow'].initiate()
        self.entity.projectiles.add(self.entity.abilities.spirit_abilities['Arrow'])#add sword to group

    def increase_phase(self):
        self.enter_state('Idle_main')
