import pygame, random, sys, Read_files, states, particles, animation, states_health, states_basic, states_player, states_NPC, states_enemy, states_vatt, states_mygga, states_reindeer, states_bluebird, states_kusa, states_rogue_cultist, AI_wall_slime, AI_vatt, AI_kusa, AI_bluebird, AI_enemy, AI_reindeer, math, sound
import constants as C

pygame.mixer.init()

class RefelctionGroup(pygame.sprite.Group):#a group for the reflection object which need a special draw method
    def __init__(self):
        super().__init__()

    def draw(self):
        for s in self.sprites():
            s.draw()

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
        else:#going to the leftx
            entity.left_collision(self.hitbox.right)
        entity.update_rect()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
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
        if entity.velocity[1] > 0:#going down
            if entity.hitbox.bottom <= self.hitbox.top+offset:
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
            entity.velocity[1] = 2 #need to have a value to avoid "dragin in air" while running
            entity.velocity[0] = 0 #need to have a value to avoid "dragin in air" while running
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

class Collision_dmg(Platform):#should be an interactable
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
        entity.update_rect()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.down_collision(self.hitbox.top)
            entity.velocity[1] = -10#knock back
        else:#going up
            entity.top_collision(self.hitbox.bottom)
            entity.velocity[1] = 10#knock back
        entity.take_dmg(self.dmg)
        entity.update_rect()

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
        #self.rect.topleft = [self.rect.topleft[0] + self.parallax[0]*pos[0], self.rect.topleft[1] + self.parallax[1]*pos[1]]#do you need this?
        self.true_pos = [self.true_pos[0] + self.parallax[0]*pos[0], self.true_pos[1] + self.parallax[1]*pos[1]]
        self.rect.topleft = self.true_pos.copy()

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

class Reflection(Staticentity):
    def __init__(self,pos,size,dir,game_objects, offset = 12):
        super().__init__(pos,pygame.Surface(size, pygame.SRCALPHA, 32))
        self.pos = list(pos)
        self.size = size
        self.dir = dir
        self.game_objects = game_objects
        self.offset = offset
        self.squeeze = 0.75

    def draw(self):
        squeeze = self.squeeze
        reflect_rect = pygame.Rect(self.rect.left, self.rect.top - self.size[1]*squeeze - self.offset, self.size[0], self.size[1])
        reflect_rect.center = [reflect_rect.center[0],self.game_objects.game.screen.get_height() - reflect_rect.center[1]]
        reflect_surface = self.game_objects.game.screen.copy()
        reflect_surface.convert_alpha()#do we need this?
        reflect_surface = pygame.transform.scale(reflect_surface, (reflect_surface.get_width(), reflect_surface.get_height()*squeeze))
        #reflect_surface.set_alpha(100)
        self.game_objects.game.screen.blit(pygame.transform.flip(reflect_surface, False, True), (self.rect.topleft[0],self.rect.topleft[1]), reflect_rect, special_flags = pygame.BLEND_RGBA_MULT)#BLEND_RGBA_MIN

class Animatedentity(Staticentity):#animated stuff, i.e. cosmetics
    def __init__(self,pos):
        super().__init__(pos)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

    def update(self,scroll):
        super().update(scroll)#update_pos
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):#states_basic needs this
        pass

class Platform_entity(Animatedentity):#Things to collide with platforms
    def __init__(self,pos):
        super().__init__(pos)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = False#a flag for entities to go through ramps from side or top
        self.velocity = [0,0]

    def take_dmg(self,dmg):#projectile collision dmg will call this
        pass

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.bottom = self.rect.bottom

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    def update_rect(self):
        self.rect.midbottom = self.hitbox.midbottom

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.midbottom = self.rect.midbottom

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

