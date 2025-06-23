import entities, random, math
import constants as C

def sign(number):
    if number > 0: return 1
    else: return -1

class PlayerStates():
    def __init__(self, entity):
        self.entity = entity
        self.states = {
            'idle': IdleState(entity),
            'run': RunState(entity),
            'fall': FallState(entity),
            'jump': JumpState(entity),
            'dash_ground': DashGroundState(entity),
            'dash_jump': DashJumpState(entity),
            'wall_glide': WallGlideState(entity),
            'wall_jump': WallJumpState(entity),
            'sword_stand1': SwordStandState(entity),
            'sword_stand2': SwordStandState(entity),    
            'sword_heavy': SwordHeavyState(entity),            
            #'Sword_up': SwordUpState(entity),
        }
        self.composite_state = self.states['idle']
        self.composite_state.enter_phase('main')
        self._state_factories = {}#should contain all the states that can be created, so that they can be be appended to self.stataes when needed

    def enter_state(self, state_name, phase = None, **kwargs):
        state = self.states.get(state_name)  
        print(state_name, phase)
        if state:#if the requested state is unlocked     
            self.composite_state = state
            self.composite_state.enter_state(phase, **kwargs)#choose the phase

    def update(self):#called from player
        #print(self.composite_state.current_phase)
        self.composite_state.update()#main state

    def handle_input(self, *args, **kwargs):
        self.composite_state.handle_input(*args, **kwargs)

    def handle_press_input(self, input):
        self.composite_state.handle_press_input(input)

    def handle_release_input(self, input):
        self.composite_state.handle_release_input(input)

    def handle_movement(self, event):#called from gameplay loop state
        self.composite_state.handle_movement(event)

    def increase_phase(self):#called when an animation is finished for that state
        self.composite_state.increase_phase()

    def unlock_state(self, name):#should be called when unlocking a new state
        self.states[name] = self.state_factories[name](self.entity)

class CompositeState():#will contain pre, main, post phases of a state
    def __init__(self, entity):
        self.entity = entity
        self.phases = {}

    def enter_phase(self, phase_name, **kwarg):#called when entering a new phase
        self.current_phase = self.phases[phase_name]        
        self.current_phase.enter(**kwarg)                

    def enter_state(self, phase_name, **kwarg):#called when entering a new state
        if not phase_name: phase_name = next(iter(self.phases))#get the first phase from the dictionary if not specified            
        self.common_values()               
        self.enter_phase(phase_name, **kwarg) #enter the phase of the state

    def common_values(self):#set common values for the phases
        pass

    def update(self):
        self.current_phase.update()

    def handle_input(self, input, **kwargs):
        self.current_phase.handle_input(input, **kwargs)

    def handle_press_input(self, input):
        self.current_phase.handle_press_input(input)

    def handle_release_input(self, input):
        self.current_phase.handle_release_input(input)

    def handle_movement(self, event):
        self.current_phase.handle_movement(event)

    def change_phase(self, new_phase):
        self.enter_phase(new_phase)

    def increase_phase(self):#called when an animation is finished for that state
        self.current_phase.increase_phase()

class FallState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': FallPre(entity), 'main': FallMain(entity), 'post': FallPost(entity)}

class RunState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': RunPre(entity), 'main': RunMain(entity), 'post': RunPost(entity)}

class IdleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': IdleMain(entity)}

class JumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': JumpMain(entity)}

class DashGroundState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashGroundPre(entity), 'main': DashGroundMain(entity), 'post': DashGroundPost(entity)}

    def common_values(self):#called when entering this new state, and will not change during phase changes
        self.dir = self.entity.dir.copy()#copy the direction of the entity, and save it in the state across phases 

class WallGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': WallGlide(entity, animation_name = 'wall_glide_pre'), 'main': WallGlide(entity, animation_name = 'wall_glide_main')}

class DashJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashJumpPre(entity), 'main': DashJumpMain(entity), 'post': DashJumpPost(entity)}

class WallJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallJumpMain(entity)}#'pre': WallJumpPre(entity), 

class SwordStandState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SwordStandPre(entity), 'main': SwordStandMain(entity), 'post': SwordStandPost(entity)}#'pre': WallJumpPre(entity), 

class SwordHeavyState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SwordHeavyPre(entity), 'main': SwordHeavyMain(entity), 'post': SwordHeavyPost(entity)}#'pre': WallJumpPre(entity), 


class PhaseBase():
    def __init__(self, entity):
        self.entity = entity                

    def update(self):
        pass

    def increase_phase(self):
        pass

    def handle_input(self, input, **kwarg):
        pass

    def enter(self, **kwarg):#called when entering a new phase
        pass

    def enter_state(self, new_state, **kwarg):#should call when entering a new state   
        self.entity.currentstate.enter_state(new_state, **kwarg)

    def enter_phase(self, phase_name):#should call when just changing phase
        self.entity.currentstate.composite_state.enter_phase(phase_name)

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_release_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
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

class IdleMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('idle')#the name of the class          
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times        
        
    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self, input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
        elif event[-1]=='double_x':
            input.processed()
            self.enter_state('sword_heavy')           
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

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] != 0:
            self.enter_state('run')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] == 0:
            state = 'sword_stand' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0:
            self.enter_state('sword_up')

class RunPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('run_pre')
        self.particle_timer = 0
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            self.running_particles()
            #self.entity.game_objects.sound.play_sfx(self.entity.sounds['walk'])

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def increase_phase(self):
        self.enter_phase('main')

    def running_particles(self):
        #particle = self.entity.running_particles(self.entity.hitbox.midbottom, self.entity.game_objects)
        #self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')#main
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
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

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1])<0.8:
            state='sword_stand'+str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1]>0.8:
            self.enter_state('sword_up')

class RunMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        print('runnnnn')
        self.entity.animation.play('run_main')
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
            self.enter_state('fall')#fall pre
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
            self.enter_state('jump')#main
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
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

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1]) < 0.8:
            state='sword_stand'+str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0.8:
            self.enter_state('Sword_up_main')

class RunPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)
        
    def enter(self, **kwarg):
        self.entity.animation.play('run_post')

    def update(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')#pre
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')#main
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] != 0:
            self.entity.currentstate.composite_state.enter_phase('pre')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1]==0:
            state='sword_stand'+str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

        elif self.entity.dir[1]>0:
            self.enter_state('Sword_up_main')

    def increase_phase(self):
        self.enter_state('idle')

class JumpMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_main')#the name of the class
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['jump'][random.randint(0,2)], vol = 0.1)
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.jump_dash_timer = C.jump_dash_timer
        #self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.flags['ground'] = False
        self.wall_dir = kwarg.get('wall_dir', False)
        self.shroomboost = 1#if landing on shroompoline and press jump, this vakue is modified
        self.air_timer = self.entity.colliding_platform.jumped()#jump charactereistics is set from the platform
        self.entity.game_objects.cosmetics.add(entities.Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'two'))#dust

    def update(self):
        self.jump_dash_timer -= self.entity.game_objects.game.dt
        self.air_timer -= self.entity.game_objects.game.dt
        if self.air_timer >= 0:
            self.entity.velocity[1] = C.jump_vel_player * self.shroomboost
        if self.entity.velocity[1] > 0.7:
            self.enter_state('fall')#pre

    def handle_press_input(self,input):
        event = input.output()
        if event[-1]=='lb':
            input.processed()
            if self.jump_dash_timer > 0:
                if self.wall_dir:
                    self.entity.dir[0] = -self.wall_dir[0]#if the jmup came from wall glide, jump away
                self.enter_state('dash_jump')#main
            else:
                self.enter_state('Air_dash_pre')#pre
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
            self.enter_state('fall')#pre

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

class WallJumpPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('wall_jump_pre')   

    def update(self):
        self.entity.velocity[0] = 0
        self.entity.velocity[1] = 0        

    def increase_phase(self):
        self.enter_phase('main')

class WallJumpMain(JumpMain):
    def __init__(self, entity, **kwarg):
        super().__init__(entity, **kwarg)          

    def enter(self, **kwarg):
        super().enter(**kwarg)
        self.entity.animation.play('wall_jump_main')#the name of the class

class FallPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)        

    def enter(self, **kwarg):
        self.entity.animation.play('fall_pre')
        self.wall_dir = kwarg.get('wall_dir', False)

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('jump', wall_dir = self.wall_dir)
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
            self.enter_state('wall_glide', **kwarg)
        elif input == 'belt':
            self.enter_state('Belt_glide_main')
        elif input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('run', phase = 'main')#enter run pre phase
            else:
                self.enter_state('idle')

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
        self.enter_phase('main')

class FallMain(FallPre):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_main')

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class FallPost(FallPre):#landing
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_post')

    def increase_phase(self):#called when an animation is finihed for that state
        pass        

class WallGlide(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):        
        self.entity.animation.play(self.animation_name)#the name of the class
        self.entity.flags['ground'] = True#used for jumping: sets to false in cayote timer and in jump state
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.movement_manager.add_modifier('Wall_glide')
        if self.entity.collision_types['right']:
            self.dir = [1,0]
        else:
            self.dir = [-1,0]

    def update(self):#is needed
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('fall', wall_dir = self.dir)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            #self.entity.dir[0] *= -1#if we want to jump vertically
            self.entity.velocity[0] = -self.dir[0]*10
            self.entity.velocity[1] = -7#to get a vertical velocity
            input.processed()
            self.enter_state('wall_jump', wall_dir = self.dir)
        elif event[-1] == 'lb':
            input.processed()
            self.entity.dir[0] *= -1
            self.enter_state('dash_ground')

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
            self.enter_state('fall', wall_dir = self.dir)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')
        elif abs(value[0]) == 0:#release
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('fall', wall_dir = self.dir)
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_phase('main')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def enter_state(self, input, **kwarg):#reset friction before exiting this state
        self.entity.movement_manager.remove_modifier('Wall_glide')
        super().enter_state(input, **kwarg)       

