import random, math
from engine import constants as C
from engine.utils.functions import sign
from gameplay.entities.visuals.effects.fade_effect import FadeEffect
from gameplay.ui.components.overlay.point_arrow import PointArrow
from gameplay.entities.visuals.cosmetics import PlayerSoul, PrayEffect, ThunderBall, ThunderSpark, Dusts

class PlayerStates():
    def __init__(self, entity):
        self.entity = entity
        self.states = {
            'idle': IdleState(entity),
            'invisible': InvisibleState(entity),
            'run': RunState(entity),
            'walk': WalkState(entity),
            'sprint': SprintState(entity),
            'fall': FallState(entity),
            'land': LandState(entity),
            'jump': JumpState(entity),
            'jump_sprint': JumpSprintState(entity),
            'dash_ground': DashGroundState(entity),
            'dash_jump': DashJumpState(entity),
            'wall_glide': WallGlideState(entity),
            'belt_glide': BeltGlideState(entity),
            'wall_jump': WallJumpState(entity),
            'sword_stand1': SwordStand1State(entity),
            'sword_stand2': SwordStand2State(entity),
            'sword_air1': SwordAir1State(entity),
            'sword_air2': SwordAir2State(entity),
            'sword_down': SwordDownState(entity),
            'sword_up': SwordUpState(entity),
            'smash_side': SmashSideState(entity),
            'smash_up': SmashUpState(entity),
            'dash_air': DashAirState(entity),
            'death': DeathState(entity),
            'respawn': ReSpawnState(entity),#used when respawning after death
            'heal': HealState(entity),
            'crouch': CrouchState(entity),
            'plat_bone': PlantBoneState(entity),
            'thunder': ThunderState(entity),
            'shield': ShieldState(entity),
            'wind': WindState(entity),
            'slow_motion': SlowMotionState(entity),
            'bow': BowState(entity),
        }

        self.composite_state = self.states['idle']
        self.composite_state.enter_phase('main')
        self._state_factories = {'dash_air': [('dash_air', DashAirState)],
                                'smash_up': [('smash_up', SmashUpState)],
                                'wall': [('wall_jump', WallJumpState), ('wall_glide', WallGlideState), ('belt_glide', BeltGlideState)],
                                'dash': [('dash_ground', DashGroundState), ('dash_jump', DashJumpState)],
                                'bow': [('bow', BowState)],
                                'thunder': [('thunder', ThunderState)],
                                'shield': [('shield', ShieldState)],
                                'wind': [('wind', WindState)],
                                'slow_motion': [('slow_motion', SlowMotionState)]}#should contain all the states that can be created, so that they can be be appended to self.stataes when needed

    def enter_state(self, state_name, phase = None, **kwargs):
        state = self.states.get(state_name)
        if state:#if the requested state is unlocked
            if not state.enter_state(phase, **kwargs):
                self.composite_state.cleanup(**kwargs)
                self.composite_state = state

    def update(self, dt):#called from player
        self.composite_state.update(dt)#main state

    def handle_input(self, input, **kwargs):
        self.composite_state.handle_input(input, **kwargs)

    def handle_press_input(self, input):
        self.composite_state.handle_press_input(input)

    def handle_release_input(self, input):
        self.composite_state.handle_release_input(input)

    def handle_movement(self, event):#called from gameplay loop state
        self.composite_state.handle_movement(event)

    def increase_phase(self):#called when an animation is finished for that state
        self.composite_state.increase_phase()

    def unlock_state(self, name):#should be called when unlocking a new state
        for state_name, cls in self._state_factories[name]:
            self.states[state_name] = cls(self.entity)

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

    def cleanup(self, **kwarg): #called when exiting this state
        pass

    def common_values(self):#set common values for the phases
        pass

    def update(self, dt):
        self.current_phase.update(dt)

    def handle_input(self, input, **kwargs):
        self.current_phase.handle_input(input, **kwargs)

    def handle_press_input(self, input):
        self.current_phase.handle_press_input(input)

    def handle_release_input(self, input):
        self.current_phase.handle_release_input(input)

    def handle_movement(self, event):
        self.current_phase.handle_movement(event)

    def increase_phase(self):#called when an animation is finished for that state
        self.current_phase.increase_phase()

#wrappers
class FallState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': FallPre(entity), 'main': FallMain(entity)}        

    def common_values(self):#call when this state is enetred
        self.falltime = 0        

    def update(self, dt):
        self.falltime += dt

    def determine_fall(self):
        if self.falltime >= 40: return True
        return False

class LandState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'soft': LandSoftMain(entity), 'hard': LandHardMain(entity)}

class InvisibleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': Invisible(entity)}

class RunState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': RunPre(entity), 'main': RunMain(entity), 'post': RunPost(entity)}

class WalkState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': WalkPre(entity), 'main': WalkMain(entity), 'post': WalkPost(entity)}

class SprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SprintMain(entity), 'post': SprintPost(entity)}#'pre': SprintPre(entity), 

class IdleState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': IdleMain(entity)}

class JumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': JumpMain(entity)}

class JumpSprintState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': JumpSprintPre(entity),'main': JumpSprintMain(entity),'post': JumpSprintPost(entity)}