class Character(Platform_entity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.acceleration = [0,C.acceleration[1]]
        self.friction = C.friction.copy()
        self.max_vel = C.max_vel.copy()

        self.timers = []#a list where timers are append whe applicable, e.g. jump, invincibility etc.
        self.running_particles = Dust_running_particles
        self.true_pos = self.rect.center

    def update_pos(self,pos):#scrollen
        #self.true_pos = [self.true_pos[0] + pos[0], self.true_pos[1] + pos[1]]
        #self.rect.center = self.true_pos.copy()
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.true_pos = self.rect.center
        self.hitbox.bottom = self.rect.bottom

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom

    def update_rect(self):
        self.rect.midbottom = self.hitbox.midbottom
        self.true_pos = [self.true_pos[0],self.rect.centery]

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.true_pos = self.rect.center
        self.hitbox.midbottom = self.rect.midbottom

    def update(self,pos):
        self.update_pos(pos)
        self.update_timers()
        self.update_vel()#need to be after update_timers since jump will add velocity in update_timers
        self.currentstate.update()#need to be aftre update_vel since some state transitions look at velocity
        self.animation.update()#need to be after currentstate since animation will animate the current state

    def update_vel(self):
        self.velocity[1] += self.acceleration[1]-self.velocity[1]*self.friction[1]#gravity
        self.velocity[1] = min(self.velocity[1],self.max_vel[1])#set a y max speed#

        self.velocity[0] += self.dir[0]*self.acceleration[0]-self.friction[0]*self.velocity[0]#self.game_objects.game.dt*

        self.true_pos = [self.true_pos[0] + self.velocity[0],self.true_pos[1] + self.velocity[1]]

    def take_dmg(self,dmg):
        if self.invincibile: return
        self.health -= dmg
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period

        if self.health > 0:#check if dead¨
            self.animation.handle_input('Hurt')#turn white
            #self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            self.game_objects.camera.camera_shake(3,10)
        else:#if dead
            if self.currentstate.state_name != 'death':#if not already dead
                self.aggro = False
                self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
                self.currentstate.enter_state('Death')#overrite any state and go to deat

    def knock_back(self,dir):
        self.velocity[0] = dir[0]*30
        self.velocity[1] = -dir[1]*30

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
        self.image = self.sprites.sprite_dict['idle_main'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,35)
        self.rect.midbottom = self.hitbox.midbottom#match the positions of hitboxes

        self.max_health = 10
        self.max_spirit = 5
        self.health = 2
        self.spirit = 2

        self.projectiles = game_objects.fprojectiles

        self.abilities = {'Thunder':Thunder,'Force':Force,'Arrow':Arrow,'Heal':Heal,'Darksaber':Darksaber}#the objects are referensed but created in states
        self.equip = 'Thunder'#ability pointer
        self.sword = Aila_sword(self)

        self.states = set(['Wall','Dash_attack','Dash','Idle','Walk','Jump_run','Jump_stand','Fall_run','Fall_stand','Death','Invisible','Hurt','Spawn','Sword_run1','Sword_run2','Sword_stand1','Sword_stand2','Air_sword2','Air_sword1','Sword_up','Sword_down','Plant_bone','Thunder','Force','Heal','Darksaber','Arrow','Counter'])#all states that are available to Aila, convert to set to make lookup faster
        self.currentstate=states_player.Idle_main(self)

        self.spawn_point = [{'map':'light_forest_3', 'point':'1'}]#a list of max len 2. First elemnt is updated by sejt interaction. Can append positino for bone, which will pop after use
        self.inventory = {'Amber_Droplet':403,'Bone':2,'Soul_essence':10,'Tungsten':10}#the keys need to have the same name as their respective classes
        self.omamoris = Omamoris(self)#

        self.set_abs_dist()

        self.sword_swing = 0#a flag to check which swing we are at (0 or 1)
        self.dash_cost = 1#cost of spirit to perform dash
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_player),'jump':Jump_timer(self,C.jump_time_player),'sword':Sword_timer(self,C.sword_time_player),'shroomjump':Shroomjump_timer(self,C.shroomjump_timer_player),'ground':Ground_timer(self,C.ground_timer_player)}#these timers are activated when promt and a job is appeneded to self.timer.

    def down_collision(self,hitbox):#when colliding with platform beneth
        super().down_collision(hitbox)
        self.ground = True#used for jumping

    def take_dmg(self,dmg = 1):
        if self.invincibile: return
        self.timer_jobs['invincibility'].activate()#adds a timer to self.timers and sets self.invincible to true for the given period
        self.health -= dmg
        self.game_objects.UI.remove_hearts(dmg)#update UI
        if self.health > 0:#check if dead¨
            self.animation.handle_input('Hurt')#turn white
            self.animation.handle_input('Invincibile')#blink a bit. need to be after hurt
            self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            self.hurt_particles(lifetime=40,vel=[3,8],colour=[0,0,0,255],scale=3,number_particles=60)
            self.game_objects.cosmetics.add(Slash(self.hitbox.center))#make a slash animation
            self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
        else:#if health < 0
            self.game_objects.game.state_stack[-1].handle_input('death')#depending on gameplay state, different death stuff should happen

    def heal(self, health = 1):
        self.health += health
        self.game_objects.UI.update_hearts()#update UI

    def consume_spirit(self, spirit = 1):
        self.spirit -= spirit
        self.game_objects.UI.remove_spirits(spirit)#update UI

    def add_spirit(self, spirit = 1):
        self.spirit += spirit
        self.game_objects.UI.update_spirits()#update UI

    def death(self):#"normal" gameplay states calls this
        self.game_objects.game.state_stack[-1].handle_input('dmg')#makes the game freez for few frames
        self.currentstate.enter_state('Death_pre')#overrite any state and go to deat

    def dead(self):#called when death animation is finished
        new_game_state = states.Cutscenes(self.game_objects.game,'Death')
        new_game_state.enter_state()
        self.set_abs_dist()

    def set_abs_dist(self):#the absolute distance, i.e. the total scroll
        self.abs_dist = C.player_center.copy()#the coordinate for buring the bone

    def enter_idle(self):
        self.currentstate = states_player.Idle_main(self)

    def reset_movement(self):#called when loading new map or entering conversations
        self.velocity = [0,0]
        self.acceleration =  [0,C.acceleration[1]]
        self.friction = C.friction_player.copy()

    def update(self,pos):
        super().update(pos)
        self.abs_dist = [self.abs_dist[0] - pos[0], self.abs_dist[1] - pos[1]]
        self.omamoris.update()

