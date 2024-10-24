import pygame
import entities, states_time_collision, animation, read_files, states_basic, states_gate, states_smacker
import constants as C

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self, pos, size = (16,16)):
        super().__init__()
        self.rect = pygame.Rect(pos, size)
        self.rect.topleft = pos
        self.true_pos = list(self.rect.topleft)
        self.hitbox = self.rect.copy()

    def collide_x(self, entity):
        pass

    def collide_y(self, entity):
        pass

    def draw(self, target):#conly certain platforms will require draw
        pass

    def take_dmg(self, projectile):#called from projectile
        pass   

    def release_texture(self):#called when .kill() and empty group
        pass   

    def kill(self):
        self.release_texture()#before killing, need to release the textures (but not the onces who has a pool)
        super().kill()         

class Collision_block(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos, size)
        self.run_particles = {'dust':entities.Dust_running_particles,'water':entities.Water_running_particles,'grass':entities.Grass_running_particles}[run_particle]

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down   
            entity.down_collision(self)
            entity.limit_y()
            entity.running_particles = self.run_particles#save the particles to make
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

class Collision_oneway_up(Platform):
    def __init__(self, pos, size, run_particle = 'dust'):
        super().__init__(pos,size)
        self.run_particles = {'dust':entities.Dust_running_particles,'water':entities.Water_running_particles,'grass':entities.Grass_running_particles}[run_particle]

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        if entity.velocity[1] < 0: return#going up
        offset = entity.velocity[1] + abs(entity.velocity[0]) + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:
            entity.down_collision(self)
            entity.limit_y()
            entity.running_particles = self.run_particles#save the particles to make
            entity.update_rect_y()

class Collision_right_angle(Platform):#ramp
    def __init__(self, pos, points, go_through = True):
        self.define_values(pos, points)
        super().__init__([self.new_pos[0],self.new_pos[1]-self.size[1]],self.size)
        self.ratio = self.size[1]/self.size[0]
        self.go_through = go_through#a flag that determines if aila can go through when pressing down
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

    def get_target(self,entity):#called when oresing down
        if self.orientation == 1:
            rel_x = entity.hitbox.right - self.hitbox.left
        elif self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
        else: return 0
        return -rel_x*self.ratio + self.hitbox.bottom

    def collide(self, entity):#called in collisions        
        if self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
            other_side = self.hitbox.left - entity.hitbox.left
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.target = -rel_x*self.ratio + self.hitbox.bottom 
            self.shift_up(other_side, entity, benethe)    
        elif self.orientation == 1:
            rel_x = entity.hitbox.right - self.hitbox.left
            other_side = entity.hitbox.right - self.hitbox.right
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.target = -rel_x*self.ratio + self.hitbox.bottom 
            self.shift_up(other_side, entity, benethe)
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
            entity.ramp_top_collision(self.target)
            entity.update_rect_y()

    def shift_up(self, other_side, entity, benethe):   
        if self.target > entity.hitbox.bottom:
            entity.go_through['ramp'] = False        
        elif other_side > 0 or benethe > 0:
            entity.go_through['ramp'] = True       
        elif not entity.go_through['ramp']: #need to be elif
            entity.ramp_down_collision(self.target)
            entity.update_rect_y()    

class Collision_dmg(Platform):#"spikes"
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.dmg = 1

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self)
            entity.velocity[0] = -10#knock back
        else:#going to the left
            entity.left_collision(self)
            entity.velocity[0] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self)
            entity.velocity[1] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect_y()

#texture based
class Collision_texture(Platform):#blocks that has tectures
    def __init__(self, pos, game_objects):
        super().__init__(pos)    
        self.game_objects = game_objects        
        self.dir = [1,0]#animation needs it

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down   
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

    def reset_timer(self):#aniamtion need it
        self.currentstate.increase_phase()

    def release_texture(self):#called when .kill() and empty group
        for state in self.sprites.keys():
            for frame in range(0,len(self.sprites[state])):
                self.sprites[state][frame].release()

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, position = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])))#int seem nicer than round         

class Boulder(Collision_texture):#blocks village cave
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/boulder/', game_objects)

        if game_objects.world_state.events.get('reindeer', False):#if reindeer has been deafeated
            state = 'down'
        else:
            state = 'erect'

        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

