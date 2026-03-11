from gameplay.entities.base.animated_entity import AnimatedEntity
from engine import constants as C
from gameplay.entities.shared.components.hitstop_component import HitstopComponent

class PlatformEntity(AnimatedEntity):#Things to collide with platforms
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = {'ramp': True, 'one_way':True}#a flag for entities to go through ramps from side or top
        self.velocity = [0, 0]
        self.hitstop = HitstopComponent()

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

    def update_true_pos_x(self, dt):#called from Engine.platform collision. The velocity to true pos need to be set in collision if group distance should work proerly for enemies (so that the velocity is not applied when removing the sprite from gorup)    
        self.true_pos[0] += dt * self.velocity[0]
        self.rect.left = round(self.true_pos[0])#should be int -> round fixes gliding on bubble
        self.update_hitbox()

    def update_true_pos_y(self, dt):#called from Engine.platform collision
        self.true_pos[1] += dt * self.velocity[1]
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
        self.currentstate.handle_input('ceiling')

    def limit_y(self):#limits the velocity on ground, onewayup. But not on ramps to make a smooth drop
        self.velocity[1] = 1.2#assume at least 60 fps -> 1 