class DashGroundState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashGroundPre(entity), 'main': DashGroundMain(entity), 'post': DashGroundPost(entity)}

    def common_values(self):#called when entering this new state, and will not change during phase changes
        self.dir = self.entity.dir.copy()#copy the direction of the entity, and save it in the state across phases

    def enter_state(self, phase_name, **kwarg):#called when entering a new state
        if not self.entity.flags['grounddash']: return True
        super().enter_state(phase_name, **kwarg)

    def cleanup(self, **kwarg):
        if kwarg.get('to_dash_jump', False):
            return
        self.entity.flags['grounddash'] = False
        self.entity.game_objects.timer_manager.start_timer(C.ground_dash_timer, self.entity.on_grounddash_timout)

class WallGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallGlide(entity, animation_name = 'wall_glide_main')}#{'pre': WallGlide(entity, animation_name = 'wall_glide_pre'), 'main': WallGlide(entity, animation_name = 'wall_glide_main')}

class BeltGlideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BeltGlide(entity, animation_name = 'wall_glide_pre'), 'main': BeltGlide(entity, animation_name = 'wall_glide_main')}

class DashJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashJumpPre(entity)}#, 'main': DashJumpMain(entity), 'post': DashJumpPost(entity)}

    def enter_state(self, phase_name, **kwarg):#called when entering a new state
        if not self.entity.flags['grounddash']: return True
        super().enter_state(phase_name, **kwarg)

    def cleanup(self, **kwarg):
        self.entity.flags['grounddash'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.ground_dash_timer, self.entity.on_grounddash_timout)

class WallJumpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WallJumpMain(entity)}#'pre': WallJumpPre(entity),

class SwordStand1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {#'pre': SwordStandPre(entity, animation_name = 'sword_stand1_pre'),
                       'main': SwordStandMain(entity, animation_name = 'sword_stand1_main'),
                       'post': SwordStandPost(entity, animation_name = 'sword_stand1_post')}#

class SwordStand2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {#'pre': SwordStandPre(entity, animation_name = 'sword_stand2_pre'),
                       'main': SwordStandMain(entity, animation_name = 'sword_stand2_main'),
                       'post': SwordStandPost(entity, animation_name = 'sword_stand2_post')}#

class SwordDownState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordDownMain(entity)}

class SwordUpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordUpMain(entity)}

class SmashSideState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SmashSidePre(entity), 'charge': SmashSideCharge(entity), 'main': SmashSideMain(entity), 'post': SmashSidePost(entity)}

class SmashUpState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SmashUpPre(entity), 'charge': SmashUpCharge(entity), 'main': SmashUpMain(entity), 'post': SmashUpPost(entity)}

class SwordAir1State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air1_main')}

class SwordAir2State(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': SwordAirMain(entity, animation_name = 'sword_air2_main')}

class DashAirState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DashAirPre(entity), 'main': DashAirMain(entity), 'post': DashAirPost(entity)}

class DeathState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': DeathPre(entity), 'main': DeathMain(entity), 'post': DeathPost(entity)}

class ReSpawnState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': ReSpawnMain(entity)}

class HealState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': HealPre(entity), 'main': HealMain(entity)}

class CrouchState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': CrouchPre(entity), 'main': CrouchMain(entity), 'post': CrouchPost(entity)}

class PlantBoneState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': PlantBoneMain(entity)}

class ThunderState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': ThunderPre(entity), 'main': ThunderMain(entity), 'post': ThunderPost(entity)}

class ShieldState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': ShieldPre(entity), 'main': ShieldMain(entity)}

class WindState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'main': WindMain(entity)}

class SlowMotionState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': SlowMotionPre(entity), 'main': SlowMotionMain(entity)}

class BowState(CompositeState):
    def __init__(self, entity):
        super().__init__(entity)
        self.phases = {'pre': BowPre(entity), 'main': BowMain(entity)}

#normal phases
class PhaseBase():
    def __init__(self, entity):
        self.entity = entity

    def update(self, dt):
        pass

    def increase_phase(self):
        pass

    def handle_input(self, input, **kwarg):
        pass

    def enter(self, **kwarg):#called when entering a new phase
        pass

    def enter_state(self, new_state, **kwarg):#should call when entering a new state
        self.entity.currentstate.enter_state(new_state, **kwarg)

    def enter_phase(self, phase_name, **kwarg):#should call when just changing phase
        self.entity.currentstate.composite_state.enter_phase(phase_name, **kwarg)

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_release_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press

        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        multiplier = 0
        if 0.1 < abs(value[0]) < 0.65:
            multiplier = 0.3
        elif abs(value[0]) >= 0.65:
            multiplier = 1
        self.entity.acceleration[0] = C.acceleration[0] * multiplier#always positive, add acceleration to entity

        self.entity.dir[1] = -value[1]
        if multiplier > 0:
            self.entity.dir[0] = sign(value[0])

    def do_ability(self):#called when pressing B (E). This is needed if all of them do not have pre animation, or vice versa
        self.enter_state(self.entity.abilities.equip.lower())