class Enemy(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause
        self.description = 'enemy'##used in journal

        self.currentstate = states_enemy.Idle(self)
        self.AI = AI_enemy.Peace(self)

        self.inventory = {'Amber_Droplet':random.randint(0, 10),'Bone':2}
        self.spirit = 10
        self.health = 3

        self.aggro = True#colliding with player
        self.dmg = 1#projectile damage

        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

        #move these to AI classes?
        self.attack_distance = 0#when try to hit
        self.aggro_distance = 300#when ot become aggro

    def update(self,pos):
        super().update(pos)
        self.AI.update()#tell what the entity should do
        self.group_distance()

    def player_collision(self):#when player collides with enemy
        if not self.aggro: return
        if not self.game_objects.player.invincibile and not self.game_objects.player.currentstate.state_name == 'death':
            self.game_objects.player.take_dmg(1)
            sign=(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
            if sign>0:
                self.game_objects.player.knock_back([1,0])
            else:
                self.game_objects.player.knock_back([-1,0])

    def dead(self):#called when death animation is finished
        self.loots()
        self.game_objects.world_state.update_kill_statistics(type(self).__name__.lower())
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

class Mygga(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/mygga/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)
        self.currentstate = states_mygga.Idle(self)
        self.health = 2
        self.acceleration = [0,0]
        self.friction = [C.friction[0]*0.8,C.friction[0]*0.8]
        self.max_vel = [C.max_vel[0],C.max_vel[0]]

class Slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],16,16)

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
        self.velocity[1]=self.acceleration[1]-self.dir[1]
        self.velocity[0]=self.acceleration[0]+self.dir[0]

class Woopie(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.health = 1
        self.spirit=100
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')

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
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)

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
        self.AI = AI_bluebird.Peace(self)

    def knock_back(self,dir):
        pass