class Gate_1(Collision_texture):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.init()

        self.ID_key = kwarg.get('ID', 'None')#an ID to match with the gate
        if game_objects.world_state.quests.get(self.ID_key[:self.ID_key.rfind('_')], False):#if quest accodicated with it has been completed
            state = 'down'
        elif game_objects.world_state.events.get(self.ID_key[:self.ID_key.rfind('_')], False):#if the event has been completed
            state = 'down'
        else:                
            state = {True: 'erect', False: 'down'}[kwarg.get('erect', False)]#a flag that can be specified in titled   
        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width,self.image.height)#hitbox is set in state                
                
        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/animations/gate_1/', self.game_objects)

class Gate_2(Gate_1):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects, **kwarg)

    def init(self):
        self.sprites = read_files.load_sprites_dict('Sprites/animations/gate_2/', self.game_objects)        

class Bridge(Collision_texture):#bridge twoards forest path
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/bridge/', game_objects)

        if game_objects.world_state.events.get('reindeer', False):#if reindeer has been deafeated
            state = 'erect'
        else:
            state = 'down'

        self.image = self.sprites[state][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.animation = animation.Animation(self)
        self.currentstate = {'erect': states_gate.Erect, 'down': states_gate.Down}[state](self)

class Conveyor_belt(Collision_texture):
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, game_objects)
        self.tile_size = [16,16]
        
        if kwarg.get('vertical', False):#default is horizontal belft
            angle = 90              
            size[1] = max(size[1], self.tile_size[1] * 3)#assert at least 3 tiles
            if kwarg.get('up', False):#default is up down betls
                self.direction = [0, -1]
            else:#down
                self.direction = [0, 1]      
            animation_direction =  self.direction[1]                          
        else:#horizontal
            angle = 0             
            size[0] = max(size[0], self.tile_size[0] * 3)#assert at least 3 tiles
            if kwarg.get('right', False):#default is left moving belts
                self.direction = [1,0]
            else:#left
                self.direction = [-1, 0]
            animation_direction =  -self.direction[0]                 
        
        #self.timer = Conveyor_belt_timer(self, 10, self.direction)
        #self.timers = []

        self.make_belt(size, angle)
        self.animation = animation.Animation(self, direction = animation_direction)#can revert the animation direction
        self.currentstate = states_basic.Idle(self)     

        self.rect = pygame.Rect(pos, size)    
        self.true_pos = list(self.rect.topleft)
        if angle == 0:
            self.hitbox = pygame.Rect(pos[0], pos[1], (self.rect[2] - 16), self.rect[3] * 0.55)
        else:
            self.hitbox = pygame.Rect(pos[0], pos[1], (self.rect[2]) * 0.55, (self.rect[3]-16))
        self.hitbox.center = self.rect.center

    #def update(self):
    #    super().update()
        #for timer in self.timers:
        #    timer.update()

    def make_belt(self, size, angle = 0):#the spits are divided into left, middle and right. Merge them here                
        sprites = read_files.load_sprites_dict('Sprites/block/conveyor_belt/', self.game_objects)

        self.sprites = {'idle' : []}
        self.layers = []#store each layer so that it can be released
        principle_sections = ['left', 'middle','right']#the middle will be placed multiple times depending on the size     

        if angle == 0:
            sections = [principle_sections[0]] + [principle_sections[1]] * (int(size[0]/self.tile_size[0]) - 2) + [principle_sections[2]]
        else:#90
            sections = [principle_sections[0]] + [principle_sections[1]] * (int(size[1]/self.tile_size[1]) - 2) + [principle_sections[2]]

        for frame in range(0, len(sprites[sections[0]]) - 1):  
            self.layers.append(self.game_objects.game.display.make_layer(size))
            for index, section in enumerate(sections):
                if angle == 0:
                    pos = [sprites[sections[index - 1]][frame].width * index , 0]
                else:#vertical
                    pos = [0, sprites[sections[index - 1]][frame].height * index ]

                self.game_objects.game.display.render(sprites[section][frame], self.layers[-1], position = pos, angle = angle)#int seem nicer than round         

            self.sprites['idle'].append(self.layers[-1].texture)            
        self.image =  self.sprites['idle'][0]      

        for state in sprites.keys():
            for frame in range(0,len(sprites[state])):
                sprites[state][frame].release()   

    def release_texture(self):
        super().release_texture()
        for layer in self.layers:
            layer.release()

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self, 'belt')
            entity.velocity[1] += self.game_objects.game.dt * self.direction[1]
        else:#going to the leftx
            entity.left_collision(self, 'belt')
            entity.velocity[1] += self.game_objects.game.dt * -self.direction[1]
        entity.update_rect_x()
 
    def collide_y(self,entity):
        super().collide_y(entity)
        entity.velocity[0] += self.game_objects.game.dt * self.direction[0]
        #self.timer.activate(entity)