class PhaseAirBase(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press

        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        multiplier = 0
        if abs(value[0]) > 0.1:
            multiplier = 1
        self.entity.acceleration[0] = C.acceleration[0] * multiplier#always positive, add acceleration to entity

        self.entity.dir[1] = -value[1]
        if multiplier > 0:
            self.entity.dir[0] = sign(value[0])

class Invisible(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('invisible')

class IdleMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('idle', f_rate = 0.1667)
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self, dt):
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
        elif event[-1] == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()

        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()
        elif event[-1]=='rt':#depends on if the abillities have pre or main animation
            input.processed()
            self.enter_state('heal')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_movement(self, event):
        super().handle_movement(event)
        if abs(self.entity.acceleration[0]) > 0.5:
            self.enter_state('run')
        elif abs(self.entity.acceleration[0]) > 0.1:
            self.enter_state('walk')

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

    def update(self, dt):
        self.particle_timer -= dt
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
        elif event[-1] == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
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
        self.entity.animation.play('run_main')
        self.particle_timer = 0
        self.sfx_loop_time = 18
        self.sfx_timer = 1

    def update(self, dt):
        self.particle_timer -= dt
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

    def enter_state(self, new_state, **kwarg):
        #self.sfx_channel.stop()
        super().enter_state(new_state, **kwarg)

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
        elif abs(self.entity.acceleration[0]) < 0.3:
            self.enter_state('walk', phase = 'main')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1]) < 0.8:
            state='sword_stand'+str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0.8:
            self.enter_state('sword_up')

class RunPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('run_post')

    def update(self, dt):
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
        elif event[-1] == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
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
            self.enter_state('sword_up')

    def increase_phase(self):
        self.enter_state('idle')

class WalkPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('walk_pre')
        self.particle_timer = 0
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times

    def update(self, dt):
        self.particle_timer -= dt
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
        elif event[-1] == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
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
        elif abs(self.entity.acceleration[0]) > 0.5:
            self.enter_state('run')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1])<0.8:
            state='sword_stand'+str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1]>0.8:
            self.enter_state('sword_up')

class WalkMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('walk_main')
        self.particle_timer = 0
        self.sfx_loop_time = 18
        self.sfx_timer = 1

    def update(self, dt):
        self.particle_timer -= dt
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
        elif abs(self.entity.acceleration[0]) > 0.5:
            self.enter_state('run')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if abs(self.entity.dir[1]) < 0.8:
            state='sword_stand'+str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing
        elif self.entity.dir[1] > 0.8:
            self.enter_state('sword_up')

class WalkPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('walk_post')

    def update(self, dt):
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
        elif event[-1] == 'x':
            if input.meta.get('smash'):
                direction = input.meta.get('direction')
                if direction == 'left':
                    self.enter_state('smash_side', dir = -1)
                elif direction == 'right':
                    self.enter_state('smash_side', dir = 1)
                elif direction == 'up':
                    self.enter_state('smash_up')
            else:
                self.swing_sword()
            input.processed()
        elif event[-1]=='b':#depends on if the abillities have pre or main animation
            input.processed()
            self.do_ability()

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] != 0:
            self.entity.currentstate.composite_state.enter_phase('pre')
        elif abs(self.entity.acceleration[0]) > 0.5:
            self.enter_state('run')

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
            self.enter_state('sword_up')

    def increase_phase(self):
        self.enter_state('idle')

class SprintPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sprint_pre')
        self.entity.flags['ground'] = True

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')#main

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def handle_movement(self,event):
        super().handle_movement(event)
        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')

class SprintMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sprint_main')

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')#fall pre
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump_sprint')#main

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()
        elif event[-1]=='lb':
            self.enter_phase('post')           

    def handle_movement(self,event):
        value = event['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * 2#always positive, add acceleration to entity

        if self.entity.acceleration[0] == 0:
            self.entity.currentstate.composite_state.enter_phase('post')

class SprintPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sprint_post')

    def update(self, dt):
        if not self.entity.collision_types['bottom']:
            self.enter_state('fall')#pre
            self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')#main

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')#enter run

class JumpMain(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_main')#the name of the class
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['jump'][random.randint(0,2)], vol = 0.1)
        self.entity.animation.frame = kwarg.get('frame', 0)
        self.jump_dash_timer = C.jump_dash_timer
        #self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.flags['ground'] = False
        self.shroomboost = 1#if landing on shroompoline and press jump, this vakue is modified
        try:
            self.air_timer = self.entity.colliding_platform.jumped()#jump charactereistics is set from the platform
        except AttributeError:
            print(self.entity.flags['ground'])
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'two'))#dust

    def update(self, dt):
        self.jump_dash_timer -= dt
        self.air_timer -= dt
        if self.air_timer >= 0:
            self.entity.velocity[1] = C.jump_vel_player * self.shroomboost
        if self.entity.velocity[1] >= 0.7:
            self.enter_state('fall')#pre

    def handle_press_input(self,input):
        event = input.output()
        if event[-1]=='lb':
            input.processed()
            if self.jump_dash_timer > 0:
                self.entity.velocity[1] = 0
                self.enter_state('dash_jump')
            else:
                self.enter_state('dash_air')
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
            self.enter_state('belt_glide')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('sword_down')
        else:#right or left
            state = 'sword_air' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

class JumpSprintPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_sprint_pre')#the name of the class
        self.air_timer = 10
        self.entity.flags['ground'] = False

    def update(self, dt):
        self.air_timer -= dt
        if self.air_timer >= 0:
            self.entity.velocity[1] = C.jump_vel_player
            self.entity.velocity[0] = self.entity.dir[0] * 10      
        else:
            self.enter_phase('main')  

class JumpSprintMain(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('jump_sprint_main')#the name of the class
        try:
            self.air_timer = self.entity.colliding_platform.jumped()#jump charactereistics is set from the platform
        except AttributeError:
            print(self.entity.flags['ground'])

    def update(self, dt):
        self.entity.velocity[0] += self.entity.dir[0]

    def handle_input(self, input):
        if input == 'Ground':
            self.enter_phase('post')

class JumpSprintPost(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):#landing
        self.entity.animation.play('jump_sprint_post')#the name of the class
        self.entity.flags['ground'] = True

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        self.entity.acceleration[0] = 0

    def update(self, dt):
        self.entity.velocity[0] += 0.5 * self.entity.dir[0]

    def increase_phase(self):
        self.enter_state('idle')

class WallJumpPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('wall_jump_pre')

    def update(self, dt):
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
        self.entity.velocity[0] = -self.entity.dir[0]*6
        self.ignore_input_timer = 8
        self.accelerate_timer = 15
        self.start_dir = -self.entity.dir[0]

    def update(self, dt):
        super().update(dt)
        self.ignore_input_timer -= 1
        self.accelerate_timer -= 1

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        super().handle_movement(event)
        if self.ignore_input_timer > 0:
            self.entity.dir[0] = self.start_dir
        if self.accelerate_timer > 0:
            self.entity.acceleration[0] = C.acceleration[0]

class FallPre(PhaseAirBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('fall_pre')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('jump')#TODO how about sprint jump
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='lb':
            if self.entity.flags['ground']:
                input.processed()
                self.enter_state('dash_ground')
            else:
                input.processed()
                self.enter_state('dash_air')
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
            self.enter_state('belt_glide')
        elif input == 'Ground':
            if self.entity.currentstate.states['fall'].determine_fall():
                self.enter_state('land', phase = 'hard')
            else:
                if self.entity.acceleration[0] != 0:
                    self.enter_state('run')#enter run pre phase
                else:                
                    self.enter_state('land', phase = 'soft')

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('sword_down')
        else:#right or left
            state = 'sword_air' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
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

class LandSoftMain(PhaseBase):#landing: mainly cosmetic
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['ground'] = True
        self.entity.animation.play('land_soft_main')

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press                
        if 0.1 < abs(value[0]) < 0.65:
            self.enter_state('walk')
        elif abs(value[0]) >= 0.65:
            self.enter_state('run')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            self.enter_state('jump')
        elif event[-1]=='b':
            input.processed()
            self.do_ability()
        elif event[-1]=='lb':
            input.processed()
            self.enter_state('dash_ground')
        elif event[-1]=='x':
            input.processed()
            self.swing_sword()

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='a':
            input.processed()

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('idle')    

    def swing_sword(self):
        if not self.entity.flags['attack_able']: return
        if self.entity.dir[1] > 0.7:
            self.enter_state('sword_up')
        elif self.entity.dir[1] < -0.7:
            self.enter_state('sword_down')
        else:#right or left
            state = 'sword_stand' + str(int(self.entity.sword.swing)+1)
            self.enter_state(state)
            self.entity.sword.swing = not self.entity.sword.swing

class LandHardMain(PhaseBase):#landing: cannot move
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['ground'] = True
        self.entity.animation.play('land_hard_main')

    def update(self, dt):
        self.entity.velocity[0] = 0

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('idle')

class WallGlide(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']


    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)#the name of the class
        self.entity.flags['ground'] = False#used for jumping: sets to false in cayote timer and in jump state
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.movement_manager.add_modifier('wall_glide')
        if self.entity.collision_types['right']:
            self.dir = [1,0]
        else:
            self.dir = [-1,0]
        self.timer_init = 6
        self.timer = self.timer_init
        self.count_timer = False

    def update(self, dt):#is needed
        if self.count_timer:
            self.timer -= dt
            if self.timer <= 0:
                self.fall()
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.entity.velocity[0] = 0
            self.enter_state('fall', wall_dir = self.dir)
        else:
            self.entity.velocity[0] += self.entity.dir[0] * 0.2



    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
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
        curr_dir = self.entity.dir[0]

        if value[0] * curr_dir < 0:
            self.count_timer = True
        elif value[0] * curr_dir > 0:
            self.count_timer = False
            self.timer = self.timer_init

    def fall(self):
        self.entity.velocity[0] = -self.entity.dir[0]*2
        self.enter_state('fall', wall_dir = self.dir)

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def enter_state(self, input, **kwarg):#reset friction before exiting this state
        self.entity.movement_manager.remove_modifier('wall_glide')
        super().enter_state(input, **kwarg)

class BeltGlide(PhaseBase):#same as wall glide but only jump if wall_glide has been unlocked
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)#the name of the class
        self.entity.flags['ground'] = True#used for jumping: sets to false in cayote timer and in jump state
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.entity.movement_manager.add_modifier('wall_glide')
        if self.entity.collision_types['right']:
            self.dir = [1,0]
        else:
            self.dir = [-1,0]

    def update(self, dt):#is needed
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_press_input(self,input):
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.velocity[0] = -self.dir[0]*10
                self.entity.velocity[1] = -7#to get a vertical velocity
                self.enter_state('jump')
            else:
                self.entity.velocity[0] = -self.entity.dir[0]*10
                self.enter_state('fall')
        elif event[-1] == 'lb':
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.dir[0] *= -1
                input.processed()
                self.enter_state('dash_ground')

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        curr_dir = self.entity.dir[0]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

        if value[0] * curr_dir < 0:#change sign
            self.entity.velocity[0] = self.entity.dir[0]*2
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')
        elif value[0] == 0:#release
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('fall')
            if self.entity.currentstate.states.get('wall_glide'):
                self.entity.game_objects.timer_manager.start_timer(C.cayote_timer_player, self.entity.on_cayote_timeout, ID = 'cayote')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            self.enter_state('run')

    def enter_state(self,input):#reset friction before exiting this state
        self.entity.movement_manager.remove_modifier('wall_glide')
        super().enter_state(input)

class DashGroundPre(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):        
        self.entity.animation.play('dash_ground_pre')#the name of the class

        self.dash_length = C.dash_length
        if int(self.entity.velocity[0]) == 0:
            self.dash_length += 1
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))#dust
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_manager.add_modifier('dash', entity = self.entity)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0], vol = 1)    
        self.wall_buffer = 3

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        self.entity.acceleration[0] = 0

    def update(self, dt):
        self.jump_dash_timer -= dt
        #self.entity.velocity[1] = 0
        #self.entity.velocity[0] = self.entity.dir[0] * max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.dash_length -= dt
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            self.wall_buffer -= 1
            if self.wall_buffer > 0: return
            if self.entity.acceleration[0] != 0:
                state = input.lower() + '_glide'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('idle')
        elif input == 'interrupt':
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            input.processed()
            if self.jump_dash_timer > 0: self.enter_state('dash_jump', to_dash_jump=True)

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.movement_manager.remove_modifier('dash')
        super().enter_state(state, **kwarg)

