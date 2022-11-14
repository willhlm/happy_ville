import pygame, random, sys, Read_files, states, particles, animation, states_basic, states_player, states_NPC, states_enemy, states_vatt, states_reindeer, states_bluebird, states_kusa, states_rogue_cultist, AI_wall_slime, AI_shroompoline, AI_vatt, AI_kusa, AI_bluebird, AI_enemy, AI_reindeer, math, sound
import time
import constants as C

pygame.mixer.init()

class PauseGroup(pygame.sprite.Group):#the pause group when enteties are outside the boundaries
    def __init__(self):
        super().__init__()

    def update(self, pos):
        for s in self.sprites():
            self.group_distance(s,pos)

    @staticmethod
    def group_distance(s,pos):
        if s.rect[0]<s.bounds[0] or s.rect[0]>s.bounds[1] or s.rect[1]<s.bounds[2] or s.rect[1]>s.bounds[3]:#this means it is outside of screen
            s.update_pos(pos)
        else:
            s.add(s.group)#add to group
            s.remove(s.pause_group)#remove from pause

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self,pos,size = (16,16)):
        super().__init__()
        self.rect = pygame.Rect(pos,size)
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center = self.rect.center

    def take_dmg(self):
        pass

class Invisible_block(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_y(self,entity):
        pass

    def collide_x(self,entity):
        if type(entity).__name__ != "Player":#only apply to enemies and NPC
            entity.dir[0] = -entity.dir[0]#turn around

class Collision_block(Platform):
    def __init__(self,pos,size, run_particle = 'dust'):
        super().__init__(pos,size)
        self.run_particles = {'dust':Dust_running_particles,'water':Water_running_particles,'grass':Grass_running_particles}[run_particle]

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.right_collision(self.hitbox.left)
        else:#going to the left
            entity.left_collision(self.hitbox.right)
        entity.update_rect()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self.hitbox.top)
            entity.running_particles = self.run_particles#save the particles to make
        else:#going up
            entity.top_collision(self.hitbox.bottom)
        entity.update_rect()

class Collision_oneway_up(Platform):
    def __init__(self,pos,size,run_particle = 'dust'):
        super().__init__(pos,size)
        self.run_particles = {'dust':Dust_running_particles,'water':Water_running_particles,'grass':Grass_running_particles}[run_particle]

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        offset = entity.velocity[1]+1
        if entity.velocity[1]>0:#going down
            if entity.hitbox.bottom<self.hitbox.top+offset:
                entity.down_collision(self.hitbox.top)
                entity.running_particles = self.run_particles#save the particles to make
                entity.update_rect()
        else:#going up
            pass

class Collision_right_angle(Platform):
    def __init__(self,pos,points):
        self.define_values(pos, points)
        super().__init__(self.new_pos,self.size)
        self.ratio = self.size[1]/self.size[0]
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
            self.shift_up(rel_x,other_side,entity)
        elif self.orientation == 0:
            rel_x = self.hitbox.right - entity.hitbox.left
            other_side = self.hitbox.left - entity.hitbox.left
            self.shift_up(rel_x,other_side,entity)
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
            entity.velocity[1] = 1 #need to have a value to avoid "dragin in air" while running
            entity.update_rect()

    def shift_up(self,rel_x,other_side,entity):
        target = -rel_x*self.ratio + self.hitbox.bottom

        if other_side > 0:
            if entity.hitbox.bottom > target:
                entity.go_through = True
            else:
                entity.go_through = False

        elif entity.hitbox.bottom < target:
            entity.go_through = False

        if not entity.go_through:
            if entity.hitbox.bottom > target:
                entity.down_collision(target)
                entity.update_rect()

class Spikes(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.image = pygame.image.load("Sprites/block/spikes/spkies.png").convert_alpha()
        self.dmg = 10

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.velocity[0] = -6#knock back
        else:#going to the left
            entity.velocity[0] = 6#knock back
        entity.take_dmg(self.dmg)

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.velocity[1] = -6#knock back
        else:#going up
            entity.velocity[1] = 6#knock back
        entity.take_dmg(self.dmg)

class Staticentity(pygame.sprite.Sprite):#no hitbox but image
    def __init__(self,pos,img=pygame.Surface((16,16))):
        super().__init__()
        self.image = img.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.bounds = [-200,800,-100,350]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]

    def group_distance(self):#instead of bound, could calculate distance from center. But maybe cost
        if self.rect[0]<self.bounds[0] or self.rect[0]>self.bounds[1] or self.rect[1]<self.bounds[2] or self.rect[1]>self.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause

class BG_Block(Staticentity):
    def __init__(self,pos,img,parallax = 1):
        super().__init__(pos,img)
        self.true_pos = self.rect.bottomleft
        self.parallax = parallax

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + self.parallax[0]*pos[0], self.rect.topleft[1] + self.parallax[1]*pos[1]]
        self.true_pos = [self.true_pos[0] + self.parallax[0]*pos[0], self.true_pos[1] + self.parallax[1]*pos[1]]
        self.rect.topleft = self.true_pos

class BG_Animated(BG_Block):
    def __init__(self,pos,sprite_folder_path,parallax=(1,1)):
        super().__init__(pos,pygame.Surface((16,16)),parallax)
        self.sprites = Read_files.load_sprites(sprite_folder_path)
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

    def update(self, pos):
        self.update_pos(pos)
        self.animation.update()

    def reset_timer(self):
        pass

class Dynamicentity(Staticentity):
    def __init__(self,pos):
        super().__init__(pos)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = False#a flag for entities to go through ramps from side or top
        self.velocity = [0,0]
        self.running_particles = 'dust'

    def update(self,pos):
        super().update(pos)
        self.update_vel()

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.bottom = self.rect.bottom

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom#[self.rect.bottom + self.hitbox_offset[0], self.rect.bottom + self.hitbox_offset[1]]

    def update_rect(self):
        self.rect.midbottom = self.hitbox.midbottom#[self.hitbox.bottom - self.hitbox_offset[0], self.hitbox.bottom - self.hitbox_offset[1]]

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.midbottom = self.rect.midbottom

    def update_vel(self):
        pass

    #pltform collisions.
    def right_collision(self,hitbox):
        self.hitbox.right = hitbox
        self.collision_types['right'] = True

    def left_collision(self,hitbox):
        self.hitbox.left = hitbox
        self.collision_types['left'] = True

    def down_collision(self,hitbox):
        self.hitbox.bottom = hitbox
        self.collision_types['bottom'] = True

    def top_collision(self,hitbox):
        self.hitbox.top = hitbox
        self.collision_types['top'] = True
        self.velocity[1] = 0

