import pygame
import Entities, states_time_collision, animation, Read_files
import constants as C

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self,pos,size = (16,16)):
        super().__init__()
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.hitbox = self.rect.inflate(0,0)

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        pass

    def draw(self):
        pass

class Collision_block(Platform):
    def __init__(self, pos, size, run_particle):
        super().__init__(pos,size)
        self.run_particles = {'dust':Entities.Dust_running_particles,'water':Entities.Water_running_particles,'grass':Entities.Grass_running_particles}[run_particle]
        self.go_through = False

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self.hitbox.left)
        else:#going to the leftx
            entity.left_collision(self.hitbox.right)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] >= 0:#going down
            entity.down_collision(self.hitbox.top)
            entity.limit_y()
            entity.running_particles = self.run_particles#save the particles to make
        else:#going up
            entity.top_collision(self.hitbox.bottom)
        entity.update_rect_y()

class Collision_oneway_up(Platform):
    def __init__(self, pos, size, run_particle = 'dust', go_through = True):
        super().__init__(pos,size)
        self.run_particles = {'dust':Entities.Dust_running_particles,'water':Entities.Water_running_particles,'grass':Entities.Grass_running_particles}[run_particle]
        self.go_through = go_through

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        if entity.velocity[1] < 0: return#going up
        if entity.go_through: return
        offset = entity.velocity[1] + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            entity.down_collision(self.hitbox.top)
            entity.limit_y()
            entity.running_particles = self.run_particles#save the particles to make
            entity.update_rect_y()
        else:#going up
            pass

class Collision_right_angle(Platform):
    def __init__(self, pos, points, go_through = True):
        self.define_values(pos, points)
        super().__init__([self.new_pos[0],self.new_pos[1]-self.size[1]],self.size)
        self.ratio = self.size[1]/self.size[0]
        self.go_through = go_through
        self.target = 0
    #function calculates size, real bottomleft position and orientation of right angle triangle
    #the value in orientatiion represents the following:
    #0 = tilting to the right, flatside down
    #1 = tilting to the left, flatside down
    #2 = tilting to the right, flatside up
    #3 = tilting to the left, flatside up

    def define_values(self, pos, points):
        self.new_pos = (0,0)
        self.size = (0,0)
        self.orientation = 0
        x_0_count = 0
        y_0_count = 0
        x_extreme = 0
        y_extreme = 0

        for point in points:
            if point[0] == 0:
                x_0_count += 1
            else:
                x_extreme = point[0]
            if point[1] == 0:
                y_0_count += 1
            else:
                y_extreme = point[1]

        self.size = (abs(x_extreme), abs(y_extreme))

        if x_extreme < 0:
            if y_extreme < 0:
                self.new_pos = (pos[0] + x_extreme, pos[1])
                if x_0_count == 1:
                    self.orientation = 0
                elif y_0_count == 1:
                    self.orientation = 3
                else:
                    self.orientation = 1

            else:
                self.new_pos = (pos[0] + x_extreme, pos[1] + y_extreme)
                if x_0_count == 1:
                    self.orientation = 2
                elif y_0_count == 1:
                    self.orientation = 1
                else:
                    self.orientation = 3

        else:
            if y_extreme < 0:
                self.new_pos = pos
                if x_0_count == 1:
                    self.orientation = 1
                elif y_0_count == 1:
                    self.orientation = 2
                else:
                    self.orientation = 0

            else:
                self.new_pos = (pos[0], pos[1] + y_extreme)
                if x_0_count == 1:
                    self.orientation = 3
                elif y_0_count == 1:
                    self.orientation = 0
                else:
                    self.orientation = 2

    def collide(self,entity):#called through update
        if self.orientation == 1:
            rel_x = entity.hitbox.right - self.hitbox.left
            other_side = entity.hitbox.right - self.hitbox.right
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.target = -rel_x*self.ratio + self.hitbox.bottom
            self.shift_up(other_side,entity,benethe)
        elif self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
            other_side = self.hitbox.left - entity.hitbox.left
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.target = -rel_x*self.ratio + self.hitbox.bottom
            self.shift_up(other_side,entity,benethe)
        elif self.orientation == 2:
            rel_x = self.hitbox.right - entity.hitbox.left
            self.target = rel_x*self.ratio + self.hitbox.top
            self.shift_down(entity)
        else:#orientation 3
            rel_x = entity.hitbox.right - self.hitbox.left
            self.target = rel_x*self.ratio + self.hitbox.top
            self.shift_down(entity)

    def shift_down(self,entity):
        if entity.hitbox.top < self.target:
            entity.top_collision(self.target)
            entity.velocity[1] = 2#need to have a value to avoid "dragin in air" while running
            entity.velocity[0] = 0#need to have a value to avoid "dragin in air" while running
            entity.update_rect_y()

    def shift_up(self,other_side,entity,benethe):
        if self.target > entity.hitbox.bottom:
            entity.go_through = False
        elif other_side > 0 or benethe > 0:
            entity.go_through = True
        elif not entity.go_through:
            entity.velocity[1] = C.max_vel[1]#make aila sticj to ground to avoid falling animation
            entity.down_collision(self.target)
            entity.update_rect_y()

class Collision_dmg(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.dmg = 1

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self.hitbox.left)
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.left_collision(self.hitbox.right)
            entity.velocity[0] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self.hitbox.top)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self.hitbox.bottom)
            entity.velocity[1] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect_y()

class Collision_time(Collision_oneway_up):#collision block that dissapears if aila stands on it
    def __init__(self,game_objects,pos,size,run_particle,go_through=True):
        super().__init__(pos,size,run_particle,go_through)
        self.game_objects = game_objects
        self.timers = []
        self.timer_jobs = {'timer_disappear':Platform_timer_1(self,60),'timer_appear':Platform_timer_2(self,60)}#these timers are activated when promt and a job is appeneded to self.timer.
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_time_collision.Idle(self)#

    def deactivate(self):
        self.hitbox = [self.hitbox[0],self.hitbox[1],0,0]
        self.timer_jobs['timer_appear'].activate()
        self.currentstate.handle_input('Transition_1')

    def activate(self):#when it shoudl dissapear
        self.hitbox = self.rect.inflate(0,0)
        self.currentstate.handle_input('Transition_2')

    def update(self):
        self.animation.update()
        self.update_timers()

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def collide_y(self,entity):
        if entity.velocity[1] < 0: return#going up
        if entity.go_through: return
        offset = entity.velocity[1] + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            self.timer_jobs['timer_disappear'].activate()
            entity.down_collision(self.hitbox.top)
            entity.limit_y()
            entity.running_particles = self.run_particles#save the particles to make
            entity.update_rect_y()

    def draw(self):
        self.game_objects.game.screen.blit(self.image, (round(self.true_pos[0]-self.game_objects.camera.true_scroll[0]),round(self.true_pos[1]-self.game_objects.camera.true_scroll[1])))#round seem nicer than int

class Rhoutta_encounter_1(Collision_time):
    def __init__(self,game_objects,pos,size,run_particle,go_through=True):
        super().__init__(game_objects,pos,size,run_particle,go_through)
        self.sprites = Read_files.Sprites_Player('Sprites/block/collision_time/rhoutta_encounter_1/')
        self.image = self.sprites.sprite_dict['idle'][0]

#timer:
class Platform_timer_1(Entities.Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def deactivate(self):#when timer runs out
        super().deactivate()
        self.entity.deactivate()

class Platform_timer_2(Entities.Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def deactivate(self):#when timer runs out
        super().deactivate()
        self.entity.activate()