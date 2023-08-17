import pygame, random, sys, math
import Read_files, states, particles, animation, sound, dialogue
import state_shade_screen, states_horn_vines, states_basic, states_camerastop, states_player, states_traps, states_NPC, states_enemy, states_vatt, states_mygga, states_reindeer, states_bluebird, states_kusa, states_rogue_cultist, states_sandrew
import AI_wall_slime, AI_vatt, AI_kusa, AI_exploding_mygga, AI_bluebird, AI_enemy, AI_reindeer
import constants as C

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self,pos,size = (16,16)):
        super().__init__()
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.true_pos = self.rect.topleft
        self.hitbox = self.rect.inflate(0,0)

class Collision_block(Platform):
    def __init__(self,pos,size, run_particle):
        super().__init__(pos,size)
        self.run_particles = {'dust':Dust_running_particles,'water':Water_running_particles,'grass':Grass_running_particles}[run_particle]

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
    def __init__(self,pos,size,run_particle = 'dust'):
        super().__init__(pos,size)
        self.run_particles = {'dust':Dust_running_particles,'water':Water_running_particles,'grass':Grass_running_particles}[run_particle]

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            offset = entity.velocity[1] + 1
            if entity.hitbox.bottom <= self.hitbox.top+offset:
                entity.down_collision(self.hitbox.top)
                entity.limit_y()
                entity.running_particles = self.run_particles#save the particles to make
                entity.update_rect_y()
        else:#going up
            pass

class Collision_right_angle(Platform):
    def __init__(self,pos,points,go_through=True):
        self.define_values(pos, points)
        super().__init__([self.new_pos[0],self.new_pos[1]-self.size[1]],self.size)
        self.ratio = self.size[1]/self.size[0]
        self.go_through = go_through
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

    def collide(self,entity):
        if self.orientation == 1:
            rel_x = entity.hitbox.right - self.hitbox.left
            other_side = entity.hitbox.right - self.hitbox.right
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.shift_up(rel_x,other_side,entity,benethe)
        elif self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
            other_side = self.hitbox.left - entity.hitbox.left
            benethe = entity.hitbox.bottom - self.hitbox.bottom
            self.shift_up(rel_x,other_side,entity,benethe)
        elif self.orientation == 2:
            rel_x = self.hitbox.right - entity.hitbox.left
            self.shift_down(rel_x,entity)
        else:#orientation 3
            rel_x = entity.hitbox.right - self.hitbox.left
            self.shift_down(rel_x,entity)

    def shift_down(self,rel_x,entity):
        target = rel_x*self.ratio + self.hitbox.top

        if entity.hitbox.top < target:
            entity.top_collision(target)
            entity.velocity[1] = 2 #need to have a value to avoid "dragin in air" while running
            entity.velocity[0] = 0 #need to have a value to avoid "dragin in air" while running
            entity.update_rect_y()

    def shift_up(self,rel_x,other_side,entity,benethe):
        target = -rel_x*self.ratio + self.hitbox.bottom

        if other_side > 0 or benethe > 0:
            if entity.hitbox.bottom > target:
                entity.go_through = True
            else:
                entity.go_through = False

        elif entity.hitbox.bottom < target:
                entity.go_through = False

        if not entity.go_through:
            if entity.hitbox.bottom > target:
                entity.down_collision(target)
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

class Staticentity(pygame.sprite.Sprite):#no hitbox but image
    def __init__(self,pos,img = pygame.Surface((16,16),pygame.SRCALPHA,32)):
        super().__init__()
        self.image = img.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.bounds = [-200,800,-100,350]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen
        self.true_pos = list(self.rect.topleft)
        self.parallax = [1,1]

    def group_distance(self):#instead of bound, could calculate distance from center.
        if self.true_pos[0]-self.parallax[0]*self.game_objects.camera.scroll[0] < self.bounds[0] or self.true_pos[0]-self.parallax[0]*self.game_objects.camera.scroll[0] > self.bounds[1] or self.true_pos[1]-self.parallax[1]*self.game_objects.camera.scroll[1]<self.bounds[2] or self.true_pos[1]-self.parallax[1]*self.game_objects.camera.scroll[1]>self.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause

class BG_Block(Staticentity):
    def __init__(self,pos,img,parallax = 1):
        super().__init__(pos,img)
        self.parallax = parallax

class BG_Animated(BG_Block):
    def __init__(self,game_objects,pos,sprite_folder_path,parallax=(1,1)):
        super().__init__(pos,pygame.Surface((16,16)),parallax)
        self.game_objects = game_objects#animation need it
        self.sprites = Read_files.load_sprites(sprite_folder_path)
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

    def update(self):
        self.animation.update()

    def reset_timer(self):
        pass

class Reflection(Staticentity):
    def __init__(self,pos,size,dir,game_objects, offset = 12):
        super().__init__(pos,pygame.Surface(size, pygame.SRCALPHA, 32))
        self.game_objects = game_objects
        self.size = size
        self.dir = dir
        self.offset = offset
        self.squeeze = 0.75
        self.reflect_rect = pygame.Rect(self.rect.left, self.rect.top, self.size[0], self.size[1])

    def draw(self):
        self.reflect_rect.center = [self.rect.center[0]- self.game_objects.camera.scroll[0],self.game_objects.game.screen.get_height() - self.rect.center[1]+ self.size[1]*self.squeeze + self.offset + self.game_objects.camera.scroll[1]]
        reflect_surface = self.game_objects.game.screen.copy()
        reflect_surface.convert_alpha()#do we need this?
        reflect_surface = pygame.transform.scale(reflect_surface, (reflect_surface.get_width(), reflect_surface.get_height()*self.squeeze))
        #reflect_surface.set_alpha(100)
        blit_pos = [self.rect.topleft[0] - self.game_objects.camera.scroll[0],self.rect.topleft[1] - self.game_objects.camera.scroll[1]]
        self.game_objects.game.screen.blit(pygame.transform.flip(reflect_surface, False, True), blit_pos, self.reflect_rect, special_flags = pygame.BLEND_RGBA_MULT)#BLEND_RGBA_MIN

class Animatedentity(Staticentity):#animated stuff, i.e. cosmetics
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects#animation need dt
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

    def update(self):
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):#states_basic needs this
        pass

class Platform_entity(Animatedentity):#Things to collide with platforms
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = False#a flag for entities to go through ramps from side or top
        self.velocity = [0,0]

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
        self.true_pos = list(self.rect.center)
        self.hitbox.midbottom = self.rect.midbottom

    def update_true_pos_x(self):#called from Engine.platform collision. The velocity to true pos need to be set in collision if group distance should work proerly for enemies (so that the velocity is not applied when removing the sprite from gorup)
        self.true_pos[0] += self.slow_motion*self.game_objects.game.dt*self.velocity[0]
        self.rect.left = int(self.true_pos[0])#should be int
        self.update_hitbox()

    def update_true_pos_y(self):#called from Engine.platform collision
        self.true_pos[1] += self.slow_motion*self.game_objects.game.dt*self.velocity[1]
        self.rect.top = int(self.true_pos[1])#should be int
        self.update_hitbox()

    #pltform collisions.
    def right_collision(self,hitbox):
        self.hitbox.right = hitbox
        self.collision_types['right'] = True
        self.currentstate.handle_input('Wall')

    def left_collision(self,hitbox):
        self.hitbox.left = hitbox
        self.collision_types['left'] = True
        self.currentstate.handle_input('Wall')

    def down_collision(self,hitbox):
        self.hitbox.bottom = hitbox
        self.collision_types['bottom'] = True
        self.currentstate.handle_input('Ground')

    def top_collision(self,hitbox):
        self.hitbox.top = hitbox
        self.collision_types['top'] = True
        self.velocity[1] = 0

    def limit_y(self):#limits the velocity on ground. But not on ramps
        point = [self.hitbox.midbottom[0]+5*self.dir[0],self.hitbox.midbottom[1]+10]#infront flightly below
        if not self.game_objects.collisions.check_ramp(point):#there is not ramp in front
            self.velocity[1] = 1/self.game_objects.game.dt