class Belt_glide_main(PhaseBase):#same as wall glide but only jump if wall_glide has been unlocked
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation.play('wall_glide_main')
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

class DashGroundPre(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_pre')#the name of the class
        
        self.dash_length = C.dash_length
        self.entity.shader_state.handle_input('motion_blur')

        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.time = C.jump_dash_timer
        wall_dir = kwarg.get('wall_dir', False)
        if wall_dir:
            self.entity.dir[0] = -wall_dir[0]

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        pass

    def update(self):
        self.time -= self.entity.game_objects.game.dt        
        self.entity.velocity[1] = 0
        self.entity.velocity[0] = self.entity.dir[0] * max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity, alpha = 100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            if self.entity.acceleration[0] != 0:
                state = input.capitalize() + '_glide_main'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('Idle_main')
        elif input == 'interrupt':
            self.enter_state('Idle_main')

    def increase_phase(self):
        self.enter_phase('main')        

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.time > 0: self.enter_state('dash_jump')

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        super().enter_state(state, **kwarg)

class DashGroundMain(DashGroundPre):#level one dash: normal
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
    
    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_main')
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.game_objects.cosmetics.add(entities.Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))#dust
        self.dash_length = C.dash_length
        self.time = C.jump_dash_timer

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')
        self.enter_phase('post')

class DashGroundPost(DashGroundPre):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_post')       

    def update(self):
        pass

    def increase_phase(self):        
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run', phase = 'main')#enter run main phase

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            input.processed()

class DashJumpPre(PhaseBase):#enters from ground dash pre
    def __init__(self,entity, **kwarg):
        super().__init__(entity)       

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_pre')#the name of the class
        self.dash_length = C.dash_length
        self.entity.velocity[0] = C.dash_vel * self.entity.dir[0]
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.movement_manager.add_modifier('Dash_jump', entity = self.entity)
        self.entity.flags['ground'] = False
        self.entity.velocity[1] = C.dash_jump_vel_player
        self.buffer_time = C.jump_dash_wall_timer

    def exit_state(self):
        if self.dash_length < 0:
            self.enter_phase('main')

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay states
        pass

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input =='belt':
            if self.entity.collision_types['right'] and self.entity.dir[0] > 0 or self.entity.collision_types['left'] and self.entity.dir[0] < 0:
                if self.entity.acceleration[0] != 0:
                    if self.buffer_time < 0:
                        state = input.lower() + '_glide'
                        self.enter_state(state, **kwarg)
        elif input == 'interrupt':
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')     

    def enter_state(self, state):
        super().enter_state(state)
        self.entity.shader_state.handle_input('idle')   

    def enter_phase(self, phase):
        super().enter_phase(phase)
        self.entity.shader_state.handle_input('idle')   

    def update(self):
        self.entity.velocity[0] = self.entity.dir[0]*max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity, alpha = 100))
        self.dash_length -= self.entity.game_objects.game.dt
        self.buffer_time -= self.entity.game_objects.game.dt
        self.exit_state()

class DashJumpMain(PhaseBase):#basically falling
    def __init__(self,entity, **kwarg):
        super().__init__(entity)       

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_main')#the name of the class

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay states
        pass

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input =='belt':
            if self.entity.collision_types['right'] and self.entity.dir[0] > 0 or self.entity.collision_types['left'] and self.entity.dir[0] < 0:
                state = input.lower() + '_glide'
                self.enter_state(state, **kwarg)
        elif input == 'interrupt':
            self.enter_state('idle')
        elif input == 'Ground':
            self.enter_phase('post')            

class DashJumpPost(PhaseBase):#landing
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        pass

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_post')        

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')

class Sword(PhaseBase):#main phases shold inheret this
    def __init__(self,entity):
        super().__init__(entity)     

    def enter(self, **kwarg):   
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['sword'][0], vol = 0.7)
        self.entity.sword.stone_states['slash'].slash_speed()

class SwordStandPre(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'sword_stand1_pre'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        #self.entity.sword.currentstate.enter_state('Slash_1')
        #self.entity.projectiles.add(self.entity.sword)#add sword to group 

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):        
        self.enter_phase('main')

