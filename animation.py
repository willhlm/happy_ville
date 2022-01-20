import pygame

class Animation():

    def __init__(self,entity):
        self.entity=entity
        self.framerate=4
        self.frame=0

    def enter_state(self):
        self.entity.animation_stack.append(self)

    def exit_state(self):
        self.entity.animation_stack.pop()
        self.entity.animation_stack[-1].frame=self.frame#send back the frame number

    def reset_timer(self):
        self.frame=0

class Entity_animation(Animation):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        #if str(type(self.entity).__name__)=='Player':        
        self.entity.image = self.entity.sprites.get_image(self.entity.currentstate.state_name,self.frame//self.framerate,self.entity.currentstate.dir,self.entity.currentstate.phase).copy()
        self.frame += 1

        if self.frame == self.entity.sprites.get_frame_number(self.entity.currentstate.state_name,self.entity.currentstate.phase)*self.framerate:
            self.reset_timer()
            self.entity.currentstate.increase_phase()

class Hurt_animation(Entity_animation):#become white
    def __init__(self,entity):
        super().__init__(entity)
        self.duration=15
        self.frame=entity.animation_stack[0].frame#set the initial frame

    def update(self):
        super().update()

        self.entity.image.fill((250,250,250),special_flags=pygame.BLEND_ADD)
        self.duration -=1

        if self.duration<0:
            self.exit_state()

class Basic_animation(Animation):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.image = self.entity.sprites[self.entity.state][self.frame//self.framerate].copy()
        self.frame += 1

        if self.frame == len(self.entity.sprites[self.entity.state])*self.framerate:
            self.reset_timer()

class Ability_animation(Basic_animation):
    def __init__(self,entity):
        super().__init__(entity)

    def reset_timer(self):
        super().reset_timer()
        if self.entity.state=='post':
            self.entity.kill()#kill the object after post animation