#timer based
class Collision_timer(Collision_texture):#collision block that dissapears if aila stands on it
    def __init__(self, pos, game_objects):        
        super().__init__(pos, game_objects)
        self.timers = []
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_time_collision.Idle(self)#

    def update(self):
        super().update()
        self.update_timers()

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):#called when aila lands on platoform
        if entity.velocity[1] < 0: return#going up
        offset = entity.velocity[1] + 1
        if entity.hitbox.bottom <= self.hitbox.top + offset:            
            self.timer_jobs['timer_disappear'].activate()
            entity.down_collision(self)
            entity.limit_y()
            entity.running_particles = self.run_particles#save the particles to make
            entity.update_rect_y()

class Rhoutta_encounter_1(Collision_timer):
    def __init__(self, game_objects, pos, particle):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/rhoutta_encounter_1/',game_objects)
        self.image = self.sprites['idle'][0]
        self.timer_jobs = {'timer_disappear': Timer(self, 60, self.deactivate),'timer_appear': Timer(self, 60, self.activate)}#these timers are activated when promt and a job is appeneded to self.timer.
        self.run_particles = entities.Dust_running_particles
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()

    def deactivate(self):#called when timer_disappear runs out
        self.hitbox = [self.hitbox[0], self.hitbox[1], 0, 0]
        self.timer_jobs['timer_appear'].activate()
        self.currentstate.handle_input('Transition_1')

    def activate(self):#called when timer_appear runs out
        self.hitbox = self.rect.inflate(0,0)
        self.currentstate.handle_input('Transition_2')

class Crystal_mines_1(Collision_timer):
    def __init__(self, game_objects, pos):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/crystal_mines_1/',game_objects)
        self.image = self.sprites['idle'][0]
        self.timer_jobs = {'timer_disappear': Timer(self, 60, self.deactivate),'timer_appear': Timer(self, 60, self.activate)}#these timers are activated when promt and a job is appeneded to self.timer.
        self.run_particles = entities.Dust_running_particles
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = pygame.Rect(pos[0], pos[1], self.rect[2], self.rect[3]*0.4)
        self.hitbox.center = self.rect.center

    def deactivate(self):#called when timer_disappear runs out
        self.hitbox[2], self.hitbox[3] = 0, 0
        self.timer_jobs['timer_appear'].activate()
        self.currentstate.handle_input('Transition_1')

    def activate(self):#called when timer_appear runs out
        self.hitbox[2], self.hitbox[3] = self.rect[2], self.rect[3]*0.4
        self.currentstate.handle_input('Transition_2')

class Bubble_static(Collision_timer):#static bubble
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/bubble/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()
        lifetime = prop.get('lifetime', 100)
        self.timer_jobs = {'timer_disappear':Platform_timer_1(self,lifetime), 'timer_appear':Platform_timer_2(self,lifetime)}#these timers are activated when promt and a job is appeneded to self.timer.              

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):                    
        if entity.velocity[1] > 0:#going down   
            self.timer_jobs['timer_disappear'].activate()            
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()     

    def deactivate(self):#called when first timer runs out          
        self.hitbox = [self.hitbox[0],self.hitbox[1],0,0]
        self.timer_jobs['timer_appear'].activate()
        self.currentstate.handle_input('Transition_1')

    def activate(self):
        self.hitbox = self.rect.inflate(0,0)
        self.currentstate.handle_input('Transition_2')

#breakable
class Collision_breakable(Collision_texture):#breakable collision blocks
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.timers = []#a list where timers are append whe applicable, e.g. jump, invincibility etc.
        self.timer_jobs = {'invincibility':entities.Invincibility_timer(self,C.invincibility_time_enemy)}
        self.health = 3
        self.invincibile = False
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_basic.Idle(self)#

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def dead(self):#called when death animatin finishes
        self.kill()

    def take_dmg(self, projectile):
        if self.invincibile: return
        self.health -= projectile.dmg
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
        projectile.clash_particles(self.hitbox.center)

        if self.health > 0:#check if dead¨
            self.animation.handle_input('Hurt')#turn white
            self.game_objects.camera_manager.camera_shake(3,10)
        else:#if dead
            if self.currentstate.state_name != 'death':#if not already dead
                self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
                self.currentstate.enter_state('Death')#overrite any state and go to deat

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Breakable_block_1(Collision_breakable):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/block/breakable/light_forest/type1/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()