class SwordStandMain(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'sword_stand1_main'

    def enter(self, **kwarg):        
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['sword'][0], vol = 0.7)
        self.entity.sword.currentstate.enter_state('Slash_1')        
        self.entity.sword.stone_states['slash'].slash_speed()
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):        
        self.enter_phase('post')  

class SwordStandPost(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'sword_stand1_post'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')  

class SwordHeavyPre(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'sword_heavy_pre'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        #self.entity.sword.currentstate.enter_state('Slash_1')
        #self.entity.projectiles.add(self.entity.sword)#add sword to group 

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):        
        self.enter_phase('main')

class SwordHeavyMain(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'sword_heavy_main'

    def enter(self, **kwarg):        
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['sword'][0], vol = 0.7)
        self.entity.sword.currentstate.enter_state('Slash_1')        
        self.entity.sword.stone_states['slash'].slash_speed()
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):        
        self.enter_phase('post')  

class SwordHeavyPost(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'sword_heavy_post'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def update(self):
        super().update()
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')                                
#TODO the states below

class Air_dash_pre(PhaseBase):
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
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity, alpha = 100))
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

class Death_pre(PhaseBase):
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

class Death_charge(PhaseBase):
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

class Death_main(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.entity.dead()
        self.enter_state('Death_post')

class Death_post(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        pass

class Heal_pre(PhaseBase):
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

class Heal_main(PhaseBase):
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

class Stand_up_main(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Pray_pre(PhaseBase):
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

class Pray_main(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input == 'Pray_post':
            self.enter_state('Pray_post')

class Pray_post(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Hurt_main(PhaseBase):
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

class Spawn_main(PhaseBase):#enters when aila respawn after death
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

class Sword_fall_main(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.entity.sword.currentstate.enter_state('Slash_' + str(int(self.entity.sword.swing)+1))#slash 1 and 2
        self.entity.animation.play('fall_main')#animation name
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
        self.entity.animation.play('fall_main')#animation name
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

class Plant_bone_main(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('Idle_main')

class Thunder_pre(PhaseBase):
    def __init__(self, entity):
        self.entity = entity

        self.ball = entities.ThunderBall(self.entity.rect.topleft, self.entity.game_objects)#will be aila since aila will be swirlying
        self.entity.game_objects.cosmetics.add(self.ball)

        self.duration = 100
        self.entity.shader_state.enter_state('Swirl')#take current animation and swirl it

        if self.entity.abilities.spirit_abilities['Thunder'].level == 2:#aim arrow
            self.arrow = entities.Arrow_UI(self.entity.rect.topleft, self.entity.game_objects)
            self.entity.game_objects.cosmetics.add(self.arrow)

    def update(self):
        self.duration -= self.entity.game_objects.game.dt
        self.entity.velocity = [0, 0]

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.entity.shader_state.enter_state('Idle')
        self.ball.kill()
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

class Thunder_main(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.dir = kwarg.get('dir', [0, 1])
        self.time = 30#how long to thunder dive
        self.entity.flags['invincibility'] = True
        self.entity.shader_state.enter_state('MB')        

    def update(self):
        self.entity.game_objects.cosmetics.add(entities.Fade_effect(self.entity, alpha = 100))
        self.entity.velocity = [20*self.dir[0], 20*self.dir[1]]
        self.time -= self.entity.game_objects.game.dt
        if self.time < 0:
            self.exit_state()
            
    def exit_state(self):
        self.entity.shader_state.enter_state('Idle')    
        self.enter_state('Thunder_post')    

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input in ['Ground', 'Wall', 'belt']:                        
            self.exit_state()

class Thunder_post(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)        
        self.entity.game_objects.time_manager.modify_time(time_scale = 0, duration = 7, callback = lambda: self.entity.game_objects.camera_manager.camera_shake(amplitude = 30, duration = 30, scale = 0.9))#freeze
        
        sparks = entities.ThunderSpark(self.entity.rect.topleft, self.entity.game_objects)
        sparks.rect.midbottom = [self.entity.hitbox.midbottom[0], self.entity.hitbox.midbottom[1] + 16]#adjust the position
        self.entity.game_objects.cosmetics.add(sparks)        

    def update(self):
        self.entity.velocity = [0,0]

    def handle_movement(self, event):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        self.entity.flags['invincibility'] = False
        self.enter_state('Idle_main')

class Shield_main(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Shield'].initiate()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Run_main')

class Wind_main(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Wind'].initiate()

    def increase_phase(self):
        self.enter_state('Idle_main')

class Slow_motion_pre(PhaseBase):
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

class Bow_pre(PhaseBase):
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

class Bow_main(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Bow'].initiate(dir = kwarg['dir'], time = kwarg['time'])

    def increase_phase(self):
        self.enter_state('Idle_main')
