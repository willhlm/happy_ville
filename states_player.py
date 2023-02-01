import sound, Entities, sys
from states_entity import Entity_States
import constants as C

class Player_states(Entity_States):
    def __init__(self,entity):
        super().__init__(entity)

    def enter_state(self,newstate):
        state = newstate[:newstate.rfind('_')]#get the name up to last _ (remove pre, main, post)
        if state in self.entity.states:
            self.entity.currentstate = getattr(sys.modules[__name__], newstate)(self.entity)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.update_state()

    def increase_phase(self):#called when an animation is finihed for that state
        pass

    def handle_press_input(self,input):#all states should inehrent this function
        if input[-1] == 'a':
            self.entity.timer_jobs['shroomjump'].activate()
            self.entity.timer_jobs['jump'].activate()

    def handle_release_input(self,input):#all states should inehrent this function
        if input[-1] == 'a':
            if self.entity.velocity[1] < 0:#if going up
                self.entity.velocity[1] = 0.5*self.entity.velocity[1]

    def handle_movement(self,input):#all states should inehrent this function
        #left stick and arrow keys
        value = input[2]['l_stick']#the avlue of the press
        self.entity.acceleration[0] = abs(value[0])*C.acceleration[0]#always positive, add acceleration to entity
        self.entity.dir[1] = -value[1]

        if value[0] > 0.2:#x
            self.entity.dir[0] = 1
        elif value[0] < -0.2:#x
            self.entity.dir[0] = -1

    def handle_input(self,input):
        pass

    def do_ability(self):#called when pressing B (E). This is needed if all of them do not have pre animation, or vice versa
        if self.entity.equip=='Thunder' or self.entity.equip=='Darksaber':
            self.enter_state(self.entity.equip + '_pre')
        else:
            self.enter_state(self.entity.equip + '_main')