class DashGroundMain(DashGroundPre):#level one dash: normal
    def __init__(self, entity, **kwarg):
        super().__init__(entity)        

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_main')
        self.dash_length = C.dash_length
        self.jump_dash_timer = C.jump_dash_timer
        self.wall_buffer = 3

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()   

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')     
        if self.entity.game_objects.controller.is_held('lb'):
            self.enter_state('sprint')  
        else:
            self.enter_phase('post')#enter run              

class DashGroundPost(DashGroundPre):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_ground_post')
        self.entity.movement_manager.remove_modifier('dash')
        self.wall_buffer = 3

    def update(self, dt):
        pass

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press
        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.acceleration[0] = C.acceleration[0] * abs(value[0])#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')#enter run

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            self.enter_state('jump')
            input.processed()

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.currentstate.enter_state(state, **kwarg)

class DashJumpPre(PhaseBase):#enters from ground dash pre
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_jump_pre')#the name of the class
        self.dash_length = C.dash_jump_length
        if int(self.entity.velocity[0]) == 0:
            self.dash_length += 1
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0])
        self.entity.movement_manager.add_modifier('dash_jump', entity = self.entity)
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.flags['ground'] = False
        self.buffer_time = C.jump_dash_wall_timer
        self.entity.velocity[1] *= 0

    def exit_state(self):
        if self.dash_length < 0:
            self.entity.movement_manager.add_modifier('air_boost', entity = self.entity)
            self.enter_state('fall')

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        self.entity.acceleration[0] = 0

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input =='belt':
            if self.entity.collision_types['right'] and self.entity.dir[0] > 0 or self.entity.collision_types['left'] and self.entity.dir[0] < 0:
                if self.entity.acceleration[0] != 0:
                    if self.buffer_time < 0:
                        state = input.lower() + '_glide'
                        self.enter_state(state, **kwarg)

    def enter_state(self, state):
        self.entity.acceleration[1] = C.acceleration[1]
        self.entity.movement_manager.remove_modifier('dash_jump')
        super().enter_state(state)
        self.entity.shader_state.handle_input('idle')

    def update(self, dt):
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.buffer_time -= dt
        self.dash_length -= dt
        self.exit_state()

class DashJumpMain(PhaseBase):
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
        elif input == 'Ground':
            if self.entity.acceleration[0] == 0:
                self.enter_state('idle')
            else:
                self.enter_state('run')

class DashJumpPost(PhaseBase):#landing
    def __init__(self,entity):
        super().__init__(entity)

    def update(self, dt):
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
        self.entity.sword.use_sword()