class Character(Platform_entity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()

        self.timers = []#a list where timers are append whe applicable, e.g. jump, invincibility etc.
        self.running_particles = Dust_running_particles

    def update(self):
        self.update_timers()
        self.update_vel()#need to be after update_timers since jump will add velocity in update_timers
        self.currentstate.update()#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update()#need to be after currentstate since animation will animate the current state

    def update_vel(self):
        self.velocity[1] += self.slow_motion*self.game_objects.game.dt*(self.acceleration[1]-self.velocity[1]*self.friction[1])#gravity
        self.velocity[1] = min(self.velocity[1],self.max_vel[1])#set a y max speed#

        self.velocity[0] += self.slow_motion*self.game_objects.game.dt*(self.dir[0]*self.acceleration[0] - self.friction[0]*self.velocity[0])

    def take_dmg(self,dmg):
        if self.invincibile: return
        self.health -= dmg

        if self.health > 0:#check if dead¨
            self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period (minimum time needed to that the swrod doesn't hit every frame)
            self.animation.handle_input('Hurt')#turn white
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            self.game_objects.camera.camera_shake(3,10)
        else:#if dead
            self.aggro = False
            self.invincibile = True
            self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
            self.AI.deactivate()
            self.currentstate.enter_state('Death')#overrite any state and go to deat

    def knock_back(self,dir):
        self.velocity[0] = dir[0]*30
        self.velocity[1] = -dir[1]*10

    def hurt_particles(self,distance=0,lifetime=40,vel={'linear':[7,15]},type='Circle',dir='isotropic',scale=3,colour=[255,255,255,255],number_particles=20):
        for i in range(0,number_particles):
            obj1 = getattr(particles, type)(self.hitbox.center,self.game_objects,distance,lifetime,vel,dir,scale,colour)
            self.game_objects.cosmetics.add(obj1)

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Player(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sounds = Read_files.Sounds('Audio/SFX/enteties/aila/')
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/aila/')
        self.image = self.sprites.sprite_dict['idle_main'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes

        self.max_health = 10
        self.max_spirit = 5
        self.health = 5
        self.spirit = 2

        self.projectiles = game_objects.fprojectiles
        self.sword = Aila_sword(self)
        self.abilities = Player_abilities(self)#spirit (thunder,migawari etc) and movement /dash, double jump and wall glide)

        self.states = {'Idle':True,'Walk':True,'Run':True,'Pray':True,'Jump_run':True,
                     'Jump_stand':True,'Fall_run':True,'Fall_stand':True,'Death':True,
                     'Invisible':True,'Hurt':True,'Spawn':True,'Plant_bone':True,
                     'Sword_run1':True,'Sword_run2':True,'Sword_stand1':True,'Sword_stand2':True,
                     'Air_sword2':True,'Air_sword1':True,'Sword_up':True,'Sword_down':True,
                     'Dash_attack':True,'Ground_dash':True,'Air_dash':True,'Wall_glide':True,'Double_jump':True,
                     'Thunder':True,'Force':True,'Migawari':True,'Slow_motion':True,
                     'Arrow':True,'Counter':True}
        self.currentstate = states_player.Idle_main(self)

        self.spawn_point = [{'map':'light_forest_1', 'point':'1'}]#a list of max len 2. First elemnt is updated by sejt interaction. Can append positino for bone, which will pop after use
        self.inventory = {'Amber_Droplet':403,'Bone':2,'Soul_essence':10,'Tungsten':10}#the keys need to have the same name as their respective classes
        self.omamoris = Omamoris(self)#

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_player),'jump':Jump_timer(self,C.jump_time_player),'sword':Sword_timer(self,C.sword_time_player),'shroomjump':Shroomjump_timer(self,C.shroomjump_timer_player),'ground':Ground_timer(self,C.ground_timer_player),'air':Air_timer(self,C.air_timer)}#these timers are activated when promt and a job is appeneded to self.timer.

    def down_collision(self,hitbox):#when colliding with platform beneth
        super().down_collision(hitbox)
        self.ground = True#used for jumping

    def take_dmg(self,dmg = 1):
        if self.invincibile: return
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
        self.health -= dmg*self.dmg_scale#a omamori can set the dmg_scale to 0.5
        self.game_objects.UI['gameplay'].remove_hearts(dmg*self.dmg_scale)#update UI

        if self.health > 0:#check if dead¨
            self.animation.handle_input('Hurt')#turn white
            self.animation.handle_input('Invincibile')#blink a bit. need to be after hurt
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            self.hurt_particles(lifetime=40,vel={'linear':[3,8]},colour=[0,0,0,255],scale=3,number_particles=60)
            self.game_objects.cosmetics.add(Slash(self.hitbox.center,self.game_objects))#make a slash animation
            self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
        else:#if health < 0
            self.game_objects.game.state_stack[-1].handle_input('death')#depending on gameplay state, different death stuff should happen

    def heal(self, health = 1):
        self.health += health
        self.game_objects.UI['gameplay'].update_hearts()#update UI

    def consume_spirit(self, spirit = 1):
        self.spirit -= spirit
        self.game_objects.UI['gameplay'].remove_spirits(spirit)#update UI

    def add_spirit(self, spirit = 1):
        self.spirit += spirit
        self.game_objects.UI['gameplay'].update_spirits()#update UI

    def death(self):#"normal" gameplay states calls this
        self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
        self.currentstate.enter_state('Death_pre')#overrite any state and go to deat

    def dead(self):#called when death animation is finished
        new_game_state = states.Cutscenes(self.game_objects.game,'Death')
        new_game_state.enter_state()

    def reset_movement(self):#called when loading new map or entering conversations
        self.velocity = [0,0]
        self.acceleration =  [0,C.acceleration[1]]
        self.friction = C.friction_player.copy()

    def update(self):
        super().update()
        self.omamoris.update()

class Migawari_entity(Character):#player double ganger
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/migawari/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1]-5,16,35)#add a smalll ofset in y to avoid collision
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes
        self.invincibile = False
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_player)}#these timers are activated when promt and a job is appeneded to self.timer.

    def set_health(self,health):#should be called when making this object
        self.health = health

    def set_lifetime(self,lifetime):#should be called when making this object
        self.lifetime = lifetime

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destroy()

    def take_dmg(self,dmg):
        if self.invincibile: return
        self.health -= dmg
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period

        if self.health > 0:#check if dead¨
            self.animation.handle_input('Hurt')#turn white
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
        else:#if dead
            if self.currentstate.state_name != 'death':#if not already dead
                if self.game_objects.player.abilities.spirit_abilities['Migawari'].level == 3:
                    self.game_objects.player.heal(1)
                self.currentstate.enter_state('Death')#overrite any state and go to deat

    def destroy(self):
        if self.lifetime < 0:
            self.currentstate.enter_state('Death')#overrite any state and go to deat
            self.kill()

class Enemy(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause
        self.description = 'enemy'##used in journal
        self.original_pos = pos

        self.currentstate = states_enemy.Idle(self)
        AI_enemy.build_tree(self)#self.AI = AI_enemy.Peace(self)

        self.inventory = {'Amber_Droplet':random.randint(0,10),'Bone':1,'Heal_item':1}#thigs to drop wgen killed
        self.spirit = 10
        self.health = 3

        self.aggro = True#colliding with player
        self.dmg = 1#projectile damage

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

        self.attack_distance = [0,0]#at which distance to the player to attack
        self.aggro_distance = [100,50]#at which distance to the player when you should be aggro. Negative value make it no going aggro

    def update(self):
        super().update()
        self.AI.update()#tell what the entity should do
        self.group_distance()

    def player_collision(self,player):#when player collides with enemy
        if not self.aggro: return
        if player.invincibile: return
        #if player.currentstate.state_name == 'death': return
        player.take_dmg(1)
        sign = math.copysign(1,(player.hitbox.center[0]-self.hitbox.center[0]))
        player.knock_back([sign,0])

    def dead(self):#called when death animation is finished
        self.loots()
        self.game_objects.world_state.update_kill_statistics(type(self).__name__.lower())
        self.kill()

    def loots(self):#called when dead
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop,self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def countered(self):#player shield
        self.velocity[0] = -30*self.dir[0]
        self.currentstate = states_enemy.Stun(self,duration=30)#should it overwrite?

    def health_bar(self):#called from omamori Boss_HP
        pass

    def chase(self):#called from AI: when chaising
        self.velocity[0] += self.dir[0]*0.5

    def patrol(self,position):#called from AI: when patroling
        self.velocity[0] += self.dir[0]*0.3

class Flying_enemy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8,C.friction[0]*0.8]
        self.max_vel = [C.max_vel[0],C.max_vel[0]]
        self.dir[1] = 1

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def knock_back(self,dir):
        self.velocity[0] = dir[0]*30
        self.velocity[1] = -dir[1]*30

    def chase(self):#called from AI: when chaising
        self.velocity[0] += self.dir[0]*0.3#*abs(math.sin(self.init_time))
        self.velocity[1] += (self.AI.black_board['player_distance'][1] - 30)*0.002

    def patrol(self,position):#called from AI: when patroling
        self.velocity[0] += 0.001*(position[0]-self.rect.centerx)+0.02*self.dir[0]
        self.velocity[0] = math.copysign(1,self.velocity[0])*min(abs(self.velocity[0]),1)#limit the max abs velocity to 1
        self.velocity[1] += 0.001*(position[1]-self.rect.centery)

