import pygame
import constants as C
import math

class Animation():
    def __init__(self,entity):
        self.entity=entity
        self.framerate = 4#depends on FPS
        self.frame = 0

    def enter_state(self):
        self.entity.animation_stack.append(self)

    def exit_state(self):
        self.entity.animation_stack.pop()
        self.entity.animation_stack[-1].frame = self.frame#send back the frame number

    def reset_timer(self):
        self.frame=0

class Entity_animation(Animation):#phase and state
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.image = self.entity.sprites.get_image(self.entity.currentstate.state_name,self.frame//self.framerate,self.entity.currentstate.dir,self.entity.currentstate.phase).copy()
        self.frame += 1
    #    if str(type(self.entity).__name__)=='Wall_slime':
    #        pass#print(self.entity.currentstate.dir)

        if self.frame == self.entity.sprites.get_frame_number(self.entity.currentstate.state_name,self.entity.currentstate.phase)*self.framerate:
            self.reset_timer()
            self.entity.currentstate.increase_phase()

    def handle_input(self,input):
        if input=='Hurt':
            Hurt_animation(self.entity).enter_state()
        elif input == 'Invincibile':
            Invincibile_animation(self.entity).enter_state()

class Hurt_animation(Entity_animation):#become white
    def __init__(self,entity):
        super().__init__(entity)
        self.duration = C.hurt_animation_length#hurt animation duration
        self.frame=entity.animation_stack[0].frame#set the initial frame

    def update(self):
        super().update()
        self.entity.image.fill((250,250,250),special_flags=pygame.BLEND_ADD)
        self.duration -= 1

        if self.duration<0:
            self.exit_state()

    def handle_input(self,input):
        pass

class Invincibile_animation(Entity_animation):
    def __init__(self,entity):
        super().__init__(entity)
        self.duration = C.invincibility_time_player-(C.hurt_animation_length+1)
        self.time = 0

    def update(self):
        super().update()
        colour=[int(0.5*255*math.sin(self.time)+255*0.5),int(0.5*255*math.sin(self.time)+255*0.5),int(0.5*255*math.sin(self.time)+255*0.5)]
        self.entity.image.fill(colour,special_flags=pygame.BLEND_ADD)
        self.duration -= 1
        self.time += 0.5

        if self.duration<0:
            self.exit_state()

    def handle_input(self,input):
        if input=='Hurt':
            Hurt_animation(self.entity).enter_state()

class Basic_animation(Animation):#state
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.image = self.entity.sprites[self.entity.state][self.frame//self.framerate].copy()
        self.frame += 1

        if self.frame == len(self.entity.sprites[self.entity.state])*self.framerate:
            self.reset_timer()
            self.entity.reset_timer()

class Simple_animation(Animation):#no state or phase
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.image = self.entity.sprites[self.frame//self.framerate].copy()
        self.frame += 1

        if self.frame == len(self.entity.sprites)*self.framerate:
            self.reset_timer()
            self.entity.reset_timer()