class SwordAir(PhaseAirBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()

class SwordStandPre(Sword):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        #self.entity.sword.currentstate.enter_state('Slash_1')
        #self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        self.enter_phase('main')

class SwordStandMain(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()

        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.sword.use_sword()

        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press
        if value[0] == 0:
            self.entity.acceleration[0] = 0

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.8

    def increase_phase(self):
        self.enter_phase('post')

class SwordStandPost(Sword):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('run')

    #def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
    #    value = event['l_stick']#the avlue of the press
    #    if value[0] == 0:
    #        self.entity.acceleration[0] = 0

class SwordDownMain(SwordAir):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sword_down_main')
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()
        self.entity.sword.currentstate.enter_state('Slash_down')
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def increase_phase(self):
        self.enter_state('fall')

class SwordUpMain(Sword):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('sword_up_main')
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.use_sword()
        self.entity.sword.currentstate.enter_state('Slash_up')
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def increase_phase(self):
        if self.entity.flags['ground']:
            if self.entity.acceleration[0] == 0:
                self.enter_state('idle')
            else:
                self.enter_state('run')
        else:
            self.enter_state('fall')

class SmashSidePre(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_pre'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.release_input = False#used to check if the input is released, so that the sword can be swung
        self.entity.dir[0] = kwarg['dir']

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] = 0

    def increase_phase(self):
        if self.release_input:
            self.enter_phase('main')
        else:
            self.enter_phase('charge')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='x':
            self.release_input = True

class SmashSideCharge(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_charge'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.time  = 20

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] = 0
        self.time -= dt
        if self.time < 0: self.enter_phase('main')

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def increase_phase(self):
        pass

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='x':
            self.enter_phase('main')

class SmashSideMain(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_main'

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')
        self.entity.sword.use_sword()
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.1

    def increase_phase(self):
        self.enter_phase('post')

class SmashSidePost(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_side_post'

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.1

    def increase_phase(self):
        self.enter_state('idle')

class SmashUpPre(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_up_pre'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.release_input = False#used to check if the input is released, so that the sword can be swung

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] = 0

    def increase_phase(self):
        if self.release_input:
            self.enter_phase('main')
        else:
            self.enter_phase('charge')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='x':
            self.release_input = True

class SmashUpCharge(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_up_charge'

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.time  = 20

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] = 0
        self.time -= dt
        if self.time < 0: self.enter_phase('main')

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def increase_phase(self):
        pass

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='x':
            self.enter_phase('main')

class SmashUpMain(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_up_main'

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)
        self.entity.flags['attack_able'] = False#if fasle, sword cannot be swang. sets to true when timer runs out
        self.entity.game_objects.timer_manager.start_timer(C.sword_time_player, self.entity.on_attack_timeout)
        self.entity.abilities.spirit_abilities['Shield'].sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_up')
        self.entity.sword.use_sword()
        self.entity.projectiles.add(self.entity.sword)#add sword to group

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.1

    def increase_phase(self):
        self.enter_phase('post')

class SmashUpPost(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.animation_name = 'smash_up_post'

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        pass

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)

    def update(self, dt):
        super().update(dt)
        self.entity.velocity[0] *= 0.1

    def increase_phase(self):
        self.enter_state('idle')

class SwordAirMain(SwordAir):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)
        self.animation_name = kwarg['animation_name']

    def enter(self, **kwarg):
        self.entity.animation.play(self.animation_name)#animation name
        self.entity.sword.use_sword()
        self.entity.sword.dir = self.entity.dir.copy()
        self.entity.sword.currentstate.enter_state('Slash_1')#slash 1 and 2
        self.entity.projectiles.add(self.entity.sword)#add sword to grou

    def increase_phase(self):
        self.enter_state('fall')

    def handle_input(self, input, **kwarg):
        if input == 'Ground':
            if self.entity.acceleration[0] != 0:
                self.enter_state('run')
            else:
                self.enter_state('idle')

class DashAirPre(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_air_pre')#the name of the class

        self.dash_length = C.dash_length
        self.entity.shader_state.handle_input('motion_blur')
        self.entity.game_objects.cosmetics.add(Dusts(self.entity.hitbox.center, self.entity.game_objects, dir = self.entity.dir, state = 'one'))#dust
        self.entity.flags['ground'] = True
        self.entity.game_objects.timer_manager.remove_ID_timer('cayote')#remove any potential cayote times
        self.jump_dash_timer = C.jump_dash_timer
        self.entity.movement_manager.add_modifier('dash', entity = self.entity)
        self.entity.velocity[1] *= 0
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['dash'][0], vol = 1)
        wall_dir = kwarg.get('wall_dir', False)
        if wall_dir:
            self.entity.dir[0] = -wall_dir[0]

    def handle_movement(self, event):#all dash states should omit setting entity.dir
        self.entity.acceleration[0] = 0

    def update(self, dt):
        self.jump_dash_timer -= dt
        #self.entity.velocity[1] = 0
        #self.entity.velocity[0] = self.entity.dir[0] * max(C.dash_vel,abs(self.entity.velocity[0]))#max horizontal speed
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.dash_length -= dt
        self.entity.emit_particles(lifetime = 40, scale=3, colour = C.spirit_colour, gravity_scale = 0.5, gradient = 1, fade_scale = 7,  number_particles = 1, vel = {'wave': [-10*self.entity.dir[0], -2]})
        self.exit_state()

    def exit_state(self):
        if self.dash_length < 0:
            self.increase_phase()

    def handle_input(self, input, **kwarg):
        if input == 'Wall' or input == 'belt':
            self.entity.shader_state.handle_input('idle')
            if self.entity.acceleration[0] != 0:
                state = input.lower() + '_glide'
                self.enter_state(state, **kwarg)
            else:
                self.enter_state('idle')
        elif input == 'interrupt':
            self.entity.shader_state.handle_input('idle')
            self.enter_state('idle')

    def increase_phase(self):
        self.enter_phase('main')

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        pass
        #event = input.output()
        #if event[-1] == 'a':
        #    input.processed()
        #    if self.jump_dash_timer > 0: self.enter_state('dash_jump')

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.movement_manager.remove_modifier('dash')
        super().enter_state(state, **kwarg)

class DashAirMain(DashGroundPre):#level one dash: normal
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_air_main')
        self.dash_length = C.dash_length
        self.jump_dash_timer = C.jump_dash_timer
        self.wall_buffer = 3

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        input.processed()

    def increase_phase(self):
        self.entity.shader_state.handle_input('idle')
        self.enter_phase('post')

class DashAirPost(DashGroundPre):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('dash_air_post')
        self.entity.movement_manager.remove_modifier('dash')
        self.wall_buffer = 3

    def update(self, dt):
        pass

    def handle_movement(self, event):#all states should inehrent this function: called in update function of gameplay state
        value = event['l_stick']#the avlue of the press
        #self.entity.acceleration[0] = C.acceleration[0] * math.ceil(abs(value[0]*0.8))#always positive, add acceleration to entity
        self.entity.acceleration[0] = C.acceleration[0] * abs(value[0])#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]
        if abs(value[0]) > 0.1:
            self.entity.dir[0] = sign(value[0])

    def increase_phase(self):
        self.entity.movement_manager.add_modifier('air_boost', entity = self.entity)
        if self.entity.acceleration[0] == 0:
            self.enter_state('idle')
        else:
            self.enter_state('fall')#enter run main phase

    def handle_press_input(self, input):#all states should inehrent this function, if it should be able to jump
        event = input.output()
        if event[-1] == 'a':
            self.enter_state('jump')
            input.processed()

    def enter_state(self, state, **kwarg):
        self.entity.shader_state.handle_input('idle')
        self.entity.currentstate.enter_state(state, **kwarg)

class DeathPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)
        self.timeout = 50

    def enter(self, **kwarg):
        self.entity.animation.play('death_pre')
        self.entity.game_objects.cosmetics.add(PlayerSoul([self.entity.rect[0],self.entity.rect[1]],self.entity.game_objects))

    def update(self, dt):
        self.timeout -= dt
        self.entity.acceleration[0] = 0#slow down
        self.entity.invincibile = True
        if self.timeout < 0:
            self.enter_phase('main')

    def handle_movement(self,event):
        pass

    def handle_input(self, input):
        if input == 'Ground' or input == 'hole':
            self.enter_phase('main')

class DeathMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('death_main')

    def update(self, dt):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_phase('post')

class DeathPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.dead()
        self.entity.animation.play('death_post')

    def update(self, dt):
        self.entity.invincibile = True

    def handle_movement(self,event):
        pass

class ReSpawnMain(PhaseBase):#enters when aila respawn after death
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('respawn')
        self.entity.invincibile = False

    def handle_movement(self,event):
        pass

    def increase_phase(self):#when animation finishes
        self.entity.health = max(self.entity.health,0)#if negative, set it to 0
        self.entity.heal(self.entity.max_health)
        if self.entity.backpack.map.spawn_point.get('bone', False):#if bone, remove it
            self.entity.backpack.map.spawn_point.pop()
        self.enter_state('idle')

class HealPre(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('heal_pre')

    def handle_release_input(self, input):
        event = input.output()
        if event[-1] == 'rt':#if releasing the button
            input.processed()
            self.enter_state('idle')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.enter_phase('main')

class HealMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('heal_main')
        self.heal_cost = 1

    def handle_release_input(self, input):
        event = input.output()
        if event[-1] == 'rt':#if releasing the button
            input.processed()
            self.enter_state('idle')

    def handle_movement(self, event):
        pass

    def increase_phase(self):
        self.entity.heal()
        self.entity.backpack.inventory.remove('amber_droplet', self.heal_cost)
        self.enter_state('Heal_main')

class CrouchPre(PhaseBase):#used when saving and picking up interactable items
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('crouch_pre')
        self.entity.acceleration[0] = 0

        #effect
        effect = PrayEffect(self.entity.rect.center,self.entity.game_objects)
        effect.rect.bottom = self.entity.rect.bottom
        self.entity.game_objects.cosmetics.add(effect)
        self.entity.game_objects.sound.play_sfx(self.entity.sounds['pray'][0])

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_phase('main')

class CrouchMain(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)
        self.animation_number = 1#1 blinks, 2 doesn't

    def enter(self, **kwarg):
        self.entity.animation.play('crouch1_main')       #

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        if random.randint(0, self.animation_number * 2) == 0:
            self.animation_number = 3 - self.animation_number#altrernate vetwwn 1 and 2
            animation_name = 'crouch' + str(self.animation_number) + '_main'
            self.entity.animation.play(animation_name)

    def handle_input(self, input, **kwarg):#called from savepoint when animation finishes, or when picking up an interactable item
        if input == 'pray_post':
            self.enter_phase('post')

class CrouchPost(PhaseBase):#standing up
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('crouch_post')

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('idle')

class PlantBoneMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('plant_bone_main')
        self.entity.acceleration[0] = 0

    def handle_movement(self,event):
        pass

    def increase_phase(self):
        self.enter_state('idle')

#abilities
class ThunderPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        #self.entity.animation.play('thunder_pre')
        self.ball = ThunderBall(self.entity.rect.topleft, self.entity.game_objects)#will be aila since aila will be swirlying
        self.entity.game_objects.cosmetics.add(self.ball)

        self.duration = 100
        self.entity.shader_state.enter_state('Swirl')#take current animation and swirl it

        if self.entity.abilities.spirit_abilities['Thunder'].level == 2:#aim arrow
            self.arrow = PointArrow(self.entity.rect.topleft, self.entity.game_objects)
            self.entity.game_objects.cosmetics.add(self.arrow)

    def update(self, dt):
        self.duration -= dt
        self.entity.velocity = [0, 0]

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.entity.shader_state.enter_state('Idle')
        self.ball.kill()
        if self.entity.abilities.spirit_abilities['Thunder'].level == 1:
            self.enter_phase('main', dir = [0,1])
        else:
            self.arrow.kill()
            self.enter_phase('main', dir = [self.arrow.dir[0],-self.arrow.dir[1]])

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

class ThunderMain(PhaseBase):
    def __init__(self,entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('thunder_main')
        self.dir = kwarg.get('dir', [0, 1])
        self.time = 30#how long to thunder dive
        self.entity.flags['invincibility'] = True
        self.entity.shader_state.enter_state('MB')

    def update(self, dt):
        self.entity.game_objects.cosmetics.add(FadeEffect(self.entity, alpha = 100))
        self.entity.velocity = [20*self.dir[0], 20*self.dir[1]]
        self.time -= dt
        if self.time < 0:
            self.exit_state()

    def exit_state(self):
        self.entity.shader_state.enter_state('Idle')
        self.enter_phase('post')

    def handle_movement(self,event):
        pass

    def handle_input(self, input, **kwarg):
        if input in ['Ground', 'Wall', 'belt']:
            self.exit_state()

class ThunderPost(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('thunder_post')
        self.entity.game_objects.time_manager.modify_time(time_scale = 0, duration = 7, callback = lambda: self.entity.game_objects.camera_manager.camera_shake(amplitude = 30, duration = 30, scale = 0.9))#freeze

        sparks = ThunderSpark(self.entity.rect.topleft, self.entity.game_objects)
        sparks.rect.midbottom = [self.entity.hitbox.midbottom[0], self.entity.hitbox.midbottom[1] + 16]#adjust the position
        self.entity.game_objects.cosmetics.add(sparks)

    def update(self, dt):
        self.entity.velocity = [0,0]

    def handle_movement(self, event):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        self.entity.flags['invincibility'] = False
        self.enter_state('idle')

class ShieldPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.acceleration[0] = 0#stop moving
        self.entity.animation.play('shield_pre')

    def increase_phase(self):
        self.enter_phase('main')

class ShieldMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.animation.play('shield_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Shield'].initiate()

    def increase_phase(self):
        self.enter_state('idle')

class SlowMotionPre(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.acceleration[0] = 0#stop moving
        self.entity.animation.play('slow_motion_pre')

    def increase_phase(self):
        self.enter_phase('main')

class SlowMotionMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_movement(self, event):
        pass

    def enter(self):
        self.entity.animation.play('slow_motion_main')
        self.entity.abilities.spirit_abilities['Slow_motion'].initiate()

    def increase_phase(self):
        self.enter_state('idle')

class WindMain(PhaseBase):
    def __init__(self,entity):
        super().__init__(entity)

    def enter(self):
        self.entity.animation.play('wind_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Wind'].initiate()

    def increase_phase(self):
        self.enter_state('idle')

class BowPre(PhaseBase):
    def __init__(self, entity):
        super().__init__(entity)

    def enter(self):
        self.entity.animation.play('bow_pre')
        self.duration = 100#charge times
        self.arrow = PointArrow(self.entity.rect.topleft, self.entity.game_objects, dir = self.entity.dir.copy())
        self.entity.game_objects.cosmetics.add(self.arrow)
        self.time = 0

    def update(self, dt):
        self.duration -= dt
        self.time += dt
        self.entity.velocity = [0, 0]

        if self.duration < 0:
            self.exit_state()

    def exit_state(self):
        self.arrow.kill()
        self.enter_phase('main', dir = [self.arrow.dir[0], -self.arrow.dir[1]], time = self.time)

    def handle_release_input(self, input):
        event = input.output()
        if event[-1]=='b':
            input.processed()
            self.exit_state()

    def handle_movement(self, event):
        value = event['l_stick']#the avlue of the press
        if value[0] != 0 or value[1] != 0:
            self.arrow.dir = [value[0],-value[1]]

class BowMain(PhaseBase):
    def __init__(self, entity, **kwarg):
        super().__init__(entity)

    def enter(self, **kwarg):
        self.entity.animation.play('bow_main')
        self.entity.consume_spirit()
        self.entity.abilities.spirit_abilities['Bow'].initiate(dir = kwarg['dir'], time = kwarg['time'])

    def increase_phase(self):
        self.enter_state('idle')