class Idle_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if not self.entity.collision_types['bottom']:
            self.enter_state('Fall_stand_pre')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_stand_pre')
        elif input[-1]=='lb':
            self.enter_state('Dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation
            self.do_ability()
        elif input[-1] == 'rt':
            self.enter_state('Counter_pre')

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0] != 0:
            self.enter_state('Walk_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]==0:
                state='Sword_stand'+str(int(self.entity.sword_swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword_swing = not self.entity.sword_swing

            elif self.entity.dir[1]>0:
                self.enter_state('Sword_up_pre')

class Walk_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.particle_timer = 0

    def update_state(self):
        self.particle_timer -= self.entity.game_objects.game.dt
        if self.particle_timer < 0:
            self.running_particles()

        if not self.entity.collision_types['bottom']:#disable this one while on ramp
            self.enter_state('Fall_run_pre')

    def running_particles(self):
        particle = self.entity.running_particles(self.entity.hitbox.midbottom,self.entity.game_objects)
        self.entity.game_objects.cosmetics.add(particle)
        self.particle_timer = 10

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='a':
            self.enter_state('Jump_run_pre')
        elif input[-1]=='lb':
            self.enter_state('Dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':#depends on if the abillities have pre or main animation
            self.do_ability()

    def handle_movement(self,input):
        super().handle_movement(input)
        if self.entity.acceleration[0]==0:
            self.enter_state('Idle_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if abs(self.entity.dir[1])<0.8:
                state='Sword_run'+str(int(self.entity.sword_swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword_swing = not self.entity.sword_swing
            elif self.entity.dir[1]>0.8:
                self.enter_state('Sword_up_pre')

class Jump_stand_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.entity.velocity[1] > 0.7:#when you start falling
            self.enter_state('Fall_stand_pre')
        elif self.entity.acceleration[0] != 0:#if you start moving
            self.enter_state('Jump_run_main')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='lb':
            self.enter_state('Dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.do_ability()

    def handle_release_input(self,input):#when release space
        super().handle_release_input(input)
        if input[-1]=='a':
            if self.entity.acceleration[0]==0:
                self.enter_state('Fall_stand')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]>0:
                self.enter_state('Sword_up_pre')
            elif self.entity.dir[1]<0:
                self.enter_state('Sword_down_main')
            else:#right or left
                state='Air_sword'+str(int(self.entity.sword_swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword_swing = not self.entity.sword_swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Jump_stand_main')

class Jump_stand_main(Jump_stand_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Jump_run_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        if self.entity.velocity[1] > 0:
            self.enter_state('Fall_run_pre')
        elif self.entity.acceleration[0] == 0:
            self.enter_state('Jump_stand_main')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='lb':
            self.enter_state('Dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='b':
            self.do_ability()

    def handle_release_input(self,input):#when release space
        super().handle_release_input(input)
        if input[-1]=='a':
            if self.entity.acceleration[0]!=0:
                self.enter_state('Fall_run')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]>0:
                self.enter_state('Sword_up_pre')
            elif self.entity.dir[1]<0:
                self.enter_state('Sword_down_main')
            else:#right or left
                state='Air_sword'+str(int(self.entity.sword_swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword_swing = not self.entity.sword_swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Jump_run_main')

class Jump_run_main(Jump_run_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Double_jump_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()

    def init(self):
        self.entity.velocity[1]=-10

    def update_state(self):
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
        self.entity.velocity[1] = 1#so that the falling from platform looks natural, 0 looks strange

    def update_state(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Fall_stand_main')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='b':
            self.do_ability()
        elif input[-1]=='lb':
            self.enter_state('Dash_pre')
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='a':
            self.enter_state('Double_jump_pre')

    def handle_input(self,input):
        if input == 'Wall':
            self.enter_state('Wall_glide_main')
        elif input == 'Ground':
            self.enter_state('Walk_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]>0:
                self.enter_state('Sword_up_pre')
            elif self.entity.dir[1]<0:
                self.enter_state('Sword_down_main')
            else:#right or left
                state='Air_sword'+str(int(self.entity.sword_swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword_swing = not self.entity.sword_swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Fall_run_main')

class Fall_run_main(Fall_run_pre):
    def __init__(self,entity):
        super().__init__(entity)

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
        self.entity.velocity[1] = 1#so that the falling from platform looks natural, 0 looks strange

    def update_state(self):
        if self.entity.acceleration[0] != 0:
            self.enter_state('Fall_run_main')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1]=='b':
            self.do_ability()
        elif input[-1]=='x':
            self.swing_sword()
        elif input[-1]=='lb':
            self.enter_state('Dash_pre')
        elif input[-1]=='a':
            self.enter_state('Double_jump_pre')

    def handle_input(self,input):
        if input == 'Ground':
            self.enter_state('Idle_main')

    def swing_sword(self):
        if not self.entity.sword_swinging:
            if self.entity.dir[1]==1:
                self.enter_state('Sword_up_pre')
            elif self.entity.dir[1]==-1:
                self.enter_state('Sword_down_main')
            else:#right or left
                state='Air_sword'+str(int(self.entity.sword_swing)+1)+'_main'
                self.enter_state(state)
                self.entity.sword_swing = not self.entity.sword_swing

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Fall_stand_main')

class Fall_stand_main(Fall_stand_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def init(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Wall_glide_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.friction[1] = 0.4
        self.entity.ground = True#so that we can jump

    def update_state(self):
        if not self.entity.collision_types['right'] and not self.entity.collision_types['left']:#non wall and not on ground
            self.enter_state('Fall_stand_pre')

    def handle_press_input(self,input):
        super().handle_press_input(input)
        if input[-1] == 'a':
            self.entity.velocity[0] = -self.dir[0]*10
            self.enter_state('Jump_run_main')
        elif input[-1] == 'right' or input[-1] == 'left':
            self.entity.velocity[0] = self.entity.dir[0]*2
            self.enter_state('Fall_run_pre')

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1] == 'right' or input[-1] == 'left':
            self.entity.velocity[0] = -self.entity.dir[0]*2
            self.enter_state('Fall_stand_pre')

    def handle_input(self,input):#when hit the ground
        if input == 'Ground':
            self.enter_state('Walk_main')

    def enter_state(self,input):#reset friction before exiting this state
        self.entity.friction[1] = C.friction_player[1]
        super().enter_state(input)

class Dash_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()

    def update_state(self):
        self.entity.velocity[1] = 0
        self.entity.velocity[0] = self.dir[0]*max(10,abs(self.entity.velocity[0]))#max horizontal speed

    def handle_press_input(self,input):
        if input[-1]=='x':
            self.enter_state('Dash_attack_main')

    def handle_input(self,input):#if hit wall
        if input == 'Wall':
            if self.entity.acceleration[0]!=0:
                self.enter_state('Wall_glide_main')
            else:
                self.enter_state('Idle_main')

    def increase_phase(self):
        self.enter_state('Dash_main')

class Dash_main(Dash_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.velocity[0] = 20*self.dir[0]
        self.entity.consume_spirit(self.entity.movement_abilities.abilities_dict['Dash'].dash_cost)
        self.counter = 4#within how many frames you can press x to enter attack

    def update_state(self):
        super().update_state()
        self.counter -= self.entity.game_objects.game.dt

    def handle_press_input(self,input):
        if input[-1]=='x' and self.counter > 0:#if pressed within three frames
            self.enter_state('Dash_attack_main')

    def increase_phase(self):
        self.enter_state('Dash_post')

class Dash_post(Dash_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_press_input(self,input):
        pass

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Walk_main')

class Dash_attack_main(Player_states):#enters from pre dash
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()

        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.sword.dir[1] = 0
        self.entity.sword.dir = self.dir.copy()#sword direction
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase

    def update_state(self):
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
        self.entity.velocity[1]=-3
        if self.entity.velocity[0]<0:
            self.dir[0]=1
        else:
            self.dir[0]=-1

    def update_state(self):
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

    def update_state(self):
        self.entity.invincibile = True

    def handle_movement(self,input):
        pass

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def handle_input(self,input):
        if input == 'Ground':#if hit ground
            self.enter_state('Death_main')

class Death_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.entity.invincibile = True

    def handle_movement(self,input):
        pass

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def increase_phase(self):
        self.entity.dead()
        self.enter_state('Death_post')

class Death_post(Player_states):
    def __init__(self,entity):
        super().__init__(entity)

    def update_state(self):
        self.entity.invincibile = True

    def handle_movement(self,input):
        pass

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def increase_phase(self):
        pass

class Invisible_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.stay_still()

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def handle_movement(self,input):
        pass

class Hurt_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.next_state = 'Idle_main'

    def increase_phase(self):
        self.enter_state(self.next_state)

    def update_state(self):
        if self.entity.acceleration[0] == 0:
            self.next_state = 'Idle_main'
        else:
            self.next_state ='Walk_main'

class Spawn_main(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.invincibile = False

    def handle_press_input(self,input):#all states should inehrent this function
        pass

    def handle_release_input(self,input):#all states should inehrent this function
        pass

    def handle_movement(self,input):
        pass

    def increase_phase(self):
        self.entity.health = max(self.entity.health,0)#if negative, set it to 0
        self.entity.heal(self.entity.max_health)
        self.enter_state('Idle_main')

class Sword(Player_states):#main phases shold inheret this
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.timer_jobs['sword'].activate()
        self.dir = self.entity.dir.copy()#animation direction
        self.entity.sword.dir = self.dir.copy()#sword direction
        sound.Sound.play_sfx(self.entity.sfx_sword)
        self.slash_speed()

    def slash_speed(self):#if we have green infinity stone
        if self.entity.sword.equip=='green':
            self.entity.animation.framerate = 0.33

    def enter_state(self,input):
        self.entity.animation.framerate = C.animation_framerate
        super().enter_state(input)

class Sword_stand1_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase
        self.entity.sword.dir[1]=0

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Walk_main')

class Sword_stand2_main(Sword_stand1_main):
    def __init__(self,entity):
        super().__init__(entity)

class Sword_run1_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.dir[1]=0

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Walk_main')

class Sword_run2_main(Sword_run1_main):
    def __init__(self,entity):
        super().__init__(entity)

class Air_sword1_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.dir[1]=0

    def increase_phase(self):
        if self.entity.acceleration[0]==0:
            self.enter_state('Fall_stand_main')
        else:
            self.enter_state('Fall_run_main')

class Air_sword2_main(Air_sword1_main):
    def __init__(self,entity):
        super().__init__(entity)

class Sword_up_pre(Player_states):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = self.entity.dir.copy()#animation direction

    def slash_speed(self):#if we have green infinity stone
        if self.entity.sword.equip=='green':
            self.entity.animation.framerate = 3

    def enter_state(self,input):
        self.entity.animation.framerate = 4
        super().enter_state(input)

    def increase_phase(self):
        self.enter_state('Sword_up_main')

class Sword_up_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime = 10#swrod hitbox duration
        self.entity.projectiles.add(self.entity.sword)#add sword to group
        self.entity.sword.dir[1]=1

    def increase_phase(self):
        self.enter_state('Idle_main')

class Sword_down_main(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.sword.lifetime=10
        self.entity.projectiles.add(self.entity.sword)#add sword to group but in main phase
        self.entity.sword.dir[1]=-1

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
        self.stay_still()
        self.dir = self.entity.dir.copy()#animation direction

class Thunder_pre(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.init()

    def init(self):
        self.entity.thunder_aura = Entities.Thunder_aura(self.entity)
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

    def init(self):
        self.entity.consume_spirit()

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1]=='b':#when release the botton
            self.attack()
            self.enter_state('Thunder_main')

    def attack(self):
        self.entity.thunder_aura.currentstate.handle_input('Death')

        collision_ene = self.entity.game_objects.collisions.thunder_attack(self.entity.thunder_aura)
        if collision_ene:
            for enemy in collision_ene:
                self.entity.abilities['Thunder'].initiate(enemy.rect)
                self.entity.projectiles.add(self.entity.abilities['Thunder'])#add attack to group

    def increase_phase(self):#called when an animation is finihed for that state
        pass

class Thunder_main(Thunder_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def init(self):
        pass

    def update_state(self):
        pass

    def increase_phase(self):#called when an animation is finihed for that state
        self.enter_state('Idle_main')

class Force_main(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities['Force'].initiate()
        self.entity.projectiles.add(self.entity.abilities['Force'])#add force to group
        self.force_jump()

    def increase_phase(self):
        if self.entity.acceleration[0] == 0:
            self.enter_state('Idle_main')
        else:
            self.enter_state('Walk_main')

    def force_jump(self):
        if self.dir[1]<0:
            self.entity.velocity[1] = -10

class Heal_pre(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_release_input(self,input):
        super().handle_release_input(input)
        if input[-1]=='b':#when release the botton
            self.enter_state('Idle_main')

    def increase_phase(self):
        self.enter_state('Heal_main')

class Heal_main(Heal_pre):
    def __init__(self,entity):
        super().__init__(entity)

    def handle_release_input(self,input):
        pass

    def increase_phase(self):
        self.entity.heal()
        self.entity.consume_spirit()
        self.enter_state('Idle_main')

class Darksaber_pre(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)

    def increase_phase(self):
        self.enter_state('Darksaber_main')

class Darksaber_main(Darksaber_pre):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.abilities['Darksaber'].initiate()
        self.entity.projectiles.add(self.entity.abilities['Darksaber'])#add sword to group

    def increase_phase(self):
        self.enter_state('Idle_main')

class Arrow_main(Abillitites):
    def __init__(self,entity):
        super().__init__(entity)
        self.entity.consume_spirit()
        self.entity.abilities['Arrow'].initiate()
        self.entity.projectiles.add(self.entity.abilities['Arrow'])#add sword to group

    def increase_phase(self):
        self.enter_state('Idle_main')