class Character(Dynamicentity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.acceleration = [0,C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()
        self.animation_stack = [animation.Entity_animation(self)]

        self.invincibile = False#a flag to check if one should take damage
        self.timers=[]#a list containing timers, e.g. jump, invincibility etc.

    def update(self,pos):
        super().update(pos)
        self.currentstate.update()
        self.animation_stack[-1].update()
        self.update_timers()

    def update_vel(self):
        self.velocity[1]+=self.acceleration[1]-self.velocity[1]*self.friction[1]#gravity
        self.velocity[1]=min(self.velocity[1],self.max_vel[1])#set a y max speed

        self.velocity[0]+=self.dir[0]*self.acceleration[0]-self.friction[0]*self.velocity[0]

    def take_dmg(self,dmg):
        if self.invincibile: return
        self.health -= dmg
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
        self.hurt()

    def hurt(self):
        if self.health > 0:#check if dead¨
            self.animation_stack[-1].handle_input('Hurt')#turn white
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
        else:#if dead
            if self.currentstate.state_name != 'death' and self.currentstate.state_name != 'dead':#if not already dead
                self.aggro = False
                self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
                self.currentstate.enter_state('Death')#overrite any state and go to deat

    def knock_back(self,dir):
        self.velocity[0] = dir*30

    def hurt_particles(self,distance=0,lifetime=20,vel=[1,10],type='circle',dir='isotropic',scale=1,colour=[255,255,255,255],number_particles=12):
        for i in range(0,number_particles):
            obj1=particles.General_particle(self.hitbox.center,distance,lifetime,vel,type,dir,scale,colour)
            self.game_objects.cosmetics.add(obj1)

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Player(Character):

    sfx_sword = pygame.mixer.Sound("Audio/SFX/utils/sword_3.ogg")

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/aila/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes

        self.max_health = 250
        self.max_spirit = 100
        self.health = 30
        self.spirit = 100

        self.projectiles = game_objects.fprojectiles

        self.abilities = {'Thunder':Thunder,'Force':Force,'Arrow':Arrow,'Heal':Heal,'Darksaber':Darksaber}#the objects are referensed but created in states
        self.equip = 'Thunder'#ability pointer
        self.sword = Aila_sword(self)

        self.states = set(['Dash','Idle','Walk','Jump_run','Jump_stand','Fall_run','Fall_stand','Death','Invisible','Hurt','Spawn','Sword_run1','Sword_run2','Sword_stand1','Sword_stand2','Air_sword2','Air_sword1','Sword_up','Sword_down','Plant_bone','Thunder','Force','Heal','Darksaber','Arrow','Counter'])#all states that are available to Aila, convert to set to make lookup faster
        self.currentstate=states_player.Idle(self)

        self.spawn_point = [{'map':'light_forest1', 'point':'1'}]#a list of max len 2. First elemnt is updated by sejt interaction. Can append positino for bone, which will pop after use
        self.inventory = {'Amber_Droplet':23,'Bone':2,'Soul_essence':10,'Tungsten':10}#the keys need to have the same name as their respective classes
        self.omamoris = Omamoris(self)

        self.set_abs_dist()

        self.sword_swing = 0#a flag to check which swing we are at (0 or 1)
        self.jumping = False#a flag to check so that you cannot jump in air
        self.sword_swinging = False#a flag to make sure you can only swing sword when this is False

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_player),'jump':Jump_timer(self,C.jump_time_player),'sword':Sword_timer(self,C.sword_time_player)}

    def down_collision(self,hitbox):#when colliding with platform beneth
        super().down_collision(hitbox)
        self.velocity[1] = 0
        self.jumping = False

    def hurt(self):#called when taking dmg
        if self.health > 0:#check if dead¨
            self.animation_stack[-1].handle_input('Invincibile')#make some animation. should be first
            self.animation_stack[-1].handle_input('Hurt')#turn white
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            self.hurt_particles(lifetime=40,vel=[3,8],colour=[0,0,0,255],scale=3,number_particles=60)
            self.game_objects.cosmetics.add(Slash(self.hitbox.center))#make a slash animation
            self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
        else:#if health < 0
            self.game_objects.game.state_stack[-1].handle_input('death')#depending on gameplay state, different death stuff should happen

    def death(self):#"normal" gameplay states calls this
        if self.currentstate.state_name != 'death':#if not already dead
            self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
            self.currentstate.enter_state('Death')#overrite any state and go to deat

    def dead(self):#called when death animation is finished
        new_game_state = states.Cutscenes(self.game_objects.game,'Death')
        new_game_state.enter_state()
        self.set_abs_dist()

    def set_abs_dist(self):#the absolute distance, i.e. the total scroll
        self.abs_dist = C.player_center.copy()#the coordinate for buring the bone

    def enter_idle(self):
        self.currentstate = states_player.Idle(self)

    def reset_movement(self):#called when loading new map or entering conversations
        self.velocity = [0,0]
        self.acceleration =  [0,C.acceleration[1]]
        self.friction = C.friction_player.copy()

    def update(self,pos):
        super().update(pos)
        self.abs_dist = [self.abs_dist[0] - pos[0], self.abs_dist[1] - pos[1]]
        self.omamoris.update()

    def to_json(self):#things to save: needs to be a dict
        health = {'max_health':self.max_health,'max_spirit':self.max_spirit,'health':self.health,'spirit':self.spirit}

        abilities = {}
        for key,ability in self.abilities.items():
            abilities[key] = True

        save_dict = {'spawn_point':self.spawn_point,'inventory':self.inventory,'health':health,'abilities':abilities,'states':self.states}
        return save_dict

    def from_json(self,data):#things to load. data is a dict
        self.max_health=data['health']['max_health']
        self.max_spirit=data['health']['max_spirit']
        self.health=data['health']['health']
        self.spirit=data['health']['spirit']

        self.states=data['states']
        self.inventory=data['inventory']

        self.abilities={}
        for ability in data['abilities'].keys():
                self.abilities[ability] = getattr(sys.modules[__name__], ability)