#dynamics (moving) ones
class Collision_dynamic(Collision_texture):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.velocity = [0,0]

    def update(self):
        super().update()
        self.update_vel()

    def update_true_pos_x(self):
        self.true_pos[0] += self.game_objects.game.dt*self.velocity[0]
        self.rect.left = int(self.true_pos[0])#should be int
        self.hitbox.left = self.rect.left                

    def update_true_pos_y(self):
        self.true_pos[1] += self.game_objects.game.dt*self.velocity[1]
        self.rect.top = int(self.true_pos[1])#should be int
        self.hitbox.top = self.rect.top   

    def collide_x(self,entity):#entity moving
        if entity.velocity[0] > self.velocity[0]:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_entity_x(self,entity):  #platofmr miving          
        if self.velocity[0] > 0:#going to the right
            entity.left_collision(self)
        else:#going to the leftx
            entity.right_collision(self)
        entity.update_rect_x()

    def collide_entity_y(self,entity):  #platofmr miving                    
        if self.velocity[1] < 0:#going up              
            entity.down_collision(self)
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

    def collide_y(self,entity):  #entity moving                  
        if entity.velocity[1] > self.velocity[1]:#going down               
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

class Bubble(Collision_dynamic):#dynamic one: #shoudl be added to platforms and dynamic_platforms groups
    def __init__(self, pos, game_objects, **prop):
        super().__init__(pos, game_objects)
        self.sprites = Bubble.sprites
        self.timers = []
        self.image = self.sprites['idle'][0]
        self.rect[2], self.rect[3] = self.image.width, self.image.height
        self.hitbox = self.rect.copy()

        lifetime = prop.get('lifetime', 300)
        self.timer_jobs = {'timer_disappear':Platform_timer_1(self,lifetime)}#these timers are activated when promt and a job is appeneded to self.timer.      
        self.timer_jobs['timer_disappear'].activate()
        #TODO horitoxntal or veritcal moment
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_time_collision.Idle(self)#

    def update(self):
        super().update()
        self.update_timers()

    def update_timers(self):
        for timer in self.timers:
            timer.update()        

    def update_vel(self):
        self.velocity[1] -= self.game_objects.game.dt*0.01   

    def pool(game_objects):#all things that should be saved in object pool
        Bubble.sprites = read_files.load_sprites_dict('Sprites/block/collision_time/bubble/', game_objects)    

    def activate(self):
        pass

    def deactivate(self):#called when first timer runs out         
        self.kill()

class Smacker(Collision_dynamic):#trap
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('Sprites/animations/traps/smacker/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)
        self.hitbox = self.rect.copy()

        self.hole = kwarg.get('hole', None)
        
        self.frequency = int(kwarg.get('frequency', 100))#infinte -> idle - active
        self.distance = kwarg.get('distance', 4*16)
        self.original_pos = pos

        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Animation(self)
        self.currentstate = states_smacker.Idle(self)

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def collide_entity_y(self,entity):#plpaotfrom mobings  
        self.currentstate.collide_entity_y(entity)                

    def collide_y(self,entity):#entity moving       
        self.currentstate.collide_y(entity)        

#timers:
class Conveyor_belt_timer(entities.Timer):#not in use: if we want to make convyeor belt "jumps"
    def __init__(self, entity, duration, direction):
        super().__init__(entity, duration)
        self.direction = direction

    def activate(self, entity):#add timer to the entity timer list
        self.lifetime = self.duration
        self.entity = entity
        entity.friction[0] = 0.12
        if self in self.entity.timers: return#do not append if the timer is already inside        
        self.entity.timers.append(self)

    def update(self):
        super().update()
        self.entity.velocity[0] += self.entity.game_objects.game.dt * self.direction[0] * 0.5

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)
        self.entity.friction = C.friction_player.copy()#put it back

class Timer():
    def __init__(self, entity, duration, timeout):
        self.entity = entity
        self.duration = duration
        self.timeout = timeout

    def activate(self):#add timer to the entity timer list
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)
        self.timeout()

    def update(self):
        self.lifetime -= self.entity.game_objects.game.dt * self.entity.game_objects.player.slow_motion
        if self.lifetime < 0:
            self.deactivate()    