class Shroompoline(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/shroompolin/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box=pygame.Rect(pos[0],pos[1],32,10)
        self.AI = AI_enemy.Nothing(self)
        self.aggro = False#player collision
        self.invincibile = True#taking dmg

    def player_collision(self):
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
        self.AI_stack = [AI_kusa.Peace(self)]
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
        for i in range(0,self.number):
            pos=[self.hitbox.centerx,self.hitbox.centery-10]
            obj=Slime(pos,self.game_objects)
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
        self.attack_distance = 80
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
        self.attack_distance = 80
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
        self.conv_index = 0
        self.currentstate = states_NPC.Idle(self)

        self.sprites = Read_files.Sprites_Player("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.image = self.sprites.get_image('idle', 0, self.dir)
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
            state = 'state_' + str(self.game_objects.world_state.progress)
            conv = self.conversation[state][str(self.conv_index)]
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
        if self.game_objects.world_state.progress == 2:#if player has deafated the reindeer
            if 'Wall' not in self.game_objects.player.states:#if player doesn't have wall yet
                new_game_state = states.New_ability(self.game_objects.game,'wall')
                new_game_state.enter_state()
                self.game_objects.player.states.add('Wall')#append wall abillity to available states

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

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.health = 30

    def dead(self):
        self.aggro = False
        self.AI_stack[-1].set_AI('Nothing')
        self.loots()
        self.give_abillity()
        self.game_objects.world_state.increase_progress()
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
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate = states_reindeer.Idle(self)
        self.abillity = 'dash'
        self.spirit = 1
        self.attack = Sword
        self.special_attack = Ground_shock
        self.attack_distance = 300

        self.AI = AI_reindeer.Peace(self)

    def give_abillity(self):#called when reindeer dies
        self.game_objects.player.states.add('Dash')#append dash abillity to available states

    def take_dmg(self,dmg):
        super().take_dmg(dmg)
        #self.AI_stack[-1].handle_input('jumping')#enter stage 3
        #if self.health < 100:
    #        self.AI_stack[-1].handle_input('stage3')#enter stage 3
    #    elif self.health < 200:
    #        self.AI_stack[-1].handle_input('stage2')#enter stage 2

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

class Camera_Stop(Staticentity):

    def __init__(self,game_objects, size,pos,dir):
        super().__init__(pos,pygame.Surface(size))
        self.game_objects = game_objects
        self.flag = False#a flag such that the recentering only occures once
        self.hitbox = self.rect.inflate(0,0)
        #self.dir = dir
        self.stops = {'right':self.right,'left':self.left,'bottom':self.bottom,'top':self.top,'center':self.center}[dir]

    #def update(self,scroll):
#        super().update(scroll)
#        self.methods()#this needs to be called before camera calculates the scroll.

    def right(self):
        if (self.rect.bottom > 0) and (self.rect.top < self.game_objects.game.WINDOW_SIZE[1]):#just enters the screen vertically (the top and bottom)
            if -self.game_objects.game.WINDOW_SIZE[0] < (self.rect.left - self.game_objects.player.hitbox.centerx) < self.game_objects.game.WINDOW_SIZE[0]*0.5:
                self.game_objects.camera.center[0] = self.game_objects.game.WINDOW_SIZE[0] - (self.rect.left - self.game_objects.player.hitbox.centerx)
                self.flag = True
        else:
            if self.flag:
                self.game_objects.camera.center[0] = list(self.game_objects.map.PLAYER_CENTER)[0]
                self.flag = False

    def left(self):
        if (self.rect.bottom > 0) and (self.rect.top < self.game_objects.game.WINDOW_SIZE[1]):#just enters the screen vertically (the top and bottom)
            if -self.game_objects.game.WINDOW_SIZE[0] < (self.game_objects.player.hitbox.centerx - self.rect.right) < self.game_objects.game.WINDOW_SIZE[0]*0.5:
                self.game_objects.camera.center[0] =  self.game_objects.player.hitbox.centerx - self.rect.right
                self.flag = True
        else:
            if self.flag:
                self.game_objects.camera.center[0] = list(self.game_objects.map.PLAYER_CENTER)[0]
                self.flag = False

    def bottom(self):
        if (self.rect.left <= self.game_objects.game.WINDOW_SIZE[0]) and (self.rect.right > 0):
            if -self.game_objects.game.WINDOW_SIZE[1] < (self.rect.top - self.game_objects.player.hitbox.centery) < self.game_objects.game.WINDOW_SIZE[1]*0.5:
                self.game_objects.camera.center[1] = self.game_objects.game.WINDOW_SIZE[1] - (self.rect.top - self.game_objects.player.hitbox.centery)
                self.flag = True
        else:
            if self.flag:
                self.game_objects.camera.center[1] = list(self.game_objects.map.PLAYER_CENTER)[1]
                self.flag = False

    def top(self):
        if (self.rect.left <= self.game_objects.game.WINDOW_SIZE[0]) and (self.rect.right > 0):
            if -self.game_objects.game.WINDOW_SIZE[1] < (self.game_objects.player.hitbox.centery - self.rect.bottom) < self.game_objects.game.WINDOW_SIZE[1]*0.5:
                self.game_objects.camera.center[1] = self.game_objects.player.hitbox.centery - self.rect.bottom
                self.flag = True
        else:
            if self.flag:
                self.game_objects.camera.center[1] = list(self.game_objects.map.PLAYER_CENTER)[1]
                self.flag=False

    def center(self):
        self.game_objects.camera.center[0] = self.game_objects.player.hitbox.centerx - (self.rect.centerx - self.game_objects.game.WINDOW_SIZE[0]*0.5)
        self.game_objects.camera.center[1] = self.game_objects.player.hitbox.centery - (self.rect.centery - self.game_objects.game.WINDOW_SIZE[1]*0.5)

class Spawner(Staticentity):#an entity spawner
    def __init__(self,pos,game_objects,values):
        super().__init__(pos)
        self.game_objects=game_objects
        self.image = pygame.image.load("Sprites/invisible.png").convert_alpha()
        self.entity=values['entity']
        self.number=int(values['number'])
        self.spawn_entities()

    def spawn_entities(self):
        for i in range(0,self.number):
            offset=random.randint(-100, 100)
            pos=[self.rect.x+offset,self.rect.y]
            obj=getattr(sys.modules[__name__], self.entity)(pos,self.game_objects)
            self.game_objects.enemies.add(obj)

class Abilities(Animatedentity):#projectiels
    def __init__(self,entity):
        super().__init__(pos = [0,0])
        self.entity = entity
        self.dir = entity.dir.copy()

    def update(self,pos):
        super().update(pos)
        self.lifetime -= 1
        self.destroy()

    def destroy(self):
        if self.lifetime<0:
            self.kill()

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

    def collision_projectile(self,eprojectile):#projecticle proectile collision
        pass

    def collision_enemy(self,collision_enemy):
        if not collision_enemy.invincibile:
            collision_enemy.take_dmg(self.dmg)
            #self.kill()

    def collision_plat(self,platform):#collision platform
        platform.take_dmg()

    def collision_inetractables(self,interactable):#collusion interactables
        pass

class Melee(Abilities):
    def __init__(self,entity):
        super().__init__(entity)

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]
        self.hitbox.center = self.rect.center

    def update(self,pos):
        super().update(pos)
        self.update_hitbox()

    def countered(self):#shielded
        self.entity.countered()
        self.kill()

class Heal(Melee):
    def __init__(self,entity):
        super().__init__(entity)

class Explosion(Melee):
    sprites = Read_files.Sprites_Player('Sprites/Attack/explosion/')

    def __init__(self,entity):
        super().__init__(entity)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.x = entity.rect.x
        self.rect.bottom = entity.rect.bottom
        self.hitbox = self.rect.copy()
        self.aggro = False #to not take collision dmg
        self.lifetime = 100
        self.dmg = entity.dmg

    def update_hitbox(self):
        pass

    def reset_timer(self):
        self.kill()

class Shield(Melee):
    sprites = Read_files.Sprites_Player('Sprites/Attack/invisible/')

    def __init__(self,entity):
        super().__init__(entity)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.entity.hitbox.copy()#pygame.Rect(self.entity.rect[0],self.entity.rect[1],20,40)
        self.hitbox = self.rect.copy()
        self.dmg=0
        self.lifetime=15

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
    sprites = Read_files.Sprites_Player('Sprites/Attack/thunder_aura/')

    def __init__(self,entity):
        super().__init__(entity)
        self.currentstate = states_basic.Once(self)#
        self.image = self.sprites.sprite_dict['once'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = self.entity.rect.center
        self.hitbox = self.rect.copy()#pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)
        self.lifetime = 1000

    def update_hitbox(self):
        self.hitbox.inflate_ip(3,3)#the speed should match the animation
        self.hitbox[2]=min(self.hitbox[2],self.rect[2])
        self.hitbox[3]=min(self.hitbox[3],self.rect[3])

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Sword(Melee):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Sword/')

    def __init__(self,entity):
        super().__init__(entity)
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
        self.dmg = 1
        self.tungsten_cost = 1#the cost to level up to next level
        self.level = 0#determines how many stone one can attach
        self.potrait = Sword_potrait()
        self.equip = []#stone pointer
        self.stones = {'red':Red_infinity_stone(self),'green':Green_infinity_stone(self),'blue':Blue_infinity_stone(self),'orange':Orange_infinity_stone(self)}#,'purple':Red_infinity_stone(self)]#the ones aila has picked up
        self.colour = {'red':[255,64,64,255],'blue':[0,0,205,255],'green':[105,139,105,255],'orange':[255,127,36,255],'purple':[154,50,205,255]}#spark colour

    def set_stone(self,stone_str):#called from smith
        if len(self.equip) < self.level:
            self.equip.append(stone_str)
            self.stones[stone_str].attach()

    def remove_stone(self):#not imple,ented
        pass
        #if self.equip != 'idle':#if not first time
        #    self.stones[self.equip].detach()

    def collision_enemy(self,collision_enemy):
        super().collision_enemy(collision_enemy)
        for stone in self.equip:
            self.stones[stone].collision()#call collision specific for stone

    def clash_particles(self,pos,number_particles=12):
        angle = random.randint(-180, 180)#the ejection anglex
        color = [255,255,255,255]
        for i in range(0,number_particles):
            obj1=particles.General_particle(pos,distance=0,lifetime=10,vel=[7,14],type='spark',dir=angle,scale=0.3,colour=color)
            self.entity.game_objects.cosmetics.add(obj1)

    def level_up(self):#called when the smith imporoves the sword
        if self.level >=3: return
        self.entity.inventory['Tungsten'] -= self.tungsten_cost
        self.dmg *= 1.2
        self.level += 1
        self.potrait.currentstate.enter_state('Level_'+str(self.level))
        self.tungsten_cost += 2#1, 3, 5 tungstes to level upp 1, 2, 3

class Darksaber(Aila_sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.dmg = 0
        self.lifetime=10#swrod hitbox duration

    def collision_enemy(self,collision_enemy):
        if collision_enemy.spirit>=10:
            collision_enemy.spirit-=10
            #spirits=Spiritorb([collision_enemy.rect.x,collision_enemy.rect.y])
            #collision_enemy.game_objects.loot.add(spirits)
        self.kill()

class Projectiles(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.velocity = [0,0]

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

    def countered(self):
        self.velocity[0]=-self.velocity[0]
        self.velocity[1]=-self.velocity[1]

class Thunder(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Thunder/')

    def __init__(self,entity,enemy_rect):
        super().__init__(entity)
        self.currentstate = states_basic.Once(self)#
        self.image = self.sprites.sprite_dict['once'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midbottom = enemy_rect.midbottom
        self.hitbox = self.rect.copy()
        self.lifetime = 1000
        self.dmg = 2

    def collision_enemy(self,collision_enemy):
        self.dmg = 0
        collision_enemy.velocity = [0,0]#slow him down

    def reset_timer(self):
        self.kill()

class Poisoncloud(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Poisoncloud/')

    def __init__(self,entity):
        super().__init__(entity)
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

    def countered(self):#shielded
        self.currentstate.handle_input('Death')

class Poisonblobb(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Poisonblobb/')

    def __init__(self,entity):
        super().__init__(entity)
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = pygame.Rect(self.rect.x,self.rect.y,16,16)
        self.update_hitbox()

        self.dmg = entity.dmg
        self.lifetime = 100
        self.velocity=[entity.dir[0]*5,-1]

    def update(self,scroll):
        super().update(scroll)
        self.update_vel()

    def update_vel(self):
        self.velocity[1]+=0.1#graivity

    def collision_plat(self,platform):
        self.velocity = [0,0]
        self.currentstate.handle_input('Death')

class Ground_shock(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/ground_shock/')

    def __init__(self,entity):
        super().__init__(entity)
        self.image = self.sprites.sprite_dict['once'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.bottom = self.entity.rect.bottom
        self.hitbox=pygame.Rect(self.rect.x,self.rect.y,64,32)
        self.update_hitbox()

        self.dmg = entity.dmg
        self.lifetime = 100
        self.velocity=[entity.dir[0]*5,0]

class Force(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Force/')

    def __init__(self,entity):
        super().__init__(entity)
        self.image = self.sprites.sprite_dict['once'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()
        if entity.dir[1] == 0:
            self.dir = entity.dir.copy()
        else:
            self.dir = [0,entity.dir[1]]
        self.velocity=[self.dir[0]*10,-self.dir[1]*10]
        self.update_hitbox()

        self.lifetime = 30
        self.dmg = 0

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

class Arrow(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Arrow/')

    def __init__(self,entity):
        super().__init__(entity)
        self.image = self.sprites.sprite_dict['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy()

        self.lifetime = 100
        self.dmg = 1
        if entity.dir[1] == 0:
            self.dir = entity.dir.copy()
        else:
            self.dir = [0,-entity.dir[1]]
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

class Loot(Platform_entity):#
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.description = ''

    def update(self,scroll):
        super().update(scroll)
        self.update_vel()

    def update_vel(self):
        pass

    def attract(self,pos):#the omamori calls on this in loot group
        pass

class Empty_item(Loot):
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/heart_container/')

    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)

class Heart_container(Loot):

    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/heart_container/')

    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
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

    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/spirit_container/')

    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
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
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/soul_essence/')

    def __init__(self,pos,game_objects,ID_key = None):
        super().__init__(pos, game_objects)
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

    def update(self,scroll):
        super().update(scroll)
        obj1 = particles.General_particle(self.rect.center,distance=100,lifetime=20,vel=[2,4],type='spark',dir='isotropic')
        self.game_objects.cosmetics.add(obj1)

class Tungsten(Loot):
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/tungsten/')

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heavy rock'

    def player_collision(self):
        self.game_objects.player.inventory['Tungsten'] += 1
        #a cutscene?
        self.kill()

class Spiritorb(Loot):#the thing dark saber produces
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/spiritorbs/')

    def __init__(self,pos,game_objects):
        super().__init__(pos, game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()

    def player_collision(self):
        self.game_objects.player.add_spirit(1)
        self.kill()

class Enemy_drop(Loot):#add gravity
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
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
            self.velocity = [0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def player_collision(self):#when the player collides with this object
        obj=(self.__class__.__name__)#get the string in question
        try:
            self.game_objects.player.inventory[obj] += 1
        except:
            self.game_objects.player.inventory[obj] = 1
        self.kill()

    #plotfprm collisions
    def down_collision(self,hitbox):
        super().down_collision(hitbox)
        self.velocity[0] = 0.5*self.velocity[0]
        self.velocity[1] = -0.6*self.velocity[1]

    def right_collision(self,hitbox):
        super().right_collision(hitbox)
        self.velocity[0] = -self.velocity[0]

    def left_collision(self,hitbox):
        super().left_collision(hitbox)
        self.velocity[0] = -self.velocity[0]

class Amber_Droplet(Enemy_drop):
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/amber_droplet/')

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect = pygame.Rect(pos[0],pos[1],5,5)#resize the rect
        self.hitbox = self.rect.copy()
        self.description = 'moneyy'

    def player_collision(self):#when the player collides with this object
        super().player_collision()
        self.game_objects.world_state.update_money_statistcis()

class Bone(Enemy_drop):
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/bone/')

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = self.sprites.sprite_dict['idle'][0]
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
            self.game_objects.player.currentstate.enter_state('Plant_bone_main')

class Water_running_particles(Animatedentity):#should make for grass, dust, water etc
    sprites=Read_files.Sprites_Player('Sprites/animations/running_particles/water/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

class Grass_running_particles(Animatedentity):#should make for grass, dust, water etc
    sprites=Read_files.Sprites_Player('Sprites/animations/running_particles/grass/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

class Dust_running_particles(Animatedentity):#should make for grass, dust, water etc
    sprites=Read_files.Sprites_Player('Sprites/animations/running_particles/dust/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def reset_timer(self):
        self.kill()

class Player_Soul(Animatedentity):#the thing that popps out when player dies
    sprites=Read_files.Sprites_Player('Sprites/Enteties/soul/')

    def __init__(self,pos):
        super().__init__(pos)
        self.currentstate = states_basic.Once(self)
        self.image = self.sprites.sprite_dict['once'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.timer=0
        self.velocity=[0,0]

    def update(self,scroll):
        super().update(scroll)

        self.timer +=1
        if self.timer>100:#fly to sky
            self.velocity[1]=-20
        elif self.timer>200:
            self.kill()

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0]+self.velocity[0], self.rect.topleft[1] + pos[1]+self.velocity[1]]

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Spawneffect(Animatedentity):#the thing that crets when aila re-spawns
    sprites = Read_files.Sprites_Player('Sprites/GFX/respawn/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.finish = False

    def reset_timer(self):
        self.finish = True
        self.kill()

class Slash(Animatedentity):#thing that pop ups when take dmg or give dmg: GFX
    sprites = Read_files.Sprites_Player('Sprites/GFX/slash/')

    def __init__(self,pos):
        super().__init__(pos)
        state = str(random.randint(1, 3))
        self.currentstate.enter_state('Slash_' + state)
        self.image = self.sprites.sprite_dict['slash_' + state][0]
        self.rect = self.image.get_rect(center=pos)

    def reset_timer(self):
        self.kill()

class Rune_symbol(Animatedentity):#the stuff that will be blitted on uberrunestone
    def __init__(self,pos,ID_key):
        super().__init__(pos)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/rune_symbol/' + ID_key)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.rect.center = pos

    def reset_timer(self):
        pass

class Interactable(Animatedentity):#interactables
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.group = game_objects.interactables
        self.pause_group = game_objects.entity_pause

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

class Spikes(Interactable):#should be an interactable
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/traps/spikes')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (pos[0],pos[1])
        self.hitbox = self.rect.copy()

class Bridge(Interactable):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/bridge/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (pos[0],pos[1])
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
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn
        self.image.set_alpha(0)#make them transparent

    def update(self,scroll):
        self.update_pos(scroll)
        self.group_distance()

    def player_collision(self):
        self.game_objects.load_map(self.destination, self.spawn)

class Path_inter(Interactable):

    def __init__(self, pos, game_objects, size, destination, spawn, image):
        super().__init__(pos, game_objects)
        self.rect = pygame.Rect(pos,size)
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.destionation_area = destination[:destination.rfind('_')]
        self.spawn = spawn
        self.image.set_alpha(0)#make them transparent

    def update(self,scroll):
        self.update_pos(scroll)
        self.group_distance()

    def interact(self):
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
        self.sprites=Read_files.Sprites_Player('Sprites/animations/cave_grass/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)

class Runestones(Interactable):
    def __init__(self, pos, game_objects, state, ID_key):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/runestones/' + ID_key)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world

        if state != "idle":
            self.currentstate = states_basic.Interacted(self)

    def interact(self):
        self.currentstate.handle_input('Transform')#goes to interacted after transform
        self.game_objects.world_state.state[self.game_objects.map.level_name]['runestone'][self.ID_key] = 'interacted'#write in the state dict that this has been picked up

class Uber_runestone(Interactable):
    def __init__(self, pos, game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/uber_runestone/')
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
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
        self.rect.bottomleft = pos
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.health=3
        self.inventory = {'Amber_Droplet':3}
        self.ID_key = ID_key#an ID key to identify which item that the player is intracting within the world
        self.timers = []
        self.timer_jobs = {'invincibility':Invincibility_timer(self,C.invincibility_time_enemy)}

        if state != "idle":
            self.currentstate = states_basic.Interacted(self)

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
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        self.currentstate.handle_input('Opening')
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

class Collision_breakable(Interactable):#a breakable collision block: should it be inetractable instead?
    def __init__(self, pos,game_objects,type = 'type1'):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/block/breakable/'+type+'/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
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
        self.game_objects.player.update_rect()

    def update(self,scroll):
        super().update(scroll)
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
        self.rect.bottomleft = pos
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

    def player_collision(self):#player collision
        self.currentstate.handle_input('Outline')

    def interact(self):#when player press t/y
        if type(self.currentstate).__name__ == 'Outline':#single click
            self.game_objects.player.spawn_point[0]['map']=self.map
            self.game_objects.player.spawn_point[0]['point']=self.init_cord
            self.currentstate.handle_input('Once')
        else:#odoulbe click
            pass

class Inorinoki(Interactable):#the place where you trade soul essence for spirit or heart contrainer
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/inorinoki/')
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = pos
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
        self.rect.bottomleft = pos
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
            new_state = states.Fast_travel_unlock(self.game_objects.game,self)
            new_state.enter_state()
        else:
            self.currentstate.handle_input('Once')
            new_state = states.Fast_travel_menu(self.game_objects.game)
            new_state.enter_state()

class Rhoutta_altar(Interactable):#altar to trigger the cutscane at the beginning
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/animations/rhoutta_altar/')
        self.image = self.sprites.sprite_dict['idle'][0]
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
        self.sprites = Read_files.Sprites_Player('Sprites/animations/sign/')
        self.image = self.sprites.sprite_dict['idle'][0]
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

#UI
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

class Health():
    sprites=Read_files.Sprites_Player('Sprites/UI/gameplay/health/')

    def __init__(self):
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_health.Death(self)

    def update(self):
        self.currentstate.update()
        self.animation.update()

class Spirit():
    sprites=Read_files.Sprites_Player('Sprites/UI/gameplay/spirit/')

    def __init__(self):
        self.image = self.sprites.sprite_dict['death'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]: animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_health.Death(self)

    def update(self):
        self.currentstate.update()
        self.animation.update()

class Sword_potrait():
    def __init__(self):
        self.sprites = Read_files.Sprites_Player("Sprites/Enteties/Items/sword")#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#

    def reset_timer(self):
        pass

class Infinity_stones():
    def __init__(self,sword):
        self.sword = sword
        self.dir = [1,0]#animation and state need this
        self.animation = animation.Entity_animation(self)
        self.currentstate = states_basic.Idle(self)#
        self.description = ''

    def set_pos(self, pos):
        self.rect.center = pos

    def reset_timer(self):
        pass

    def attach(self):
        pass

    def detach(self):
        pass

    def collision(self):#hit enemy
        pass

class Empty_infinity_stone(Infinity_stones):#more dmg
    sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/empty/')#for inventory

    def __init__(self,sword):
        super().__init__(sword)
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()

class Red_infinity_stone(Infinity_stones):#more dmg

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/red/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'red'

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

class Blue_infinity_stone(Infinity_stones):#get spirit at collision

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/blue/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'blue'

    def collision(self):
        self.sword.entity.add_spirit()

class Orange_infinity_stone(Infinity_stones):#bigger hitbox

    def __init__(self,sword):
        super().__init__(sword)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/orange/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
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
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/Items/infinity_stones/purple/')#for inventory
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.colour = 'purple'

    def attach(self):
        pass

    def detach(self):
        pass

class Omamoris():
    def __init__(self,entity):
        self.equipped_omamoris=[]#equiped omamoris
        self.omamori_list=[Double_jump(entity),Loot_magnet(entity),Dash_master(entity)]#omamoris in inventory.
        self.level = 0
        self.number = 3#number of omamori we can equip

    def update(self):
        for omamori in self.equipped_omamoris:
            omamori.update()

    def handle_input(self,input):
        for omamori in self.equipped_omamoris:
            omamori.handle_input(input)

    def level_up(self):
        self.level += 1

    def equip_omamori(self,omamori):
        if omamori not in self.equipped_omamoris:#if not equiped
            if len(self.equipped_omamoris)<self.number:#maximum number of omamoris to equip
                self.equipped_omamoris.append(omamori)
                omamori.attach()
        else:##if equiped -> remove
            self.equipped_omamoris.remove(omamori)
            omamori.detach()#call the detach function of omamori

class Omamori():
    def __init__(self,entity):
        self.entity = entity
        self.dir = [1,0]
        self.animation = animation.Entity_animation(self)#it is called from inventory
        self.currentstate = states_basic.Idle(self)#
        self.image = self.sprites.sprite_dict['idle'][0]
        self.rect = self.image.get_rect()
        self.description = ''

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

class Empty_omamori(Omamori):
    sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/empty_omamori/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)

class Double_jump(Omamori):
    sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/double_jump/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)
        self.counter = 0
        self.description = 'Double jump'

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
    sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/loot_magnet/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)
        self.description = 'Attracts loot'

    def update(self):
        for loot in self.entity.game_objects.loot.sprites():
            loot.attract(self.entity.rect.center)

class Dash_master(Omamori):#makes dash free of charge
    sprites = Read_files.Sprites_Player('Sprites/Enteties/omamori/dash_master/')#for inventory

    def __init__(self,entity):
        super().__init__(entity)
        self.description = 'Free dash'

    def detach(self):
        super().detach()
        self.entity.dash_cost = 1

    def attach(self):
        super().attach()
        self.entity.dash_cost = 0

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
        self.entity.timers.remove(self)

    def update(self):
        self.lifetime -= 1
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
            self.entity.velocity[1] = -10
            self.entity.ground = False
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