class Enemy(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause

        self.currentstate = states_enemy.Idle(self)
        self.AI_stack = [AI_enemy.Peace(self)]

        self.inventory = {'Amber_Droplet':random.randint(0, 10),'Bone':2}
        self.spirit = 100
        self.health = 100

        self.aggro = True#colliding with player
        self.dmg = 10#projectile damage

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

        #move these to AI classes?
        self.attack_distance = 0#when try to hit
        self.aggro_distance = 200#when ot become aggro

    def update(self,pos):
        super().update(pos)
        self.AI_stack[-1].update()#tell what the entity should do
        self.group_distance()

    def player_collision(self):#when player collides with enemy
        if not self.aggro:
            return
        if not self.game_objects.player.invincibile and not self.game_objects.player.currentstate.state_name == 'death':
            self.game_objects.player.take_dmg(10)
            sign=(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
            if sign>0:
                self.game_objects.player.knock_back(1)
            else:
                self.game_objects.player.knock_back(-1)

    def dead(self):#called when death animation is finished
        self.loots()
        self.game_objects.statistics['kill'][type(self).__name__.lower()] += 1#add to kill statisics
        if self.game_objects.statistics['kill'][type(self).__name__.lower()] > 100:
            for omamori in self.game_objects.player.omamoris.omamori_list:
                omamori.level_up()
        self.kill()

    def loots(self):#called when dead
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)([self.rect.x,self.rect.y],self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def countered(self):#player shield
        self.velocity[0] = -30*self.dir[0]
        self.currentstate = states_enemy.Stun(self,duration=30)#should it overwrite?

class Collision_breakable(Enemy):#a breakable collision block
    def __init__(self, pos,game_objects,type = 'type1'):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/block/breakable/'+type+'/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)

        self.health = 40

    def player_collision(self):#only sideways collision checks, for now
        sign=(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
        if sign>0:#plaer on right
            self.game_objects.player.hitbox.left = self.hitbox.right
        else:#plyer on left
            self.game_objects.player.hitbox.right = self.hitbox.left
        self.game_objects.player.update_rect()

    def knock_back(self,dir):
        pass

    def update(self,pos):
        self.update_pos(pos)
        self.currentstate.update()
        self.animation_stack[-1].update()
        self.update_timers()
        self.group_distance()

    def dead(self):#called when death animatin finishes
        self.kill()

class Slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.health = 50

class Wall_slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_wallslime('Sprites/Enteties/enemies/wall_slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()#pygame.Rect(pos[0],pos[1],16,16)
        self.health = 50
        self.currentstate.enter_state('Walk')
        self.AI_stack = [AI_wall_slime.Peace(self)]

    def knock_back(self,dir):
        pass

    def update_vel(self):
        self.velocity[1]=self.acceleration[1]-self.dir[1]
        self.velocity[0]=self.acceleration[0]+self.dir[0]

class Woopie(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.health = 1
        self.spirit=100
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')

class Vatt(Enemy):

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/vatt/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)
        self.health = 30
        self.spirit = 30
        self.aggro = False
        self.currentstate = states_vatt.Idle(self)
        self.attack_distance = 60
        self.AI_stack = [AI_vatt.Peace(self)]

    def turn_clan(self):#this is acalled when tranformation is finished
        for enemy in self.game_objects.enemies.sprites():
            if type(enemy).__name__=='Vatt':
                enemy.aggro = True
                enemy.currentstate.handle_input('Transform')

class Flowy(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = pygame.image.load("Sprites/Enteties/enemies/flowy/main/Idle/Stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/flowy/')
        self.spirit=10

class Larv(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/larv/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.health = 40
        self.spirit=10
        self.attack=Poisonblobb
        self.attack_distance=150

class Blue_bird(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/animals/bluebird/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate = states_bluebird.Idle(self)
        self.aggro=False
        self.health=1
        self.AI_stack = [AI_bluebird.Peace(self)]

    def knock_back(self,dir):
        pass

class Shroompolin(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/shroompolin/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box=pygame.Rect(pos[0],pos[1],32,10)
        self.aggro=False
        self.invincibile=True
        self.AI_stack = [AI_shroompoline.Peace(self)]

    def player_collision(self):
        offset=9
        if self.game_objects.player.velocity[1]>0:#going down
            if self.game_objects.player.hitbox.bottom<self.jump_box.top+offset:
                self.game_objects.player.velocity[1] = -10
                self.currentstate.enter_state('Hurt')

    def update_hitbox(self):
        super().update_hitbox()
        self.jump_box.midtop = self.rect.midtop

class Kusa(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/kusa/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = 30
        self.health = 1
        self.AI_stack = [AI_kusa.Peace(self)]

    def suicide(self):
        self.projectiles.add(Explosion(self,dmg=10))
        self.game_objects.camera[-1].camera_shake(amp=2,duration=30)#amplitude and duration

class Svampis(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/svampis/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],32,32)
        self.currentstate = states_kusa.Idle(self)
        self.attack_distance = 30
        self.health = 1
        self.AI_stack = [AI_kusa.Peace(self)]

    def suicide(self):
        self.projectiles.add(Explosion(self,dmg=10))
        self.game_objects.camera[-1].camera_shake(amp=2,duration=30)#amplitude and duration

class Egg(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/egg/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],64,64)
        self.health = 1
        self.number = random.randint(1, 4)
        self.aggro_distance = -1 #if negative, it will not go into aggro

    def knock_back(self,dir):
        pass

    def death(self):
        self.spawn_minions()
        self.kill()

    def spawn_minions(self):
        for i in range(0,self.number):
            pos=[self.hitbox.centerx,self.hitbox.centery-10]
            obj=Slime(pos,self.game_objects)
            obj.velocity=[random.randint(-100, 100),random.randint(-10, -5)]
            self.game_objects.enemies.add(obj)

class Skeleton_warrior(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/skeleton_warrior/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,40)
        self.health = 50
        self.attack_distance = 100
        self.attack = Sword

    def knock_back(self,dir):
        pass

class Liemannen(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/liemannen/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,40)
        self.health = 50
        self.attack_distance = 100
        self.attack = Sword

    def knock_back(self,dir):
        pass

class Skeleton_archer(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/skeleton_archer/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],40,40)
        self.health = 50
        self.attack_distance = 300
        self.attack = Arrow
        self.aggro_distance = 400

    def knock_back(self,dir):
        pass

class Cultist_rogue(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/cultist_rogue/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 50
        self.attack_distance = 80
        self.attack = Sword
        self.currentstate = states_rogue_cultist.Idle(self)

class Cultist_warrior(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/cultist_warrior/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 50
        self.attack_distance = 80
        self.attack = Sword

class John(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/john/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,40)
        self.health = 50
        self.attack_distance = 80
        self.attack = Sword

class NPC(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.group = game_objects.npcs
        self.pause_group = game_objects.entity_pause
        self.name = str(type(self).__name__)#the name of the class
        self.conv_index = 0
        self.currentstate = states_NPC.Idle(self)

        self.sprites = Read_files.Sprites_Player("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.image = self.sprites.get_image('idle', 0, self.dir, 'main')
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/' + self.name +'/potrait.png').convert_alpha()  #temp
        self.load_conversation()
        self.counter = 0
        self.state = 'state_1'#a flag to decide what do say. Should we have a world state instead?

    def load_conversation(self):
        self.conversation = Read_files.read_json("Text/NPC/" + self.name + ".json")

    def get_conversation(self):#returns the conversation depending on the NPC state and conversation index
        try:
            conv = self.conversation[self.game_objects.world_state][str(self.conv_index)]
        except:
            self.conv_index -= 1
            return None
        return conv

    def reset_conv_index(self):
        self.conv_index = 0

    def increase_conv_index(self):
        self.conv_index += 1

    def update(self,pos):
        super().update(pos)
        self.AI()
        self.group_distance()

    def interact(self):#when plater press t
        new_state = states.Conversation(self.game_objects.game, self)
        new_state.enter_state()

    def idle(self):
        self.currentstate.handle_input('Idle')

    def walk(self):
        self.currentstate.handle_input('Walk')

    def AI(self):
        self.counter += 1
        if self.counter > 100:
            self.counter = 0
            rand=random.randint(0,1)
            if rand == 0:
                self.idle()
            else:
                self.walk()

    def buisness(self):#enters after conversation
        pass

class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        if self.game_objects.world_state == 'state_2':#if player has deafated the reindeer
            if 'Wall' not in self.game_objects.player.states:#if player doesn't have wall yet
                new_game_state = states.New_ability(self.game_objects.game,'wall')
                new_game_state.enter_state()
                self.game_objects.player.states.add('Wall')#append wall abillity to available states

class Sahkar(NPC):#deer handler
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_Droplet':1}#itam+price

    def buisness(self):#enters after conversation
        new_state = states.Vendor(self.game_objects.game, self)
        new_state.enter_state()

class MrSmith(NPC):#balck smith
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):#enters after conversation
        new_state = states.Smith(self.game_objects.game, self)
        new_state.enter_state()

class MrBanks(NPC):#bank
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.ammount = 0

    def buisness(self):#enters after conversation
        new_state = states.Bank(self.game_objects.game, self)
        new_state.enter_state()

class Bridge_keeper(NPC):#bridge block spawn this
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def dead(self):
        self.aggro = False
        self.AI_stack[-1].set_AI('Nothing')
        self.loots()
        self.give_abillity()
        self.game_objects.increase_world_state()
        new_game_state = states.New_ability(self.game_objects.game,self.abillity)
        new_game_state.enter_state()
        new_game_state = states.Cutscenes(self.game_objects.game,'Defeated_boss')
        new_game_state.enter_state()

    def give_abillity(self):
        self.game_objects.player.abilities[self.ability] = getattr(sys.modules[__name__], self.ability)

class Reindeer(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/reindeer/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate = states_reindeer.Idle(self)
        self.abillity = 'dash'
        self.health = 210
        self.spirit = 1
        self.attack = Sword
        self.special_attack = Ground_shock

        self.AI_stack = [AI_reindeer.Peace(self)]

    def give_abillity(self):#called when reindeer dies
        self.game_objects.player.states.add('Dash')#append dash abillity to available states

    def take_dmg(self,dmg):
        super().take_dmg(dmg)
        if self.health < 100:
            self.AI_stack[-1].handle_input('stage3')#enter stage 3
        elif self.health < 200:
            self.AI_stack[-1].handle_input('stage2')#enter stage 2

class Idun(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/idun/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 50
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
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 50
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
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 50
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
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 50
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
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.health = 100
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

class Camera_Stop(Staticentity):

    def __init__(self,size,pos,dir):
        #pos = (pos[0],pos[1]-size[1])
        super().__init__(pos,pygame.Surface(size))
        self.hitbox = self.rect.inflate(0,0)
        self.dir = dir

class Spawner(Staticentity):#an entity spawner
    def __init__(self,pos,game_objects,values):
        super().__init__(pos)
        self.image = pygame.image.load("Sprites/invisible.png").convert_alpha()
        self.game_objects=game_objects
        self.entity=values['entity']
        self.number=int(values['number'])
        self.spawn_entities()

    def spawn_entities(self):
        for i in range(0,self.number):
            offset=random.randint(-100, 100)
            pos=[self.rect.x+offset,self.rect.y]
            obj=getattr(sys.modules[__name__], self.entity)(pos,self.game_objects)
            self.game_objects.enemies.add(obj)

class Abilities(pygame.sprite.Sprite):#projectiels
    def __init__(self,entity):
        super().__init__()
        self.entity = entity
        self.state = 'main'
        self.animation = animation.Basic_animation(self)
        self.image = self.sprites[self.state][0]

    def rectangle(self):
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()

    def update(self,pos):
        self.lifetime-=1
        self.update_pos(pos)
        self.animation.update()
        self.destroy()

    def destroy(self):
        if self.lifetime<0:
            self.kill()

    def collision_projectile(self,eprojectile):
        pass

    def update_hitbox(self):#make this a dictionary?
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
            self.dir[0] = 0#no knock back when hit from below or above
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
            self.dir[0] = 0 #no knock back when hit from below or above
        elif self.dir[0] > 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def collision_enemy(self,collision_enemy):
        collision_enemy.take_dmg(self.dmg)
        self.kill()

    def collision_plat(self,platform):
        platform.take_dmg()

    def reset_timer(self):
        if self.state == 'post':
            self.kill()

    def collision_inetractables(self,interactable):
        pass

class Melee(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = entity.dir.copy()
        self.rectangle()

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]
        self.hitbox.center = self.rect.center

    def update(self,pos):
        super().update(pos)
        self.update_hitbox()

    def countered(self):
        self.entity.countered()
        self.kill()

class Heal(Melee):
    def __init__(self,entity):
        super().__init__(entity)

class Explosion(Melee):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/invisible/')

    def __init__(self,entity,dmg):
        super().__init__(entity)
        self.lifetime = 10
        self.dmg = dmg

    def rectangle(self):
        self.rect = pygame.Rect(self.entity.rect.centerx-50,self.entity.rect.centery-50,100,100)
        self.hitbox = self.rect.copy()

    def update_hitbox(self):
        pass

class Shield(Melee):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/invisible/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=0
        self.lifetime=15

    def rectangle(self):
        self.rect = self.entity.hitbox.copy()#pygame.Rect(self.entity.rect[0],self.entity.rect[1],20,40)
        self.hitbox = self.rect.copy()

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
        self.entity.projectiles.add(eprojectile)#add the projectilce to Ailas projectile group
        eprojectile.countered()
        self.kill()

class Thunder_aura(Melee):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/thunder_aura/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime = 1000
        self.dmg = 0
        self.state = 'pre'

    def rectangle(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.entity.rect.center
        self.hitbox = pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)
        self.hitbox.center = self.rect.center

    def update_hitbox(self):
        self.hitbox.inflate_ip(3,3)#the speed should match the animation
        self.hitbox[2]=min(self.hitbox[2],self.rect[2])
        self.hitbox[3]=min(self.hitbox[3],self.rect[3])

    def reset_timer(self):
        if self.state=='pre':
            self.state='main'
        elif self.state=='main':
            pass
        elif self.state=='post':
            self.kill()

class Sword(Melee):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Sword/')

    def __init__(self,entity):
        super().__init__(entity)
        self.init()

    def init(self):
        self.dmg = self.entity.dmg

    def rectangle(self):
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,40,35)
        self.hitbox = self.rect.copy()

    def collision_enemy(self, collision_enemy):
        self.sword_jump()

        if not collision_enemy.invincibile:
            collision_enemy.take_dmg(self.dmg)
            collision_enemy.knock_back(self.dir[0])
            collision_enemy.hurt_particles(dir=self.dir[0])
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
            obj1=particles.General_particle(pos,distance=0,lifetime=10,vel=[7,14],type='spark',dir=angle,scale=0.3)
            self.entity.game_objects.cosmetics.add(obj1)

    def collision_inetractables(self,interactable):#called when projectile hits interactables
        interactable.take_dmg(self)#some will call clash_particles but other will not. So sending self to interactables

class Aila_sword(Sword):
    def __init__(self,entity):
        super().__init__(entity)

    def init(self):
        self.dmg = 10
        self.potrait = Read_files.Sprites().load_all_sprites("Sprites/Enteties/Items/sword")
        self.equip = 'idle'#stone pointer
        self.frame = 0#potrait frame
        self.stones = {'red':Red_infinity_stone(self),'green':Green_infinity_stone(self),'blue':Blue_infinity_stone(self),'orange':Orange_infinity_stone(self)}#,'purple':Red_infinity_stone(self)]
        self.colour = {'idle':[255,255,255,255],'red':[255,64,64,255],'blue':[0,0,205,255],'green':[105,139,105,255],'orange':[255,127,36,255],'purple':[154,50,205,255]}#spark colour

    def potrait_animation(self):#called from inventory
        self.potrait_image = self.potrait[self.equip][self.frame//4].copy()
        self.frame += 1

        if self.frame == len(self.potrait[self.equip])*4:
            self.frame = 0

    def set_stone(self,stone_str):#set from inventory
        if self.equip!='idle':#if not first time
            self.stones[self.equip].detach()

        self.equip = stone_str
        self.stones[stone_str].attach()

    def collision_enemy(self,collision_enemy):
        super().collision_enemy(collision_enemy)
        if self.equip != 'idle':
            self.stones[self.equip].collision()#call collision specific for stone

    def clash_particles(self,pos,number_particles=12):
        angle = random.randint(-180, 180)#the ejection anglex
        for i in range(0,number_particles):
            obj1=particles.General_particle(pos,distance=0,lifetime=10,vel=[7,14],type='spark',dir=angle,scale=0.3,colour=self.colour[self.equip])
            self.entity.game_objects.cosmetics.add(obj1)

class Darksaber(Aila_sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.dmg = 0
        self.lifetime=10#swrod hitbox duration

    def collision_enemy(self,collision_enemy):
        if collision_enemy.spirit>=10:
            collision_enemy.spirit-=10
            spirits=Spiritsorb([collision_enemy.rect.x,collision_enemy.rect.y])
            collision_enemy.game_objects.loot.add(spirits)
        self.kill()

class Projectiles(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir = entity.dir.copy()
        self.rectangle()
        self.velocity = [0,0]

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

    def countered(self):
        self.velocity[0]=-self.velocity[0]
        self.velocity[1]=-self.velocity[1]

class Thunder(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Thunder/')

    def __init__(self,entity,rect):
        super().__init__(entity)
        self.dmg = 10
        self.rect.midbottom = rect.midbottom
        self.lifetime = 1000
        self.velocity = [0,0]
        self.hitbox.center = self.rect.center
        self.state = 'pre'

    def collision_enemy(self,collision_enemy):
        self.dmg=0

    def reset_timer(self):
        if self.state=='pre':
            self.state='main'
        elif self.state=='main':
            self.kill()

class Poisoncloud(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Poisoncloud/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=1
        self.lifetime=400
        self.velocity=[0,0]
        self.update_hitbox()

    def collision_ene(self,collision_ene):
        pass

    def destroy(self):
        if self.lifetime<0:
            self.animation.reset_timer()
            self.state='post'

    def countered(self):
        self.animation.reset_timer()
        self.state='post'

class Poisonblobb(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Poisonblobb/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=10
        self.lifetime=100
        self.velocity=[entity.dir[0]*5,-1]
        self.hitbox=pygame.Rect(self.rect.x,self.rect.y,16,16)
        self.update_hitbox()

    def update(self,scroll):
        self.update_vel()
        super().update(scroll)

    def update_vel(self):
        self.velocity[1]+=0.1#graivity

    def collision_plat(self):
        self.velocity=[0,0]
        if self.state=='main':
            self.animation.reset_timer()
            self.state='post'

class Ground_shock(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/ground_shock/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg = self.entity.dmg
        self.lifetime=100
        self.velocity=[entity.dir[0]*5,0]
        self.rect.bottom = self.entity.rect.bottom
        self.hitbox=pygame.Rect(self.rect.x,self.rect.y,64,32)
        self.update_hitbox()

class Force(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Force/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=30
        self.dmg=0
        self.state='pre'
        self.velocity=[entity.dir[0]*10,0]
        self.update_hitbox()

    def collision_plat(self):
        self.animation.reset_timer()
        self.state='post'
        self.velocity=[0,0]

    def collision_enemy(self,collision_enemy):#if hit something
        self.animation.reset_timer()
        self.state='post'
        self.velocity=[0,0]

        collision_enemy.velocity[0]=self.dir[0]*10#abs(push_strength[0])
        collision_enemy.velocity[1]=-6

class Arrow(Projectiles):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Attack/Arrow/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=100
        self.dmg=10
        self.velocity=[entity.dir[0]*30,0]
        self.update_hitbox()

    def collision_enemy(self,collision_enemy):
        collision_enemy.take_dmg(self.dmg)
        self.velocity=[0,0]
        self.kill()

    def collision_plat(self):
        self.velocity=[0,0]
        self.dmg=0

    def rotate(self):#not in use
        angle=self.dir[0]*max(-self.dir[0]*self.velocity[0]*self.velocity[1],-60)

        self.image=pygame.transform.rotate(self.original_image,angle)#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

class Loot(Dynamicentity):#animated stuff with hitbox
    def __init__(self,pos):
        super().__init__(pos)
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_basic.Idle(self)

    def update(self,scroll):
        super().update(scroll)#update_pos and update_vel
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):
        pass

    def attract(self,pos):#the omamori calls on this in loot group
        pass

class Heart_container(Loot):

    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/heart_container/')

    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects#Soul_essence requries game_objects and it is the same static stamp
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heart container'

    def update_vel(self):
        self.velocity[1]=3

    def player_collision(self):
        self.game_objects.player.max_health += 1
        #a cutscene?
        self.kill()

class Spirit_container(Loot):

    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/spirit_container/')

    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects#Soul_essence requries game_objects and it is the same static stamp
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A spirit container'

    def update_vel(self):
        self.velocity[1]=3

    def player_collision(self):
        self.game_objects.player.max_spirit += 1
        #a cutscene?
        self.kill()

class Soul_essence(Loot):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/soul_essence/')

    def __init__(self,pos,game_objects,ID_key = None):
        super().__init__(pos)
        self.game_objects = game_objects
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'An essence container'#for shops
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world

    def player_collision(self):
        self.game_objects.player.inventory['Soul_essence'] += 1
        self.game_objects.map.state[self.game_objects.map.level_name]['soul_essence'][self.ID_key] = 'gone'#write in the state file that this has been picked up
        #make a cutscene?
        self.kill()

    def update(self,scroll):
        super().update(scroll)
        obj1 = particles.General_particle(self.rect.center,distance=100,lifetime=20,vel=[2,4],type='spark',dir='isotropic')
        self.game_objects.cosmetics.add(obj1)

class Tungsten(Loot):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/tungsten/')

    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects#Soul_essence requries game_objects and it is the same static stamp
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heavy rock'

    def player_collision(self):
        self.game_objects.player.inventory['Tungsten'] += 1
        #a cutscene?
        self.kill()

class Enemy_drop(Loot):
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.velocity = [random.randint(-3, 3),-4]
        self.lifetime = 500

    def update_vel(self):
        self.velocity[1] += 0.5

    def update(self,pos):
        super().update(pos)
        self.lifetime-=1
        self.destory()

    def attract(self,pos):#the omamori calls on this in loot group
        if self.lifetime < 350:
            self.velocity=[0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def player_collision(self):#when the player collides with this object
        obj=(self.__class__.__name__)#get the loot in question
        self.game_objects.player.inventory[obj]+=1
        self.kill()

    #plotfprm collisions
    def down_collision(self,hitbox):
        super().down_collision(hitbox)
        self.velocity[0] = 0.5*self.velocity[0]
        self.velocity[1] = -0.7*self.velocity[1]

    def right_collision(self,hitbox):
        super().right_collision(hitbox)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self,hitbox):
        super().left_collision(hitbox)
        self.velocity[0] = -self.velocity[0]

class Amber_Droplet(Enemy_drop):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/amber_droplet/')

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos[0],pos[1],5,5)#resize the rect
        self.hitbox = self.rect.copy()
        self.description = 'moneyy'

class Bone(Enemy_drop):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/bone/')

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hitbox = self.rect.copy()
        self.description = 'Ribs from my daugther. You can respawn and stuff'

    def use_item(self):
        if self.game_objects.player.inventory['Bone']>0:#if we have bones
            self.game_objects.player.inventory['Bone']-=1
            if len(self.game_objects.player.spawn_point)==2:#if there is already a bone
                self.game_objects.player.spawn_point.pop()
            self.game_objects.player.spawn_point.append({'map':self.game_objects.map.level_name, 'point':self.game_objects.player.abs_dist})
            self.game_objects.player.currentstate = states_player.Plant_bone(self.game_objects.player)

class Spiritsorb(Enemy_drop):#the thing dark saber produces
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/spiritorbs/')

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        rand_pos=[random.randint(-10, 10),random.randint(-10, 10)]
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0]+rand_pos[0],pos[1]+rand_pos[1],5,5)
        self.hitbox=self.rect.copy()

    def update_vel(self):
        self.velocity=[0.1*random.randint(-10, 10),0.1*random.randint(-10, 10)]

    def player_collision(self):
        self.game_objects.player.spirit += 10
        self.kill()

class Animatedentity(Staticentity):#animated stuff, i.e. cosmetics
    def __init__(self,pos):
        super().__init__(pos)
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_basic.Idle(self)

    def update(self,scroll):
        self.update_pos(scroll)
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):#called whe animation finshes
        pass

class Water_running_particles(Animatedentity):#should make for grass, dust, water etc
    sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/running_particles/water/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):#called whe animation finshes
        self.kill()

class Grass_running_particles(Animatedentity):#should make for grass, dust, water etc
    sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/running_particles/grass/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):#called whe animation finshes
        self.kill()

class Dust_running_particles(Animatedentity):#should make for grass, dust, water etc
    sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/running_particles/dust/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):#called whe animation finshes
        self.kill()

class Player_Soul(Animatedentity):#the thing that popps out when player dies
    sprites=Read_files.Sprites().load_all_sprites('Sprites/Enteties/soul/')

    def __init__(self,pos):
        super().__init__(pos)
        self.currentstate = states_basic.Once(self)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.timer=0
        self.velocity=[0,0]

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

    def update(self,scroll):
        super().update(scroll)

        self.timer +=1
        if self.timer>100:#fly to sky
            self.velocity[1]=-20
        elif self.timer>200:
            self.kill()

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0]+self.velocity[0], self.rect.topleft[1] + pos[1]+self.velocity[1]]

class Spawneffect(Animatedentity):#the thing that crets when aila re-spawns
    sprites = Read_files.Sprites().load_all_sprites('Sprites/GFX/respawn/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.finish = False

    def reset_timer(self):
        self.finish = True
        self.kill()

class Slash(Animatedentity):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/GFX/slash/')

    def __init__(self,pos):
        super().__init__(pos)
        self.state = str(random.randint(1, 3))
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.center = pos

    def reset_timer(self):#called whe animation finshes
        self.kill()

class Interactable(Animatedentity):#interactables
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.group = game_objects.interactables
        self.pause_group=game_objects.entity_pause

    def update(self,scroll):
        super().update(scroll)
        self.group_distance()

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.midbottom = self.rect.midbottom

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
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/animations/bridge/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (pos[0],pos[1])#for some reason, the f**ing rect pos is one pixel off. But the platform is at correct pos
        self.hitbox = self.rect.copy()
        platform = Collision_block(pos,(self.image.get_width(),32))
        self.game_objects.platforms.add(platform)

class Path_col(Interactable):

    def __init__(self, pos, game_objects,size, destination, spawn):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.spawn = spawn
        self.image.set_alpha(0)#make them transparent

    def update(self,scroll):
        self.update_pos(scroll)
        self.group_distance()

    def player_collision(self):
        self.game_objects.sound.pause_bg_sound()
        self.game_objects.player.enter_idle()
        self.game_objects.player.reset_movement()
        self.game_objects.load_map(self.destination, self.spawn)

class Path_inter(Interactable):

    def __init__(self, pos, game_objects, size, destination, spawn, image):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.spawn = spawn
        self.image.set_alpha(0)#make them transparent

    def update(self,scroll):
        self.update_pos(scroll)
        self.group_distance()

    def interact(self):
        self.game_objects.sound.pause_bg_sound()
        self.game_objects.player.enter_idle()
        self.game_objects.player.reset_movement()
        self.game_objects.load_map(self.destination, self.spawn)

class Cutscene_trigger(Interactable):
    def __init__(self,pos,game_objects,size,event):
        super().__init__(pos,game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.event = event
        self.image.set_alpha(0)#make them transparent

    def update(self,scroll):
        self.update_pos(scroll)
        self.group_distance()

    def player_collision(self):
        if self.event not in self.game_objects.cutscenes_complete:#if the cutscene has not been shown before. Shold we kill the object instead?
            self.specific()
            new_game_state = states.Cutscenes(self.game_objects.game,self.event)
            new_game_state.enter_state()

    def specific(self):
        if self.event == 'Cultist_encounter':
            new_game_state = states.Cultist_encounter_gameplay(self.game_objects.game)
            new_game_state.enter_state()

class Interactable_bushes(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.interacted = False

    def player_collision(self):#player collision
        if not self.interacted:
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
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/cave_grass/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)

class Chest(Interactable):
    def __init__(self,pos,game_objects,state,ID_key):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/animations/Chest/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health=3
        self.inventory = {'Amber_Droplet':3}
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting with in the world
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}
        self.invincibile = False

        if state != "closed":
            self.currentstate = states_basic.Open(self)

    def update(self,scroll):
        super().update(scroll)
        self.update_timers()#invincibililty

    def loots(self):#this is called when the opening animation is finished
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)([self.hitbox.x,self.hitbox.y],self.game_objects)#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def reset_timer(self):#when animation is finished
        self.currentstate.handle_input('Idle')

    def take_dmg(self,projectile):
        if self.invincibile:
            return
        projectile.clash_particles(self.hitbox.center)
        self.health-=1
        self.timer_jobs['invincibility'].activate()

        if self.health > 0:
            self.currentstate.handle_input('Hurt')
        else:
            self.currentstate.handle_input('Opening')
            self.game_objects.map.state[self.game_objects.map.level_name]['chest'][self.ID_key] = 'open'#write in the state file that this has been picked up

    def update_timers(self):
        for timer in self.timers:
            timer.update()

class Door(Interactable):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/Door/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

class Spawnpoint(Interactable):#save point
    def __init__(self,pos,game_objects,map):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/Spawnpoint/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox=self.rect.copy()
        self.init_cor = pos
        self.map = map

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        if type(self.currentstate).__name__ == 'Outline':#single click
            self.game_objects.player.spawn_point[0]['map']=self.map
            self.game_objects.player.spawn_point[0]['point']=self.init_cor
            self.currentstate.handle_input('Once')
        else:#odoulbe click
            new_state = states.Soul_essence(self.game_objects.game)
            new_state.enter_state()

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Rhoutta_altar(Interactable):#altar to trigger the cutscane at the beginning
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/animations/rhoutta_altar/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox=self.rect.copy()

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        self.currentstate.handle_input('Once')
        new_game_state = states.Cutscenes(self.game_objects.game,'Rhoutta_encounter')
        new_game_state.enter_state()

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Sign(Interactable):#save point
    def __init__(self,pos,game_objects,directions):
        super().__init__(pos,game_objects)
        self.directions = directions
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/animations/sign/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox=self.rect.copy()

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def player_noncollision(self):#when player doesn't collide
        self.currentstate.handle_input('Idle')

    def interact(self):#when player press t/y
        new_state = states.Signpost(self.game_objects.game,self)
        new_state.enter_state()

class Menu_Arrow():

    def __init__(self):
        self.img = pygame.image.load("Sprites/utils/arrow.png").convert_alpha()
        self.rect = self.img.get_rect()

    #note: sets pos to input, doesn't update with an increment of pos like other entities
    def update(self,pos):
        self.rect.topleft = pos

    def draw(self,screen):
        screen.blit(self.img, self.rect.topleft)

class Menu_Box():
    def __init__(self):
        self.img = pygame.image.load("Sprites/utils/box.png").convert_alpha()#select box
        self.rect = self.img.get_rect()

    def update(self,pos):
        pass

    def draw(self,screen):
        pass
        #screen.blit(self.img, self.rect.topleft)

class Infinity_stones():

    def __init__(self,sword):
        self.sword = sword
        self.state = 'idle'
        self.animation = animation.Basic_animation(self)#it is called from inventory

    def reset_timer(self):
        pass

    def attach(self):
        pass

    def detach(self):
        pass

    def collision(self):
        pass

class Red_infinity_stone(Infinity_stones):#more dmg

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/infinity_stones/red/')#for inventory
        self.colour = 'red'

    def attach(self):
        self.sword.dmg*=1.1

    def detach(self):
        self.sword.dmg*=(1/1.1)

class Green_infinity_stone(Infinity_stones):#faster slash (changing framerate)

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/infinity_stones/green/')#for inventory
        self.colour = 'green'

class Blue_infinity_stone(Infinity_stones):#get spirit at collision

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/infinity_stones/blue/')#for inventory
        self.colour = 'blue'

    def collision(self):
        self.sword.entity.spirit += 5

class Orange_infinity_stone(Infinity_stones):#bigger hitbox

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/infinity_stones/orange/')#for inventory
        self.colour = 'orange'

    def detach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y,40,40)
        self.sword.hitbox = self.sword.rect.copy()

    def attach(self):
        self.sword.rect = pygame.Rect(self.sword.entity.rect.x,self.sword.entity.rect.y,80,40)
        self.sword.hitbox = self.sword.rect.copy()

class Purple_infinity_stone(Infinity_stones):#donno

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/infinity_stones/purple/')#for inventory
        self.colour = 'purple'

    def attach(self):
        pass

    def detach(self):
        pass

class Omamoris():
    def __init__(self,entity):
        self.equipped_omamoris=[]#equiped omamoris
        self.omamori_list=[Double_jump(entity),Loot_magnet(entity),More_spirit(entity)]#omamoris in inventory.
        self.level = 0

    def update(self):
        for omamori in self.equipped_omamoris:
            omamori.update()

    def handle_input(self,input):
        for omamori in self.equipped_omamoris:
            omamori.handle_input(input)

    def equip_omamori(self,omamori_index):
        new_omamori=self.omamori_list[omamori_index]
        if new_omamori not in self.equipped_omamoris:#add the omamori
            if len(self.equipped_omamoris)<3:#maximum number of omamoris to equip
                self.equipped_omamoris.append(new_omamori)
                new_omamori.attach()
        else:#remove the omamori
            old_omamori=self.omamori_list[omamori_index]
            self.equipped_omamoris.remove(old_omamori)
            old_omamori.detach()#call the detach function of omamori

    def level_up(self):
        self.level += 1

class Omamori():
    def __init__(self,entity):
        self.entity = entity
        self.state = 'idle'
        self.animation = animation.Basic_animation(self)#it is called from inventory

    def update(self):
        pass

    def handle_input(self,input):
        pass

    def detach(self):
        self.state='idle'
        self.animation.reset_timer()

    def attach(self):
        self.state='equip'
        self.animation.reset_timer()

    def reset_timer(self):
        pass

class Double_jump(Omamori):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/omamori/double_jump/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)
        self.counter=0

    def update(self):
        if self.entity.collision_types['bottom'] or self.entity.collision_types['right'] or self.entity.collision_types['left']:
            self.reset_counter()

    def handle_input(self,input):
        if input[-1]=='a' and self.counter<1:
            self.entity.currentstate.handle_press_input('double_jump')
            if type(self.entity.currentstate).__name__=='Double_jump':
                self.counter+=1

    def reset_counter(self):
        self.counter=0

class Loot_magnet(Omamori):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/omamori/loot_magnet/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

class More_spirit(Omamori):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/omamori/more_spirit/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)

    def update(self):
        self.entity.spirit += 0.5

#timer toools: activate with the attrubute activate, which will run until the specified duration is run out
class Timer():
    def __init__(self,entity,duration):
        self.entity = entity
        self.duration = duration

    def activate(self):#add timer to the entity timer list
        self.lifetime = self.duration
        self.entity.timers.append(self)

    def deactivate(self):
        if self in self.entity.timers:
            self.entity.timers.remove(self)

    def update(self):
        self.lifetime -= 1
        if self.lifetime < 0:
            self.deactivate()

class Invincibility_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def activate(self):
        super().activate()
        self.entity.invincibile = True

    def deactivate(self):
        super().deactivate()
        self.entity.invincibile = False

class Sword_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def activate(self):
        super().activate()
        self.entity.sword_swinging = True

    def deactivate(self):
        super().deactivate()
        self.entity.sword_swinging = False

class Jump_timer(Timer):
    def __init__(self,entity,duration):
        super().__init__(entity,duration)

    def update(self):
        super().update()
        self.entity.velocity[1] -= 0.4*(C.max_vel[1]+self.entity.velocity[1])

    def activate(self):
        super().activate()
        self.entity.velocity[1] = 0
        self.entity.jumping = True

    def deactivate(self):
        super().deactivate()
        #self.entity.velocity[1] = 0.7*self.entity.velocity[1]