class Mygga(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate = states_mygga.Idle(self)
        self.health = 3

class Exploding_Mygga(Flying_enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/exploding_mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate = states_mygga.Idle(self)
        AI_exploding_mygga.build_tree(self)#AI_exploding_mygga.Peace(self)#
        self.health = 4
        self.attack_distance = [20,20]
        self.aggro_distance = [150,100]
        self.size = [64,64]#hurtbox size for hurt box

    def suicide(self):
        self.projectiles.add(Hurt_box(self,lifetime = 50))
        self.game_objects.camera.camera_shake(amp=2,duration=30)#amplitude and duration

class Packun(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/packun/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.health = 3
        self.dmg = 1
        self.attack = Projectile_1
        self.attack_distance = [250,50]

    def chase(self):#called from AI
        pass

    def patrol(self,position):
        pass

class Sandrew(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/sandrew/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_sandrew.Idle(self)
        self.health = 3
        self.attack_distance = [250,50]
        self.aggro_distance = [250,50]#at which distance to the player when you should be aggro. Negative value make it no going aggro

class Slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.aggro_distance = [-1,-1]#at which distance to the player when you should be aggro

class Slime_giant(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/slime_giant/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],48,48)
        self.number = random.randint(1, 6)

    def dead(self):
        self.game_objects.world_state.update_kill_statistics(type(self).__name__.lower())
        self.spawn_minions()
        self.kill()

    def spawn_minions(self):
        pos = [self.hitbox.centerx,self.hitbox.centery-10]
        for i in range(0,self.number):
            obj = Slime(pos,self.game_objects)
            obj.velocity=[random.randint(-10, 10),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Wall_slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_wallslime('Sprites/Enteties/enemies/wall_slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()#pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate.enter_state('Walk')
        self.AI = AI_wall_slime.Peace(self)

    def knock_back(self,dir):
        pass

    def update_vel(self):
        self.velocity[1] = self.acceleration[1]-self.dir[1]
        self.velocity[0] = self.acceleration[0]+self.dir[0]

class Woopie(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.health = 1
        self.spirit=100

class Vatt(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/vatt/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)
        self.health = 3
        self.spirit = 3
        self.aggro = False
        self.currentstate = states_vatt.Idle(self)
        self.attack_distance = 60
        self.AI = AI_vatt.Peace(self)

    def turn_clan(self):#this is acalled when tranformation is finished
        for enemy in self.game_objects.enemies.sprites():
            if type(enemy).__name__=='Vatt':
                enemy.aggro = True
                enemy.currentstate.handle_input('Transform')

class Flowy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/flowy/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1
        self.spirit=10

class Larv_poison(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/larv/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.attack=Poisonblobb
        self.attack_distance=150

class Larv_simple(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/larv_simple/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,30)

class Blue_bird(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/animals/bluebird/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate = states_bluebird.Idle(self)
        self.aggro=False
        self.health=1
        self.AI = AI_bluebird.Peace(self)#should we make it into a tree as well?
        self.aggro_distance = [100,50]#at which distance to the player when you should be aggro. Negative value make it no going aggro

    def knock_back(self,dir):
        pass

class Shroompoline(Enemy):#an enemy or interactable?
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/shroompolin/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box=pygame.Rect(pos[0],pos[1],32,10)
        self.aggro = False#player collision
        self.invincibile = True#taking dmg

    def player_collision(self,player):
        if self.game_objects.player.velocity[1]>0:#going down
            offset=self.game_objects.player.velocity[1]+1
            if self.game_objects.player.hitbox.bottom < self.jump_box.top+offset:
                self.currentstate.enter_state('Hurt')
                self.game_objects.player.currentstate.enter_state('Jump_stand_main')
                self.game_objects.player.velocity[1] = -10
                self.game_objects.player.timer_jobs['shroomjump'].activate()

    def update_hitbox(self):
        super().update_hitbox()
        self.jump_box.midtop = self.rect.midtop

    def chase(self):#called from AI: when chaising
        pass

    def patrol(self,position):#called from AI: when patroling
        pass

class Kusa(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/kusa/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = 30
        self.health = 1
        self.AI = AI_kusa.Peace(self)
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera.camera_shake(amp=2,duration=30)#amplitude and duration

class Svampis(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/svampis/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = 30
        self.health = 1
        self.AI = AI_kusa.Peace(self)
        self.dmg = 2

    def suicide(self):
        self.projectiles.add(Explosion(self))
        self.game_objects.camera.camera_shake(amp=2,duration=30)#amplitude and duration

class Egg(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/egg/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.number = random.randint(1, 4)
        self.aggro_distance = -1 #if negative, it will not go into aggro

    def knock_back(self,dir):
        pass

    def death(self):
        self.spawn_minions()
        self.kill()

    def spawn_minions(self):
        pos = [self.hitbox.centerx,self.hitbox.centery-10]
        for i in range(0,self.number):
            obj = Slime(pos,self.game_objects)
            obj.velocity=[random.randint(-100, 100),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Skeleton_warrior(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/skeleton_warrior/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,40)
        self.attack_distance = 100
        self.attack = Sword
        self.health = 3

    def knock_back(self,dir):
        pass

class Liemannen(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/liemannen/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,40)
        self.attack_distance = 100
        self.attack = Sword

    def knock_back(self,dir):
        pass

class Skeleton_archer(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/skeleton_archer/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,40)
        self.attack_distance = 300
        self.attack = Arrow
        self.aggro_distance = 400

    def knock_back(self,dir):
        pass

class Cultist_rogue(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/cultist_rogue/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 10
        self.attack_distance = [80,10]
        self.attack = Sword
        self.currentstate = states_rogue_cultist.Idle(self)

class Cultist_warrior(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/cultist_warrior/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 10
        self.attack_distance = [80,10]
        self.attack = Sword

class John(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/john/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.attack_distance = 80
        self.attack = Sword

class NPC(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.group = game_objects.npcs
        self.pause_group = game_objects.entity_pause
        self.name = str(type(self).__name__)#the name of the class

        self.sprites = Read_files.Sprites_Player("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox
        self.portrait = pygame.image.load('Sprites/Enteties/NPC/' + self.name +'/potrait.png').convert_alpha()

        self.currentstate = states_NPC.Idle(self)
        self.dialogue = dialogue.Dialogue(self)#handles dialoage and what to say
        self.define_conversations()

    def define_conversations(self):#should depend on NPC
        self.priority = ['reindeer','ape']#priority events to say
        self.event = ['aslat']#normal events to say

    def update(self):
        super().update()
        #self.group_distance()

    def interact(self):#when plater press t
        new_state = states.Conversation(self.game_objects.game, self)
        new_state.enter_state()

    def idle(self):
        self.currentstate.handle_input('Idle')

    def walk(self):
        self.currentstate.handle_input('Walk')

    def buisness(self):#enters after conversation
        pass

class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
    #    self.true_pos = self.rect.topleft

    def buisness(self):#enters after conversation
        if 'reindeer' not in self.priority:#if player has deafated the reindeer
            if not self.game_objects.player.states['Wall_glide']:#if player doesn't have wall yet
                new_game_state = states.New_ability(self.game_objects.game,'Wall_glide')
                new_game_state.enter_state()
                self.game_objects.player.states['Wall_glide'] = True

class Sahkar(NPC):#deer handler
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Bierdna(NPC):#bartender
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_Droplet':1}#itam+price

    def buisness(self):#enters after conversation
        new_state = states.Facilities(self.game_objects.game,'Vendor',self)
        new_state.enter_state()

class MrSmith(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        new_state = states.Facilities(self.game_objects.game,'Smith',self)
        new_state.enter_state()

class MrBanks(NPC):#bank
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.ammount = 0

    def buisness(self):#enters after conversation
        new_state = states.Facilities(self.game_objects.game,'Bank',self)
        new_state.enter_state()

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 10
        self.health_bar = Health_bar(self)

    def dead(self):
        self.loots()
        self.give_abillity()
        self.game_objects.world_state.increase_progress()
        self.game_objects.world_state.update_event(str(type(self).__name__).lower())
        new_game_state = states.New_ability(self.game_objects.game,self.abillity)
        new_game_state.enter_state()
        new_game_state = states.Cutscenes(self.game_objects.game,'Defeated_boss')
        new_game_state.enter_state()

    def health_bar(self):#called from omamori Boss_HP
        self.health_bar.max_health = self.health
        self.game_objects.cosmetics.add(self.health_bar)

    def give_abillity(self):
        self.game_objects.player.abilities.Player_abilities[self.ability] = getattr(sys.modules[__name__], self.ability)

class Reindeer(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/reindeer/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate = states_reindeer.Idle(self)
        AI_reindeer.build_tree(self)

        self.abillity = 'dash_1main'#the stae of image that will be blitted to show which ability that was gained
        self.attack = Sword
        self.special_attack = Horn_vines
        self.attack_distance = 50

    def give_abillity(self):#called when reindeer dies
        self.game_objects.player.states['Dash'] = True#append dash abillity to available states

    def take_dmg(self,dmg):
        super().take_dmg(dmg)
        self.health_bar.resize()

    def knock_back(self,dir):
        pass

class Idun(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/idun/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.attack_distance = 100
        self.attack = Sword

    def death(self):
        self.kill()

    def give_abillity(self):
        pass

class Freja(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/freja/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.attack_distance = 100
        self.attack = Sword

    def death(self):
        self.kill()

    def give_abillity(self):
        self.game_objects.player.dash=True

class Tyr(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/tyr/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.attack_distance = 100
        self.attack = Sword

    def death(self):
        self.kill()

    def give_abillity(self):
        self.game_objects.player.dash=True

class Fenrisulven(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/fenrisulven/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.attack_distance = 100
        self.attack = Sword

    def death(self):
        self.kill()

    def give_abillity(self):
        self.game_objects.player.dash=True

class Rhoutta_encounter(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/rhoutta/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 5
        self.attack_distance = 100
        self.attack = Sword
        self.dmg = 0
        self.count = 0

    def hurt(self):
        super().hurt()
        self.count += 1
        if self.count > 3:
            new_game_state = states.Cutscenes(self.game_objects.game,'Rhoutta_encounter')
            new_game_state.enter_state()
        #new_game_state = states.Fading(self.game_objects.game,1)
        #new_game_state.enter_state()

#stuff
class Camera_Stop(Staticentity):
    def __init__(self,game_objects, size,pos,dir):
        super().__init__(pos,pygame.Surface(size))
        self.game_objects = game_objects
        self.hitbox = self.rect.inflate(0,0)
        self.size = size

        self.currentstate = states_camerastop.Idle(self)
        self.currentstate.enter_state('Idle_'+dir)

class Spawner(Staticentity):#an entity spawner
    def __init__(self,pos,game_objects,values):
        super().__init__(pos)
        self.game_objects = game_objects
        self.entity = values['entity']
        self.number = int(values['number'])
        self.spawn_entities()

    def spawn_entities(self):
        for i in range(0,self.number):
            offset=random.randint(-100, 100)
            pos=[self.rect.x+offset,self.rect.y]
            obj=getattr(sys.modules[__name__], self.entity)(pos,self.game_objects)
            self.game_objects.enemies.add(obj)

class Dark_screen(Staticentity):#a dark layer ontop of  stagge, used in e.g. caves. loaded in maploader
    def __init__(self, game_objects, colour = (10,10,10,200)):
        super().__init__([0,0], pygame.Surface((int(game_objects.game.WINDOW_SIZE[0]), int(game_objects.game.WINDOW_SIZE[1]))))
        self.game_objects = game_objects
        self.colour = colour

    def update(self):
        self.rect.topleft  = [self.game_objects.camera.scroll[0], self.game_objects.camera.scroll[1]]#this is [0,0]
        self.image.fill(self.colour)#make it dark again

class Light_glow(Staticentity):#a light glow anounf an entity.
    def __init__(self, entity, radius = 200,layers = 40):
        super().__init__(entity.rect.center)
        self.entity = entity
        self.game_objects = entity.game_objects
        self.radius = radius
        self.layers = layers
        self.make_glow()
        self.image = self.glow
        self.rect = self.image.get_rect()
        self.rect.center = entity.rect.center
        self.alpha = 255

    def diminish(self):#slowly reduce the light
        self.image.set_alpha(int(self.alpha))
        self.alpha -= self.game_objects.game.dt*self.slow_motion

    def make_glow(self):#init
        self.glow = pygame.Surface((self.radius * 2, self.radius * 2),pygame.SRCALPHA,32).convert_alpha()

        for i in range(self.layers):
            temp = pygame.Surface((self.radius * 2, self.radius * 2),pygame.SRCALPHA,32).convert_alpha()
            pygame.draw.circle(temp,(80,80,80,1),temp.get_rect().center,i*5+1)
            self.glow.blit(temp,[0,0],special_flags = pygame.BLEND_RGBA_ADD)

class Dark_glow(Staticentity):#the glow to use in dark area; it removes the dark screen/layer in e.g. caves. It can be combined with light_glow
    def __init__(self, entity, radius = 200, layers = 40):
        super().__init__(entity.rect.center)
        self.entity = entity
        self.game_objects = entity.game_objects
        self.radius = radius
        self.layers = layers
        self.make_glow()

    def update(self):
        pos = [self.entity.rect.centerx - self.radius - self.game_objects.camera.scroll[0], self.entity.rect.centery - self.radius - self.game_objects.camera.scroll[1]]
        self.game_objects.map.screen.image.blit(self.glow, pos, special_flags = pygame.BLEND_RGBA_SUB)
        #self.game_objects.map.screen.image.blit(self.game_objects.map.screen.image, (0,0), special_flags = pygame.BLEND_RGB_SUB)#inverting

    def make_glow(self,const = 6):#init
        self.glow = pygame.Surface((self.radius * 2, self.radius * 2),pygame.SRCALPHA,32).convert_alpha()

        for i in range(self.layers):
            k = i*const
            k = min(k,255)
            pygame.draw.circle(self.glow,(0,0,0,k),self.glow.get_rect().center,self.radius-i*5)

class Dash_effect(Staticentity):
    def __init__(self, entity, alpha = 255):
        super().__init__(entity.rect.center)
        self.image = entity.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = entity.rect.center
        self.alpha = alpha
        self.image.set_alpha(self.alpha)
        self.true_pos = self.rect.topleft

    def update(self):
        self.alpha *= 0.9
        self.image.set_alpha(self.alpha)
        self.destroy()

    def destroy(self):
        if self.alpha < 5:
            self.kill()

class Sign_symbols(Staticentity):#a part of sign, it blits the landsmarks in the appropriate directions
    def __init__(self,entity):
        super().__init__(entity.rect.center)
        self.game_objects = entity.game_objects
        self.image = pygame.Surface((400,400), pygame.SRCALPHA, 32).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = [entity.game_objects.game.WINDOW_SIZE[0]*0.5,entity.game_objects.game.WINDOW_SIZE[0]*0.5-100]
        self.image.fill((0,0,0))

        dir = {'left':[self.image.get_width()*0.25,150],'up':[self.image.get_width()*0.5,50],'right':[self.image.get_width()*0.75,150],'down':[self.image.get_width()*0.5,300]}
        for key in entity.directions.keys():
            text = entity.game_objects.font.render(text = entity.directions[key])
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.image.blit(text,dir[key])

        self.render_fade=[self.render_in,self.render_out]
        self.init()

    def init(self):
        self.fade = 0
        self.image.set_alpha(self.fade)
        self.page = 0

    def update(self):
        self.render_fade[self.page]()

    def render_in(self):
        self.fade += self.game_objects.game.dt
        self.fade = min(self.fade,200)
        self.image.set_alpha(int(self.fade))

    def render_out(self):
        self.fade -= self.game_objects.game.dt
        self.fade = max(self.fade,0)
        self.image.set_alpha(int(self.fade))

        if self.fade < 10:
            self.init()
            self.kill()

    def finish(self):#called when fading out should start
        self.page = 1

class Shade_Screen(Staticentity):#a screen that can be put on each layer to make it e.g. dark or light
    def __init__(self, game_objects, parallax, colour):
        super().__init__([0,0], pygame.Surface([game_objects.game.WINDOW_SIZE[0],game_objects.game.WINDOW_SIZE[1]], pygame.SRCALPHA, 32))
        self.game_objects = game_objects
        self.colour = [colour.g,colour.b,colour.a,7/parallax[0]]#higher alpha for lower parallax
        self.original_colour = self.colour.copy()
        self.image.fill(self.colour)#make it dark again
        self.currentstate = state_shade_screen.Idle(self,self.original_colour)

    def update(self):
        self.currentstate.update()
        self.true_pos = [self.game_objects.camera.scroll[0], self.game_objects.camera.scroll[1]]#this is [0,0]

#Player movement abilities, handles them. Contains also spirit abilities
class Player_abilities():
    def __init__(self,entity):
        self.entity = entity
        self.spirit_abilities = {'Thunder':Thunder(entity),'Force':Force(entity),'Arrow':Arrow(entity),'Migawari':Migawari(entity),'Slow_motion':Slow_motion(entity)}#abilities aila has
        self.equip = 'Thunder'#spirit ability pointer
        self.movement_dict = {'Dash':Dash(entity),'Wall_glide':Wall_glide(entity),'Double_jump':Double_jump(entity)}#abilities the player has
        self.movement_abilities = list(self.movement_dict.values())#make it a list
        self.number = 3#number of movement abilities one can have equiped, the equiped one will be appended to self.entity.states

    def remove_ability(self):#movement stuff
        abilities = self.movement_abilities[0:self.number]#the abilities currently equiped
        for ability in abilities:#remove ability
            string = ability.__class__.__name__
            self.entity.states.remove(string)

    def add_ability(self):#movement stuff
        abilities = self.movement_abilities[0:self.number]#the abilities to be equiped
        for ability in abilities:#at tthe ones we have equipped
            string = ability.__class__.__name__
            self.entity.states.add(string)

    def increase_number(self):#movement stuff
        self.number += 1
        self.number = min(self.number,3)#limit the number of abilities one can equip at the same time

    def handle_input(self,input):#movement stuff
        value = input[2]['d_pad']
        if sum(value) == 0: return#if d_pad wasn't pressed

        if value[0] == 1:#pressed right
            self.remove_ability()
            self.movement_abilities = self.movement_abilities[-1:] + self.movement_abilities[:-1]#rotate the abilityes to the right
            self.entity.game_objects.UI['gameplay'].init_ability()
            self.add_ability()
        elif value[0] == -1:#pressed left
            self.remove_ability()
            self.movement_abilities = self.movement_abilities[1:] + self.movement_abilities[:1]#rotate the abilityes to the left
            self.entity.game_objects.UI['gameplay'].init_ability()
            self.add_ability()
        elif value[1] == 1:#pressed up
            pass
        elif value[1] == -1:#pressed down
            pass

class Movement_abilities():#ailas movement abilities. Contains logic to handle the level ups from save point. Should it do something when used?
    def __init__(self,entity):
        self.entity = entity
        self.level = 1

    def upgrade_ability(self):
        self.level += 1

class Dash(Movement_abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Wall_glide(Movement_abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Double_jump(Movement_abilities):
    def __init__(self,entity):
        super().__init__(entity)

#projectiles
class Projectiles(Animatedentity):#projectiels: should it be platform enteties?
    def __init__(self,entity):
        super().__init__([0,0],entity.game_objects)
        self.entity = entity
        self.dir = entity.dir.copy()
        self.timers = []#a list where timers are append whe applicable, e.g. jump, invincibility etc.
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

    def update(self):
        super().update()
        self.update_timers()
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destroy()

    def destroy(self):
        if self.lifetime < 0:
            self.kill()

    def update_timers(self):
        for timer in self.timers:
            timer.update()

    def update_hitbox(self):#make this a dictionary?
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
            self.dir[0] = 0#no side knock back when hit from below or above
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
            self.dir[0] = 0 #no side knock back when hit from below or above
        elif self.dir[0] > 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def collision_projectile(self,eprojectile):#projecticle proectile collision
        pass

    def collision_enemy(self,collision_enemy):#projecticle enemy collision (inclusing player)
        if collision_enemy.invincibile: return#is this needed?
        collision_enemy.take_dmg(self.dmg)
        #self.kill()

    def collision_plat(self,platform):#collision platform
        pass

    def collision_inetractables(self,interactable):#collusion interactables
        pass

    #called from upgrade menu
    def upgrade_ability(self):
        self.level += 1

    def countered(self,dir, pos):#called from sword collsion with purple infinity stone
        pass

class Melee(Projectiles):
    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        super().update()
        self.update_hitbox()

    def countered(self,dir,pos):#called from sword collision_projectile, purple initinty stone
        return
        self.entity.countered()
        self.kill()

class Hurt_box(Melee):#a hitbox that spawns
    def __init__(self,entity, lifetime = 100):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/hurt_box/')#invisible
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = entity.rect.center
        self.hitbox = pygame.Rect(entity.rect.x,entity.rect.y,entity.size[0],entity.size[1])
        self.lifetime = lifetime
        self.dmg = entity.dmg

    def update_hitbox(self):
        pass

class Explosion(Melee):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/explosion/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.x = entity.rect.x
        self.rect.bottom = entity.rect.bottom
        self.hitbox = self.rect.copy()
        self.lifetime = 100
        self.dmg = entity.dmg

    def update_hitbox(self):
        pass

    def reset_timer(self):
        self.kill()

class Shield(Melee):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/invisible/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.entity.hitbox.copy()#pygame.Rect(self.entity.rect[0],self.entity.rect[1],20,40)
        self.hitbox = self.rect.copy()
        self.dmg = 0
        self.lifetime = 25

    def update_hitbox(self):
        if self.dir[0] > 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def collision_enemy(self,collision_enemy):
        collision_enemy.countered()
        self.kill()

    def collision_projectile(self,eprojectile):
        return
        self.entity.projectiles.add(eprojectile)#add the projectilce to Ailas projectile group
        eprojectile.countered(self.dir,self.rect.center)

class Sword(Melee):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/Sword/')
        self.init()
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,40,35)
        self.hitbox = self.rect.copy()

    def init(self):
        self.dmg = self.entity.dmg

    def collision_enemy(self, collision_enemy):
        self.sword_jump()
        if collision_enemy.invincibile: return
        collision_enemy.take_dmg(self.dmg)
        collision_enemy.knock_back(self.dir)
        collision_enemy.hurt_particles(dir = self.dir[0])
        #slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])#self.entity.cosmetics.add(slash)
        if self.dir[0]>0:
            self.clash_particles(self.rect.midright)
        else:
            self.clash_particles(self.rect.midleft)

    def sword_jump(self):
        if self.dir[1] == -1:
            self.entity.velocity[1] = -11

    def clash_particles(self,pos,number_particles=12):
        angle=random.randint(-180, 180)#the ejection anglex
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos,self.game_objects,distance=0,lifetime=20,vel={'linear':[7,14]},dir=angle,scale=0.5,colour = [255,255,255,255])
            self.entity.game_objects.cosmetics.add(obj1)

    def collision_inetractables(self,interactable):#called when projectile hits interactables
        interactable.take_dmg(self)#some will call clash_particles but other will not. So sending self to interactables

class Aila_sword(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.tungsten_cost = 1#the cost to level up to next level
        self.level = 0#determines how many stone one can attach
        self.equip = ['purple']#stone pointers, the ones attached to the sword, strings
        self.stones = {'red':Red_infinity_stone(self),'green':Green_infinity_stone(self),'blue':Blue_infinity_stone(self),'orange':Orange_infinity_stone(self),'purple':Red_infinity_stone(self)}#the ones aila has picked up
        self.colour = {'red':[255,64,64,255],'blue':[0,0,205,255],'green':[105,139,105,255],'orange':[255,127,36,255],'purple':[154,50,205,255]}#spark colour
        self.swing = 0#a flag to check which swing we are at (0 or 1)

    def init(self):
        self.dmg = 1

    def set_stone(self,stone_str):#called from smith
        if len(self.equip) < self.level:
            self.equip.append(stone_str)
            self.stones[stone_str].attach()

    def remove_stone(self):#not impleented
        pass
        #if self.equip != 'idle':#if not first time
        #    self.stones[self.equip].detach()

    def collision_projectile(self,eprojectile):#projecticle proectile collision
        if eprojectile.invincibile: return
        eprojectile.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period

        if 'purple' in self.equip:#if the purpuple stone is equped
            eprojectile.countered(self.dir,self.rect.center)
            self.sword_jump()
        else:
            eprojectile.velocity = [0,0]
            eprojectile.dmg = 0
            eprojectile.currentstate.handle_input('Death')

    def collision_enemy(self,collision_enemy):
        super().collision_enemy(collision_enemy)
        self.game_objects.camera.camera_shake(amp=2,duration=30)#amplitude and duration
        for stone in self.equip:
            self.stones[stone].collision()#call collision specific for stone

    def clash_particles(self,pos,number_particles=12):
        angle = random.randint(-180, 180)#the ejection anglex
        color = [255,255,255,255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Spark')(pos,self.game_objects,distance=0,lifetime=15,vel={'linear':[7,14]},dir=angle,scale=0.4,colour=color)
            self.entity.game_objects.cosmetics.add(obj1)

    def level_up(self):#called when the smith imporoves the sword
        if self.level >= 3: return
        self.entity.inventory['Tungsten'] -= self.tungsten_cost
        self.dmg *= 1.2
        self.level += 1
        self.tungsten_cost += 2#1, 3, 5 tungstes to level upp 1, 2, 3

class Ranged(Projectiles):
    def __init__(self,entity):
        super().__init__(entity)
        self.velocity = [0,0]

    def update(self):
        super().update()
        self.update_pos()

    def update_pos(self):
        self.rect.topleft = [self.rect.topleft[0] + self.slow_motion*self.game_objects.game.dt*self.velocity[0], self.rect.topleft[1] + self.slow_motion*self.game_objects.game.dt*self.velocity[1]]
        self.hitbox.center = self.rect.center

class Thunder(Ranged):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/Thunder/')
        self.currentstate = states_basic.Death(self)#
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.dmg = 1
        self.level = 1#upgrade pointer

    def initiate(self,enemy_rect):
        self.rect.midbottom = enemy_rect.midbottom
        self.hitbox = self.rect.copy()
        self.lifetime = 1000

    def collision_enemy(self,collision_enemy):
        super().collision_enemy(collision_enemy)
        self.dmg = 0
        collision_enemy.velocity = [0,0]#slow him down

    def reset_timer(self):
        self.dmg = 1
        self.kill()

class Poisoncloud(Ranged):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/poisoncloud/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.dmg = 1
        self.lifetime=400
        self.update_hitbox()

    def collision_ene(self,collision_ene):
        pass

    def destroy(self):
        if self.lifetime<0:
            self.currentstate.handle_input('Death')

    def countered(self,dir,pos):#shielded
        self.currentstate.handle_input('Death')

class Poisonblobb(Ranged):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/poisonblobb/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(self.rect.x,self.rect.y,16,16)
        self.update_hitbox()

        self.dmg = entity.dmg
        self.lifetime = 100
        self.velocity=[entity.dir[0]*5,-1]

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        self.velocity[1] += 0.1*self.game_objects.game.dt*self.slow_motion#graivity

    def collision_plat(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

class Projectile_1(Ranged):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/projectile_1/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.update_hitbox()

        self.dmg = entity.dmg
        self.lifetime = 400
        self.velocity=[entity.dir[0]*5,0]

    def collision_plat(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

    def countered(self,dir,pos):#called from sword collsion with purple infinity stone
        dy = self.rect.centery - pos[1]
        dx = self.rect.centerx - pos[0]

        self.velocity[0] = -dir[1]*self.velocity[0]*dx*0.05 + dir[0]*(10 - abs(dx)*0.1)
        self.velocity[1] = -dir[1]*10 + self.velocity[1]*abs(dy) + dir[0]*dy*0.2

class Horn_vines(Ranged):
    def __init__(self, entity, pos):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/horn_vines/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.rect.bottom = self.entity.rect.bottom
        self.hitbox = self.rect.copy()
        self.hitbox = pygame.Rect(pos[0],pos[1],0,0)#
        self.currentstate = states_horn_vines.Idle(self)#
        self.dmg = entity.dmg
        self.lifetime = 500

    def destroy(self):
        if self.lifetime < 0:
            self.entity.currentstate.handle_input('Horn_vines')
            self.kill()

class Force(Ranged):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/force/')
        self.image = self.sprites.sprite_dict['once'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.dmg = 0
        self.level = 1#upgrade pointer

    def initiate(self):
        self.lifetime = 30
        if self.entity.dir[1] == 0:
            self.dir = self.entity.dir.copy()
        else:
            self.dir = [0,self.entity.dir[1]]
        self.velocity=[self.dir[0]*10,-self.dir[1]*10]
        self.update_hitbox()

    def collision_plat(self,platform):
        self.animation.reset_timer()
        self.currentstate.handle_input('Death')
        self.velocity=[0,0]

    def collision_enemy(self,collision_enemy):#if hit something
        self.animation.reset_timer()
        self.currentstate.handle_input('Death')
        self.velocity=[0,0]

        collision_enemy.velocity[0]=self.dir[0]*10#abs(push_strength[0])
        collision_enemy.velocity[1]=-6

class Arrow(Ranged):
    def __init__(self,entity):
        super().__init__(entity)
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/arrow/')
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        self.dmg = 1
        self.level = 1#upgrade pointer

    def initiate(self):#called when using the attack
        self.lifetime = 100
        if self.entity.dir[1] == 0:
            self.dir = self.entity.dir.copy()
        else:
            self.dir = [0,-self.entity.dir[1]]
        self.velocity=[self.dir[0]*30,self.dir[1]*30]
        self.update_hitbox()

    def collision_enemy(self,collision_enemy):
        collision_enemy.take_dmg(self.dmg)
        self.velocity=[0,0]
        self.kill()

    def collision_plat(self,platform):
        self.velocity=[0,0]
        self.dmg=0

    def rotate(self):#not in use
        angle=self.dir[0]*max(-self.dir[0]*self.velocity[0]*self.velocity[1],-60)

        self.image=pygame.transform.rotate(self.original_image,angle)#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

class Migawari():
    def __init__(self,entity):
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/migawari/')
        self.entity = entity
        self.game_objects = entity.game_objects#animation need dt
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

        self.health = 1
        self.level = 1#upgrade pointer

    def spawn(self,pos):#called when using the ability
        spawn = Migawari_entity(pos,self.entity.game_objects)
        spawn.set_health(self.health)
        spawn.set_lifetime(1000)
        self.entity.game_objects.players.add(spawn)

    def reset_timer(self):
        pass

    def upgrade_ability(self):#called from upgrade menu
        self.level += 1
        if self.level == 2:
            self.health = 2

class Slow_motion():
    def __init__(self,entity):
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/slow_motion/')
        self.entity = entity
        self.game_objects = entity.game_objects#animation need dt
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

        self.level = 1#upgrade pointer
        self.duration = 200#slow motion duration, in time [whatever units]

    def init(self,rate):#called from slow motion gameplay state
        if self.level == 3:#counteract slowmotion for aila
            self.entity.slow_motion = 1/rate
            self.duration = 400#slow motion duration, in time [whatever units]
        if self.level == 2:
            self.duration = 400#slow motion duration, in time [whatever units]

    def spawn(self):#called when using the ability from player states
        new_state = states.Slow_motion_gameplay(self.game_objects.game)
        new_state.enter_state()

    def upgrade_ability(self):#called from upgrade menu
        self.level += 1

    def reset_timer(self):
        pass

#things player can pickup
class Loot(Platform_entity):#
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.description = ''

    def update(self):
        super().update()
        self.update_vel()

    def update_vel(self):
        pass

    def attract(self,pos):#the omamori calls on this in loot group
        pass

class Heart_container(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/heart_container/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heart container'

    def update_vel(self):
        self.velocity[1] = 3*self.game_objects.game.dt*self.slow_motion

    def player_collision(self):
        self.game_objects.player.max_health += 1
        #a cutscene?
        self.kill()

class Spirit_container(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/spirit_container/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A spirit container'

    def update_vel(self):
        self.velocity[1]=3*self.game_objects.game.dt*self.slow_motion

    def player_collision(self):
        self.game_objects.player.max_spirit += 1
        #a cutscene?
        self.kill()

class Soul_essence(Loot):
    def __init__(self,pos,game_objects,ID_key = None):
        super().__init__(pos, game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/soul_essence/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'An essence container'#for shops
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def player_collision(self):
        self.game_objects.player.inventory['Soul_essence'] += 1
        self.game_objects.world_state.state[self.game_objects.map.level_name]['soul_essence'][self.ID_key] = 'gone'#write in the state file that this has been picked up
        #make a cutscene?
        self.kill()

    def update(self):
        super().update()
        obj1 = getattr(particles, 'Spark')(self.rect.center,self.game_objects,distance = 100,lifetime=20,vel={'linear':[2,4]},dir='isotropic',scale = 1, colour = [255,255,255,255])
        self.game_objects.cosmetics.add(obj1)

class Tungsten(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/tungsten/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heavy rock'

    def player_collision(self):
        self.game_objects.player.inventory['Tungsten'] += 1
        #a cutscene?
        self.kill()

class Spiritorb(Loot):#the thing that gives spirit
    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/spiritorbs/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()

    def player_collision(self):
        self.game_objects.player.add_spirit(1)
        self.kill()

class Enemy_drop(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.velocity = [random.uniform(-3, 3),-4]
        self.lifetime = 500

    def update_vel(self):#add gravity
        self.velocity[1] += 0.3*self.game_objects.game.dt*self.slow_motion

    def update(self):
        super().update()
        self.lifetime -= self.game_objects.game.dt*self.slow_motion
        self.destory()

    def attract(self,pos):#the omamori calls on this in loot group
        if self.lifetime < 350:
            self.velocity = [0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def player_collision(self,player):#when the player collides with this object
        if self.currentstate.__class__.__name__ == 'Death': return
        self.game_objects.sound.play_sfx(self.sounds.SFX['death'])#should be in states
        obj = (self.__class__.__name__)#get the string in question
        try:
            self.game_objects.player.inventory[obj] += 1
        except:
            self.game_objects.player.inventory[obj] = 1
        self.currentstate.handle_input('Death')

    #plotfprm collisions
    def down_collision(self,hitbox):
        super().down_collision(hitbox)
        self.velocity[0] = 0.5*self.velocity[0]
        self.velocity[1] = -0.3*self.velocity[1]

    def right_collision(self,hitbox):
        super().right_collision(hitbox)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self,hitbox):
        super().left_collision(hitbox)
        self.velocity[0] = -self.velocity[0]

    def limit_y(self):
        pass

class Amber_Droplet(Enemy_drop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = game_objects.object_pool.objects['Amber_Droplet'].sprites
        self.sounds = game_objects.object_pool.objects['Amber_Droplet'].sounds
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.true_pos = list(self.rect.topleft)
        self.hitbox = pygame.Rect(pos[0],pos[1],8,8)
        self.description = 'moneyy'

    def player_collision(self,player):#when the player collides with this object
        super().player_collision(player)
        self.game_objects.world_state.update_money_statistcis()

    @classmethod#called from object pool
    def pool(cls):#all things that should be saved in object pool
        obj = cls.__new__(cls)#creatate without runing initmethod
        obj.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/amber_droplet/')
        obj.sounds = Read_files.Sounds('Audio/SFX/enteties/items/amber_droplet/')
        return obj

class Bone(Enemy_drop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = game_objects.object_pool.objects['Bone'].sprites
        self.sounds = game_objects.object_pool.objects['Bone'].sounds
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.true_pos = list(self.rect.topleft)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.description = 'Ribs from my daugther. You can respawn and stuff'

    def use_item(self):
        if self.game_objects.player.inventory['Bone'] < 0: return#if we don't have bones
        self.game_objects.player.inventory['Bone'] -= 1
        if len(self.game_objects.player.spawn_point) == 2:#if there is already a bone planted somewhere
            self.game_objects.player.spawn_point.pop()
        self.game_objects.player.spawn_point.append({'map':self.game_objects.map.level_name, 'point':self.game_objects.player.abs_dist})
        self.game_objects.player.currentstate.enter_state('Plant_bone_main')

    @classmethod#called from object pool
    def pool(cls):#all things that should be saved in object pool
        obj = cls.__new__(cls)#creatate without runing initmethod
        obj.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/bone/')
        obj.sounds = Read_files.Sounds('Audio/SFX/enteties/items/bone/')
        return obj

class Heal_item(Enemy_drop):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = game_objects.object_pool.objects['Heal_item'].sprites
        self.sounds = game_objects.object_pool.objects['Heal_item'].sounds
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.true_pos = list(self.rect.topleft)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.description = 'Use it to heal'

    def use_item(self):
        if self.game_objects.player.inventory['Heal_item'] < 0: return
        self.game_objects.player.inventory['Heal_item'] -= 1
        self.game_objects.player.heal(1)

    @classmethod#called from object pool
    def pool(cls):#all things that should be saved in object pool
        obj = cls.__new__(cls)#creatate without runing initmethod
        obj.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/heal_item/')
        obj.sounds = Read_files.Sounds('Audio/SFX/enteties/items/heal_item/')
        return obj

#cosmetics
class Water_running_particles(Animatedentity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = game_objects.object_pool.objects['Water_running_particles'].sprites
        self.currentstate = states_basic.Death(self)
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    @classmethod#called from object pool
    def pool(cls):#all things that should be saved in object pool
        obj = cls.__new__(cls)#creatate without runing initmethod
        obj.sprites = Read_files.Sprites_Player('Sprites/animations/running_particles/water/')
        return obj

class Grass_running_particles(Animatedentity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = game_objects.object_pool.objects['Grass_running_particles'].sprites
        self.currentstate = states_basic.Death(self)
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

    @classmethod#called from object pool
    def pool(cls):#all things that should be saved in object pool
        obj = cls.__new__(cls)#creatate without runing initmethod
        obj.sprites = Read_files.Sprites_Player('Sprites/animations/running_particles/grass/')
        return obj

class Dust_running_particles(Animatedentity):#should make for grass, dust, water etc
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = game_objects.object_pool.objects['Dust_running_particles'].sprites
        self.currentstate = states_basic.Death(self)
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.true_pos = self.rect.topleft

    def reset_timer(self):
        self.kill()

    @classmethod#called from object pool
    def pool(cls):#all things that should be saved in object pool
        obj = cls.__new__(cls)#creatate without runing initmethod
        obj.sprites = Read_files.Sprites_Player('Sprites/animations/running_particles/dust/')
        return obj

class Player_Soul(Animatedentity):#the thing that popps out when player dies
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/soul/')
        self.currentstate = states_basic.Once(self)
        self.image = self.sprites.sprite_dict['once'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.timer=0
        self.velocity=[0,0]

    def update(self):
        super().update()
        self.update_pos()
        self.timer += self.game_objects.game.dt*self.slow_motion
        if self.timer > 100:#fly to sky
            self.velocity[1] = -20
        elif self.timer>200:
            self.kill()

    def update_pos(self):
        self.true_pos = [self.true_pos[0] + self.velocity[0], self.true_pos[1] + self.velocity[1]]

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Spawneffect(Animatedentity):#the thing that crets when aila re-spawns
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/GFX/spawneffect/')
        self.currentstate = states_basic.Once(self)#
        self.image = self.sprites.sprite_dict['once'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.finish = False
        #self.shader = shader_entities.Shader_entities(self)

    def update(self):
        super().update()

    def reset_timer(self):
        self.finish = True
        self.kill()

class Slash(Animatedentity):#thing that pop ups when take dmg or give dmg: GFX
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/GFX/slash/')
        state = str(random.randint(1, 3))
        self.currentstate.enter_state('Slash_' + state)
        self.image = self.sprites.sprite_dict['slash_' + state][0]
        self.rect = self.image.get_rect(center=pos)

    def reset_timer(self):
        self.kill()

class Rune_symbol(Animatedentity):#the stuff that will be blitted on uberrunestone
    def __init__(self,pos,game_objects,ID_key):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/rune_symbol/' + ID_key + '/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.center = pos

    def reset_timer(self):
        pass

class Thunder_aura(Animatedentity):#the auro around aila when doing the thunder attack
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/thunder_aura/')
        self.currentstate = states_basic.Once(self)#
        self.image = self.sprites.sprite_dict['once'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hitbox = self.rect.copy()#pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)

    def update(self):
        super().update()
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.inflate_ip(3,3)#the speed should match the animation
        self.hitbox[2]=min(self.hitbox[2],self.rect[2])
        self.hitbox[3]=min(self.hitbox[3],self.rect[3])

    def reset_timer(self):#called when animation is finished
        self.currentstate.handle_input('Idle')

class Pray_effect(Animatedentity):#the thing when aila pray
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/pray_effect/')
        self.currentstate = states_basic.Death(self)#
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def spawn(self):
        pass

class Health_bar(Animatedentity):
    def __init__(self,entity):
        super().__init__(entity.rect.center,entity.game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/health_bar/')
        self.entity = entity#the boss
        self.max_health = entity.health
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.width = self.rect[2]
        self.rect.topleft = [self.game_objects.game.WINDOW_SIZE[0]*0.5 - self.width*0.5,3]

    def resize(self):#in principle, should just be called when boss take dmg
        width = max(self.width * (self.entity.health/self.max_health),0)
        for index, sprite in  enumerate(self.sprites.sprite_dict['idle']):
            self.sprites.sprite_dict['idle'][index] = pygame.transform.scale(sprite,[width,self.rect[3]])

#interactables
class Interactable(Animatedentity):#interactables
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause
        self.true_pos = self.rect.topleft

    def update(self):
        super().update()
        self.group_distance()

    def interact(self):#when player press T
        pass

    def player_collision(self):#player collision
        pass

    def player_noncollision(self):#when player doesn't collide: for grass
        pass

    def take_dmg(self,projectile):#when player hits with sword
        pass

class Bridge(Interactable):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/bridge/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1])
        self.hitbox = self.rect.copy()
        platform = Collision_block(pos,(self.image.get_width(),32))
        self.game_objects.platforms.add(platform)

class Path_col(Interactable):
    def __init__(self, pos, game_objects,size, destination, spawn):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def update(self):
        self.group_distance()

    def player_collision(self):
        self.game_objects.load_map(self.destination, self.spawn)

class Path_inter(Interactable):
    def __init__(self, pos, game_objects, size, destination, spawn, image):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn

    def update(self):
        self.group_distance()

    def interact(self):
        self.game_objects.load_map(self.destination, self.spawn)

class Shade_trigger(Interactable):
    def __init__(self,pos,game_objects,size,colour):
        super().__init__(pos,game_objects)
        self.new_colour = [colour.g,colour.b,colour.a]
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/shade_trigger/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def update(self):
        pass

    def player_collision(self):#player collision
        for layer in self.layers_one:
            colour = self.new_colour + [layer.colour[-1]]
            layer.currentstate.enter_state('Turn',colour)
            self.layers_two.append(layer)
            self.layers_one.remove(layer)

    def player_noncollision(self):#when player doesn't collide: for grass
        for layer in self.layers_two:
            layer.currentstate.enter_state('Turn',layer.original_colour)
            self.layers_one.append(layer)
            self.layers_two.remove(layer)

    def add_shade_layers(self, layers):#called from map loader
        self.layers_one = layers#a list of shahde layers
        self.layers_two = []#similar to self.layer, keeps the layers of the shade screen

class Cutscene_trigger(Interactable):
    def __init__(self,pos,game_objects,size,event):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.event = event

    def update(self):
        pass
        #self.group_distance()

    def player_collision(self):
        if self.event not in self.game_objects.world_state.cutscenes_complete:#if the cutscene has not been shown before. Shold we kill the object instead?
            self.specific()
            new_game_state = states.Cutscenes(self.game_objects.game,self.event)
            new_game_state.enter_state()

    def specific(self):
        if self.event == 'Cultist_encounter':
            new_game_state = states.Cultist_encounter_gameplay(self.game_objects.game)
            new_game_state.enter_state()
        elif self.event == 'test':
            pass

class Interactable_bushes(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.interacted = False

    def player_collision(self):#player collision
        if self.interacted: return
        self.currentstate.handle_input('Hurt')
        self.interacted = True#sets to false when player gos away

    def take_dmg(self,projectile):
        self.currentstate.handle_input('Death')

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

    def player_noncollision(self):#when player doesn't collide
        self.interacted = False

class Cave_grass(Interactable_bushes):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/bushes/cave_grass/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

    def player_collision(self):
        if self.interacted: return
        self.currentstate.handle_input('Hurt')
        self.interacted = True#sets to false when player gos away
        self.release_particles()

    def take_dmg(self,projectile):
        super().take_dmg(projectile)
        self.release_particles(30)

    def release_particles(self,number_particles=12):#should release particles when hurt and death
        color = [255,255,255,255]
        for i in range(0,number_particles):
            obj1 = getattr(particles, 'Circle')(self.hitbox.center,self.game_objects,distance=30,lifetime=300,vel={'wave':[3,14]},dir='isotropic',scale=2,colour=color)
            self.game_objects.cosmetics.add(obj1)

class Runestones(Interactable):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/runestones/' + ID_key + '/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.true_pos = self.rect.topleft
        self.hitbox.midbottom = self.rect.midbottom

        if state != "idle":
            self.currentstate = states_basic.Interacted(self)

    def interact(self):
        if type(self.currentstate).__name__ == 'Interacted': return
        self.game_objects.player.currentstate.enter_state('Pray_pre')
        self.currentstate.handle_input('Transform')#goes to interacted after transform
        self.game_objects.world_state.state[self.game_objects.map.level_name]['runestone'][self.ID_key] = 'interacted'#write in the state dict that this has been picked up

    def reset_timer(self):#when animation finished
        self.game_objects.player.currentstate.handle_input('Pray_post')

class Uber_runestone(Interactable):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/uber_runestone/')
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.runestone_number = 0#a counter of number of activated runestrones
        self.count_runestones()

    def count_runestones(self):#append all runestone ID that have been activated.
        for level in self.game_objects.world_state.state.keys():
            for runestoneID in self.game_objects.world_state.state[level]['runestone'].keys():
                if self.game_objects.world_state.state[level]['runestone'][runestoneID] != 'idle':
                    pos = [self.rect.x+int(runestoneID)*16,self.rect.y]
                    self.game_objects.cosmetics.add(Rune_symbol(pos,runestoneID))
                    self.runestone_number += 1

    def interact(self):#when player press T
        if self.runestone_number == 25:
            pass#do a cutscene?

class Chest(Interactable):
    def __init__(self,pos,game_objects,state,ID_key):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/Chest/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health=3
        self.inventory = {'Amber_Droplet':3}
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}
        self.hitbox.midbottom = self.rect.midbottom

        if state != "idle":
            self.currentstate = states_basic.Interacted(self)

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def loots(self):#this is called when the opening animation is finished
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                #obj = self.game_objects.object_pool.spawn(key)
                obj = getattr(sys.modules[__name__], key)(self.hitbox.midtop, self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def reset_timer(self):#when animation is finished
        self.currentstate.handle_input('Idle')

    def take_dmg(self,projectile):
        if self.invincibile: return
        projectile.clash_particles(self.hitbox.center)
        self.health -= 1
        self.timer_jobs['invincibility'].activate()

        if self.health > 0:
            self.currentstate.handle_input('Hurt')
        else:
            self.currentstate.handle_input('Opening')
            self.game_objects.world_state.state[self.game_objects.map.level_name]['chest'][self.ID_key] = 'interacted'#write in the state dict that this has been picked up

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Door(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/Door/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

class Collision_breakable(Interactable):#a breakable collision block
    def __init__(self, pos,game_objects,type = 'type1'):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/block/breakable/'+type+'/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}
        self.health = 3

    def player_collision(self):#only sideways collision checks, for now
        sign=(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
        if sign>0:#plaer on right
            self.game_objects.player.hitbox.left = self.hitbox.right
        else:#plyer on left
            self.game_objects.player.hitbox.right = self.hitbox.left
        self.game_objects.player.update_rect_x()

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def dead(self):#called when death animatin finishes
        self.kill()

    def take_dmg(self,projectile):
        if self.invincibile: return
        self.health -= 1
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
        projectile.clash_particles(self.hitbox.center)

        if self.health > 0:#check if dead¨
            self.animation.handle_input('Hurt')#turn white
            self.game_objects.camera.camera_shake(3,10)
        else:#if dead
            if self.currentstate.state_name != 'death':#if not already dead
                self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
                self.currentstate.enter_state('Death')#overrite any state and go to deat

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Savepoint(Interactable):#save point
    def __init__(self,pos,game_objects,map):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/animations/savepoint/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        if type(self.currentstate).__name__ == 'Outline':#single click
            self.game_objects.player.currentstate.enter_state('Pray_pre')
            self.game_objects.player.spawn_point[0]['map']=self.map
            self.game_objects.player.spawn_point[0]['point']=self.init_cord
            self.currentstate.handle_input('Once')
        else:#odoulbe click
            self.game_objects.player.currentstate.handle_input('special')
            new_state = states.Facilities(self.game_objects.game,'Spirit_upgrade_menu')
            new_state.enter_state()

    def reset_timer(self):#when animation finished
        self.game_objects.player.currentstate.handle_input('Pray_post')

class Inorinoki(Interactable):#the place where you trade soul essence for spirit or heart contrainer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/inorinoki/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()

    def interact(self):#when player press t/y
        new_state = states.Soul_essence(self.game_objects.game)
        new_state.enter_state()

class Fast_travel(Interactable):#save point
    cost = 50
    def __init__(self,pos,game_objects,map):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/fast_travel/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

        try:#if it has been unlocked
            self.game_objects.world_state.travel_points[map]
            self.locked = False
        except:
            self.locked = True#starts locked. After paying some ambers, it unlocks and fast travel is open

    def unlock(self):#called from Fast_travel_unlock
        if self.game_objects.player.inventory['Amber_Droplet'] > self.cost:
            self.game_objects.player.inventory['Amber_Droplet'] -= self.cost
            self.locked = False
            Fast_travel.cost *= 5#increase by 5 for every unlock
            self.game_objects.world_state.save_travelpoint(self.map,self.init_cord)#self.game_objects.player.abs_dist)
            return True
        else:
            return False

    def interact(self):#when player press t/y
        if self.locked:
            type = 'Fast_travel_unlock'
            new_state = states.Facilities(self.game_objects.game,type,self)
        else:
            type = 'Fast_travel_menu'
            self.currentstate.handle_input('Once')
            new_state = states.Facilities(self.game_objects.game,type)
        new_state.enter_state()

class Rhoutta_altar(Interactable):#altar to trigger the cutscane at the beginning
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/rhoutta_altar/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox=self.rect.copy()

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Once')
        new_game_state = states.Cutscenes(self.game_objects.game,'Rhoutta_encounter')
        new_game_state.enter_state()

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Sign(Interactable):
    def __init__(self,pos,game_objects,directions):
        super().__init__(pos,game_objects)
        self.directions = directions
        self.sprites = Read_files.Sprites_Player('Sprites/animations/sign/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox=self.rect.copy()
        self.symbols = Sign_symbols(self)

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def player_noncollision(self):#when player doesn't collide
        self.symbols.finish()
        self.currentstate.handle_input('Idle')

    def interact(self):#when player press t/y
        if self.symbols in self.game_objects.cosmetics:
            self.symbols.finish()
        else:
            self.symbols.init()
            self.game_objects.cosmetics.add(self.symbols)

class Light_crystal(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/light_crystals/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}
        self.dark_glow = Dark_glow
        self.light_glow = Light_glow

    def update(self):
        super().update()
        self.update_timers()#invincibililty

    def take_dmg(self,projectile):
        if self.invincibile: return
        projectile.clash_particles(self.hitbox.center)
        self.timer_jobs['invincibility'].activate()
        self.currentstate.handle_input('Transform')
        self.game_objects.cosmetics.add(self.dark_glow(self))#should be when interacted state is initialised and not on taking dmg
        self.game_objects.cosmetics.add(self.light_glow(self))#should be when interacted state is initialised

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Fireplace(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/fireplace/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Interact')#goes to interacted after transform

class Lighitning_barrier(Interactable):#traps
    def __init__(self,pos,game_objects,size):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/lighitning_barrier/')
        if size != [16,16]:
            self.scale(size)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],16,self.rect[3])

    def player_collision(self):#player collision
        self.game_objects.player.take_dmg(1)
        self.game_objects.player.currentstate.handle_input('interrupt')#interupts dash
        sign=(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
        if sign>0:
            self.game_objects.player.knock_back([1,0])
        else:
            self.game_objects.player.knock_back([-1,0])

    def scale(self,size):
        for index,spirte in enumerate(self.sprites.sprite_dict['idle']):
            self.sprites.sprite_dict['idle'][index] = pygame.transform.scale(spirte,size)

class Spirit_spikes(Interactable):#traps
    def __init__(self,pos,game_objects,size):
        super().__init__(pos,game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = Read_files.Sprites_Player('Sprites/animations/traps/spirit_spikes/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1])
        self.hitbox = pygame.Rect(pos[0],pos[1],self.rect[2],16)
        self.size = [32,32]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self):#player collision
        self.currentstate.handle_input('Death')

class Lightning_spikes(Interactable):#traps
    def __init__(self,pos,game_objects,size):
        super().__init__(pos,game_objects)
        self.currentstate = states_traps.Idle(self)#
        self.sprites = Read_files.Sprites_Player('Sprites/animations/traps/lightning_spikes/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1])
        self.hitbox = pygame.Rect(pos[0],pos[1],26,16)
        self.size = [64,64]#hurtbox size
        self.hurt_box = Hurt_box
        self.dmg = 1

    def player_collision(self):#player collision
        self.currentstate.handle_input('Once')

#equipable items
class Infinity_stones():
    def __init__(self,sword):
        self.sword = sword
        self.game_objects = sword.game_objects
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.description = ''

    def set_pos(self, pos):
        self.rect.center = pos

    def reset_timer(self):
        pass

    def attach(self):#called from sword when balcksmith attached the stone
        pass

    def detach(self):
        pass

    def collision(self):#hit enemy
        pass

    def slash(self):#called when swingin sword
        pass

class Red_infinity_stone(Infinity_stones):#more dmg
    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/red/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'red'
        self.description = '10 procent more damage'

    def attach(self):
        self.sword.dmg*=1.1

    def detach(self):
        self.sword.dmg*=(1/1.1)

class Green_infinity_stone(Infinity_stones):#faster slash (changing framerate)
    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/green/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'green'
        self.description = 'fast sword swings'

    def slash(self):
        self.sword.entity.animation.framerate = 0.33

class Blue_infinity_stone(Infinity_stones):#get spirit at collision
    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/blue/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'blue'
        self.description = 'add spirit to the swinger'

    def collision(self):
        self.sword.entity.add_spirit()

class Orange_infinity_stone(Infinity_stones):#bigger hitbox
    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/orange/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'orange'
        self.description = 'larger hitbox'

    def detach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y,40,40)
        self.sword.hitbox = self.sword.rect.copy()

    def attach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y,80,40)
        self.sword.hitbox = self.sword.rect.copy()

class Purple_infinity_stone(Infinity_stones):#reflect projectile
    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/purple/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'purple'
        self.description = 'reflects projectiels'

    def attach(self):
        pass

    def detach(self):
        pass

class Omamoris():#omamori handler
    def __init__(self,entity):
        self.entity = entity
        self.equipped = {}#equiped omamoris
        self.inventory = {'Half_dmg':Half_dmg(entity),'Loot_magnet':Loot_magnet(entity),'Boss_HP':Boss_HP(entity)}#omamoris in inventory.
        self.number = 3#number of omamori we can equip
        entity.dmg_scale = 1

    def update(self):
        for omamori in self.equipped.values():
            omamori.update()

    def handle_input(self,input):
        for omamori in self.equipped.values():
            omamori.handle_input(input)

    def equip_omamori(self,omamori_string):
        if not self.equipped.get(omamori_string,False):#if it is not equipped
            if len(self.equipped) < self.number:#maximum number of omamoris to equip
                new_omamori = getattr(sys.modules[__name__], omamori_string)(self.entity)#make a class based on the name of the newstate: need to import sys
                self.equipped[omamori_string] = new_omamori
                self.inventory[omamori_string].currentstate.handle_input('Equip')
                new_omamori.attach()
        else:##if equiped -> remove
            self.inventory[omamori_string].currentstate.handle_input('Idle')
            self.equipped[omamori_string].detach()#call the detach function of omamori
            del self.equipped[omamori_string]

class Omamori():
    def __init__(self,entity):
        self.entity = entity
        self.game_objects = entity.game_objects
        self.dir = [1,0]
        self.animation = animation.Entity_animation(self)#it is called from inventory
        self.currentstate = states_basic.Idle(self)#
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.description = ''#for inventory

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def detach(self):
        self.currentstate.handle_input('Idle')

    def attach(self):
        self.currentstate.handle_input('Equip')

    def reset_timer(self):
        pass

    def set_pos(self,pos):#for inventory
        self.rect.center = pos

class Half_dmg(Omamori):
    def __init__(self,entity):
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/double_jump/')#for inventory
        super().__init__(entity)
        self.description = 'Take half dmg'

    def attach(self):
        super().attach()
        self.entity.dmg_scale = 0.5

    def detach(self):
        super().detach()
        self.entity.dmg_scale = 1

class Loot_magnet(Omamori):
    def __init__(self,entity):
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/loot_magnet/')#for inventory
        super().__init__(entity)
        self.description = 'Attracts loot'

    def update(self):
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

class Boss_HP(Omamori):
    def __init__(self,entity):
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/boss_HP/')#for inventory
        super().__init__(entity)
        self.description = 'Visible boss HP'

    def attach(self):
        super().attach()
        for enemy in self.entity.game_objects.enemies.sprites():
            enemy.health_bar()#attached a healthbar on boss

#timer toools: activate with the attrubute activate, which will run until the specified duration is run out
class Timer():
    def __init__(self,entity,duration):
        self.entity = entity
        self.duration = duration

    def activate(self):#add timer to the entity timer list
        if self in self.entity.timers: return#do not append if the timer is already inside
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self not in self.entity.timers: return#do not remove if the timer is not inside
        self.entity.timers.remove(self)

    def update(self):
        self.lifetime -= self.entity.game_objects.game.dt*self.entity.slow_motion
        if self.lifetime < 0:
            self.deactivate()

class Invincibility_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.entity.invincibile = False#a flag to check if one should take damage

    def activate(self):#called when taking a dmg
        super().activate()
        self.entity.invincibile = True

    def deactivate(self):
        super().deactivate()
        self.entity.invincibile = False

class Sword_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.entity.sword_swinging = False#a flag to make sure you can only swing sword when this is False

    def activate(self):#called when sword is swang
        super().activate()
        self.entity.sword_swinging = True

    def deactivate(self):
        super().deactivate()
        self.entity.sword_swinging = False

class Jump_timer(Timer):#can be combined with shroomjump?
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def update(self):#called everyframe after activation (activated after pressing jump)
        if self.entity.ground:#when landing on a plarform: enters once
            self.entity.ground = False
            self.entity.timer_jobs['air'].activate()
            self.deactivate()
        super().update()#need to be after

class Air_timer(Timer):#activated when jumped. It keeps a constant vertical velocity for the duration. Needs to be deactivated when releasing jump bottom
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def update(self):#called everyframe after activation (activated after jumping)
        self.entity.velocity[1] = C.jump_vel_player
        super().update()#need to be after

class Ground_timer(Timer):#a timer to check how long time one has not been on ground
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.entity.ground = True

    def activate(self):#called when entering fall run or fall stand
        if self.entity.ground:#if we fall from a plotform
            super().activate()

    def deactivate(self):#called when timer runs out
        super().deactivate()
        self.entity.ground = False

class Shroomjump_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)
        self.shrooming = False

    def activate(self):#called when pressed jump putton and/or landing on a shroom
        if self.shrooming:#second time entering (pressing or landing on shroom)
            self.entity.velocity[1] = -15
            return
        super().activate()
        self.shrooming = True

    def deactivate(self):#called when timer expires
        super().deactivate()
        self.shrooming = False
