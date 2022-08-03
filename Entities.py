import pygame, random, sys, Read_files, particles, animation, states_basic, states_player, states_NPC, states_enemy, states_vatt, states_reindeer, states_bluebird, states_kusa, states_rogue_cultist, math, sound, states
import time

pygame.mixer.init()

class ExtendedGroup(pygame.sprite.Group):#adds a white glow around enteties
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            ExtendedGroup.add_colour(20,(20,20,20),surface,spr.hitbox)#addded this
        self.lostsprites = []

    @staticmethod
    def add_colour(radius,colour,screen,rect):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(rect.x,rect.y),special_flags=pygame.BLEND_RGB_ADD)

class PauseGroup(pygame.sprite.Group):#I guess we don't need it
    def __init__(self):
        super().__init__()

    def update(self, pos):
        for s in self.sprites():
            self.group_distance(s,pos)

    @staticmethod
    def group_distance(s,pos):
        if s.rect[0]<s.bounds[0] or s.rect[0]>s.bounds[1] or s.rect[1]<s.bounds[2] or s.rect[1]>s.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
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
        self.hitbox.center=self.rect.center

class Trigger(Platform):
    def __init__(self,pos,size,values):
        super().__init__(pos,size)
        #will crach if values do not exist
        self.event=values['event']
        self.event_type=values['event_type']

class Invisible_block(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_y(self,entity):
        pass

    def collide_x(self,entity):
        if type(entity).__name__ != "Player":#only apply to enemies and NPC
            entity.dir[0] = -entity.dir[0]#turn around

class Collision_block(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_x(self,entity):
        #check for collisions and get a dictionary of sprites that collides
        if entity.velocity[0]>0:#going to the right
            entity.hitbox.right = self.hitbox.left
            entity.collision_types['right'] = True
        else:#going to the left
            entity.hitbox.left = self.hitbox.right
            entity.collision_types['left'] = True
        entity.update_rect()

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.hitbox.bottom = self.hitbox.top
            entity.collision_types['bottom'] = True
            entity.velocity[1] = 0
        else:#going up
            entity.hitbox.top = self.hitbox.bottom
            entity.collision_types['top'] = True
            entity.velocity[1] = 0 #knock back
        entity.update_rect()

class Collision_oneway_up(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)

    def collide_x(self,entity):
        pass

    def collide_y(self,entity):
        offset=9
        if entity.velocity[1]>0:#going down
            if entity.hitbox.bottom<self.hitbox.top+offset:
                entity.hitbox.bottom = self.hitbox.top
                entity.collision_types['bottom'] = True
                entity.velocity[1] = 0
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
            entity.hitbox.top = target
            entity.collision_types['top'] = True
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
                entity.hitbox.bottom = target
                entity.collision_types['bottom'] = True
                entity.update_rect()

class Spikes(Platform):
    def __init__(self,pos,size):
        super().__init__(pos,size)
        self.image=pygame.image.load("Sprites/block/spkies.png").convert_alpha()
        self.dmg = 10

    def collide_x(self,entity):
        if entity.velocity[0]>0:#going to the right
            entity.velocity[0]=-6#knock back
        else:#going to the left
            entity.velocity[0]=6#knock back
        entity.take_dmg(self.dmg)

    def collide_y(self,entity):
        if entity.velocity[1]>0:#going down
            entity.velocity[1]=-6#knock back
        else:#going up
            entity.velocity[1]=6#knock back
        entity.take_dmg(self.dmg)

class Staticentity(pygame.sprite.Sprite):#no hitbox but image
    def __init__(self,pos,img=pygame.Surface((16,16))):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.bounds=[-200,800,-100,350]#-x,+x,-y,+y: Boundaries to phase out enteties outside screen

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]

    def group_distance(self):
        if self.rect[0]<self.bounds[0] or self.rect[0]>self.bounds[1] or self.rect[1]<self.bounds[2] or self.rect[1]>self.bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
            self.remove(self.group)#remove from group
            self.add(self.pause_group)#add to pause

class BG_Block(Staticentity):
    def __init__(self,pos,img,parallax=1):
        super().__init__(pos,img)
        self.true_pos = self.rect.topleft
        self.parallax=parallax

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + self.parallax*pos[0], self.rect.topleft[1] + self.parallax*pos[1]]
        self.true_pos= [self.true_pos[0] + self.parallax*pos[0], self.true_pos[1] + self.parallax*pos[1]]
        self.rect.topleft = self.true_pos

class BG_Animated(BG_Block):
    def __init__(self,pos,sprite_folder_path,parallax=1):
        super().__init__(pos,pygame.Surface((16,16)),parallax)
        self.sprites = Read_files.load_sprites(sprite_folder_path)
        self.image = self.sprites[0]
        self.animation=animation.Simple_animation(self)

    def update(self, pos):
        self.update_pos(pos)
        self.animation.update()

class Dynamicentity(Staticentity):
    def __init__(self,pos):
        super().__init__(pos)
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.go_through = False#a flag for entities to go through ramps from side or top

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.bottom=self.rect.bottom

    def update_hitbox(self):
        self.hitbox.midbottom = self.rect.midbottom#[self.rect.bottom + self.hitbox_offset[0], self.rect.bottom + self.hitbox_offset[1]]

    def update_rect(self):
        self.rect.midbottom = self.hitbox.midbottom#[self.hitbox.bottom - self.hitbox_offset[0], self.hitbox.bottom - self.hitbox_offset[1]]

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.midbottom = self.rect.midbottom

class Character(Dynamicentity):#enemy, NPC,player
    def __init__(self,pos,game_objects):
        super().__init__(pos)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.acceleration=[1,0.7]
        self.velocity=[0,0]
        self.friction=[0.2,0]
        self.animation_stack=[animation.Entity_animation(self)]
        self.max_vel=7
        self.game_objects = game_objects

    def update(self,pos):
        self.update_pos(pos)
        self.currentstate.update()
        self.animation_stack[-1].update()

    def take_dmg(self,dmg):
        if dmg>0:
            self.health-=dmg
            if self.health>0:#check if dead¨
                self.animation_stack[-1].handle_input('Hurt')
                self.currentstate.handle_input('Hurt')#handle if we shoudl go to hurt state
            else:
                if self.currentstate.state_name!='death':#if not already dead
                    self.currentstate.enter_state('Death')#overrite any state and go to death

    def knock_back(self,dir):
        self.velocity[0]=dir*30

    def hurt_particles(self,dir,number_particles=12):
        for i in range(0,number_particles):
            obj1=particles.General_particle(self.hitbox.center,distance=0,type='circle',lifetime=20,vel=[1,10],dir=dir,scale=1)
            self.game_objects.cosmetics.add(obj1)

class Player(Character):

    sfx_sword = pygame.mixer.Sound("Audio/SFX/utils/sword_3.ogg")

    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/aila/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,35)
        self.rect.midbottom=self.hitbox.midbottom#match the positions of hitboxes
        self.max_vel = 4

        self.max_health = 250
        self.max_spirit = 100
        self.health = 100
        self.spirit = 100

        self.projectiles = game_objects.fprojectiles

        self.abilities={'Thunder':Thunder,'Force':Force,'Arrow':Arrow,'Heal':Heal,'Darksaber':Darksaber}#the objects are referensed but created in states
        self.equip='Thunder'#ability pointer
        self.sword=Aila_sword(self)
        self.shield=Shield
        self.dash=True
        self.wall=True

        self.spawn_point = [{'map':'light_forest', 'point':'1'}]#a list of len 2. First if sejt, always tehre. Can append positino for bone, which will pop after use
        self.inventory = {'Amber_Droplet':23,'Bone':2,'Soul_essence':10,'Tungsten':10}#the keys need to have the same name as their respective classes
        self.omamoris = Omamoris(self)
        self.currentstate = states_player.Idle(self)

        self.set_abs_dist()

    def set_abs_dist(self):#the absolute distance, i.e. the total scroll
        self.abs_dist = [247,180]#the coordinate for buring the bone

    def death(self):
        map=self.game_objects.map.level_name
        pos=[self.rect[0],self.rect[1]]
        self.game_objects.cosmetics.add(Player_Soul(pos))
        new_game_state = states.Cutscene_engine(self.game_objects.game,'Death')
        new_game_state.enter_state()
        self.set_abs_dist()

    def enter_idle(self):
        self.currentstate = states_player.Idle(self)

    def reset_movement(self):
        self.velocity = [0,0]
        self.acceleration = [0,0.7]
        self.friction = [0.24,0]

    def update(self,pos):
        super().update(pos)
        self.abs_dist = [self.abs_dist[0] - pos[0], self.abs_dist[1] - pos[1]]
        self.omamoris.update()

    def to_json(self):#things to save: needs to be a dict
        health={'max_health':self.max_health,'max_spirit':self.max_spirit,'health':self.health,'spirit':self.spirit}

        abilities={}
        for key,ability in self.abilities.items():
            abilities[key]=True
        abilities['dash']=self.dash
        abilities['wall']=self.wall

        save_dict = {'spawn_point':self.spawn_point,'inventory':self.inventory,'health':health,'abilities':abilities}
        return save_dict

    def from_json(self,data):#things to load. data is a dict
        self.max_health=data['health']['max_health']
        self.max_spirit=data['health']['max_spirit']
        self.health=data['health']['health']
        self.spirit=data['health']['spirit']

        self.dash=data['abilities']['dash']
        self.wall=data['abilities']['wall']

        self.inventory=data['inventory']

        self.abilities={}
        for ability in data['abilities'].keys():
            if ability == 'dash' or ability == 'wall':
                pass
            else:
                self.abilities[ability]=getattr(sys.modules[__name__], ability)

class Enemy(Character):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.projectiles = game_objects.eprojectiles
        self.group = game_objects.enemies
        self.pause_group = game_objects.entity_pause

        self.inventory = {'Amber_Droplet':random.randint(0, 10),'Bone':2}#random.randint(0, 10)
        self.counter=0
        self.AImethod=self.peaceAI
        self.player_distance=[0,0]
        self.aggro=True#colliding with player
        self.max_vel=3
        self.friction=[0.5,0]
        self.currentstate = states_enemy.Idle(self)
        self.attack_distance = 0#when try to hit
        self.dmg = 10#sword damage
        self.aggro_distance = 200#when ot become aggro
        self.spirit = 100

    def update(self,pos):
        super().update(pos)
        self.AI()
        self.group_distance()#need to be before currentstate.update(): fails sometimes

    def player_collision(self):#when player collides with enemy
        if self.aggro:
            self.game_objects.player.take_dmg(10)
            sign=(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
            if sign>0:
                self.game_objects.player.knock_back(1)
            else:
                self.game_objects.player.knock_back(-1)

    def death(self):
        self.aggro=False
        self.kill()

    def loots(self):
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj = getattr(sys.modules[__name__], key)([self.rect.x,self.rect.y])#make a class based on the name of the key: need to import sys
                self.game_objects.loot.add(obj)
            self.inventory[key]=0

    def countered(self):#player shield
        self.velocity[0] = -30*self.dir[0]
        duration = 30
        self.currentstate = states_enemy.Stun(self,duration)#should it overwrite?

    def AI(self):
        self.player_distance=[self.game_objects.player.rect.center[0]-self.rect.centerx,self.game_objects.player.rect.center[1]-self.rect.centerx]#check plater distance
        self.counter += 1
        self.AImethod()#run ether aggro- or peace-AI

    def cutsceneAI(self):#do nothing
        pass

    def peaceAI(self):
        if self.counter>20:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.currentstate.handle_input('Idle')
            else:
                self.dir[0] = -self.dir[0]
                self.currentstate.handle_input('Walk')
        if abs(self.player_distance[0])<self.aggro_distance:
            self.AImethod=self.aggroAI

    def aggroAI(self):
        if self.counter < 40:
            pass
        else:
            if self.player_distance[0] > self.attack_distance:
                self.dir[0] = 1
                self.currentstate.handle_input('Walk')
            elif abs(self.player_distance[0]) < self.attack_distance:

                if self.player_distance[0]>0:
                    self.dir[0]=1
                else:
                    self.dir[0]=-1

                self.currentstate.handle_input('Attack')
                self.counter = 0
            elif self.player_distance[0] < -self.attack_distance:
                self.dir[0] = -1
                self.currentstate.handle_input('Walk')
            else:
                self.counter = 0
                self.currentstate.handle_input('Idle')

        if abs(self.player_distance[0])>self.aggro_distance:
            self.AImethod=self.peaceAI

class Slime(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/slime/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,16)
        self.health = 50
        self.spirit=100

    def update(self,pos):
        super().update(pos)

class Woopie(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = pygame.image.load("Sprites/Enteties/enemies/woopie/main/Idle/Kodama_stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1
        self.spirit=100
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')

class Vatt(Enemy):

    aggro = False  #remember to turn false when changing maps
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.image = pygame.image.load("Sprites/Enteties/enemies/vatt/main/idle/idle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 30
        self.spirit = 30
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/vatt/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.currentstate = states_vatt.Idle(self)
        self.aggro=False
        self.attack_distance = 60

    def updateAI(self):
        if Vatt.aggro and not self.aggro:
            self.currentstate.enter_state('Transform')#also sets to aggro AI
            self.aggro = True
            #self.AImethod=self.aggroAI

    def peaceAI(self):
        if self.counter>70:
            self.counter=0
            rand=random.randint(0,6)
            if rand<2:
                self.currentstate.handle_input('Idle')
            else:
                self.currentstate.handle_input('Walk')

    def aggroAI(self):
        if self.counter < 40:
            pass
        else:
            if self.player_distance[0] > self.attack_distance:
                self.dir[0] = 1
                self.currentstate.handle_input('Run')
            elif self.player_distance[0] < -self.attack_distance:
                self.dir[0] = -1
                self.currentstate.handle_input('Run')
            else:
                self.counter = 0
                self.currentstate.handle_input('Javelin')

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

    def knock_back(self,dir):
        pass

    def peaceAI(self):
        if abs(self.player_distance[0])<100:
            self.currentstate.handle_input('Fly')
        else:
            rand=random.randint(0,100)
            if rand==1:
                self.currentstate.handle_input('Idle')
            elif rand==2:
                self.currentstate.handle_input('Walk')
            elif rand==3:
                self.currentstate.handle_input('Eat')
            elif rand==4:
                self.dir[0]=-self.dir[0]

class Shroompolin(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/shroompolin/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],64,64)
        self.jump_box=pygame.Rect(pos[0],pos[1],32,10)
        self.aggro=False

    def player_collision(self):
        offset=9
        if self.game_objects.player.velocity[1]>0:#going down
            if self.game_objects.player.hitbox.bottom<self.jump_box.top+offset:
                self.game_objects.player.velocity[1] = -10
                self.currentstate.enter_state('Hurt')

    def update_hitbox(self):
        super().update_hitbox()
        self.jump_box.midtop = self.rect.midtop

    def update(self,pos):
        super().update(pos)

    def take_dmg(self,dmg):
        pass

    def peaceAI(self):
        pass

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

    def peaceAI(self):
        if abs(self.player_distance[0])<150:
            self.AImethod=self.aggroAI
            self.currentstate.handle_input('Transform')

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

    def peaceAI(self):
        if abs(self.player_distance[0])<150:
            self.AImethod=self.aggroAI
            self.currentstate.handle_input('Transform')

    def suicide(self):
        self.projectiles.add(Explosion(self,dmg=10))
        self.game_objects.camera[-1].camera_shake(amp=2,duration=30)#amplitude and duration

class Egg(Enemy):#change design
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites=Read_files.Sprites_Player('Sprites/Enteties/enemies/egg/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],64,64)
        self.health = 1
        self.number = random.randint(1, 4)

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

    def peaceAI(self):
        pass

    def aggroAI(self):
        pass

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

    def cutsceneAI(self):
        pass

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

    def cutsceneAI(self):
        pass

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
        self.counter=0

    def load_conversation(self):
        self.conversation = Read_files.read_json("Text/NPC/" + self.name + ".json")

    #returns conversation depdening on worldstate input. increases index
    def get_conversation(self, flag):
        try:
            conv = self.conversation[flag][str(self.conv_index)]
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
        self.counter+=1
        if self.counter>100:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.idle()
            else:
                self.walk()

    def buisness(self):#enters after conversation
        pass

class Aslat(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Sahkar(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

class Astrid(NPC):#vendor
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)
        self.inventory={'Bone':10,'Amber_Droplet':1}#itam+price

    def buisness(self):
        new_state = states.Vendor(self.game_objects.game, self)
        new_state.enter_state()

class MrSmith(NPC):
    def __init__(self, pos,game_objects):
        super().__init__(pos,game_objects)

    def buisness(self):
        new_state = states.Smith(self.game_objects.game, self)
        new_state.enter_state()

class MrBanks(NPC):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.ammount = 0

    def buisness(self):
        new_state = states.Bank(self.game_objects.game, self)
        new_state.enter_state()

class Boss(Enemy):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def death(self):
        self.aggro=False
        self.AImethod = self.cutsceneAI
        self.give_abillity()
        new_game_state = states.Cutscene_engine(self.game_objects.game,'Defeated_boss')
        new_game_state.enter_state()

    def give_abillity(self):
        self.game_objects.player.abilities[self.ability]=getattr(sys.modules[__name__], self.ability)

class Reindeer(Boss):
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/boss/reindeer/')
        self.image = self.sprites.sprite_dict['main']['idle'][0]#pygame.image.load("Sprites/Enteties/boss/cut_reindeer/main/idle/Reindeer walk cycle1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],40,50)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.currentstate = states_reindeer.Idle(self)

        self.health = 1
        self.spirit = 1
        self.attack = Sword

    def give_abillity(self):
        self.game_objects.player.dash=True

    def update(self,pos):
        super().update(pos)

    def peaceAI(self):
        pass

    def aggroAI(self):
        if self.counter < 40:
            pass
        else:
            if self.player_distance[0] > self.attack_distance:
                self.dir[0] = 1

                if random.randint(0, 100)==100:
                    self.currentstate.handle_input('Dash')
                else:
                    self.currentstate.handle_input('Walk')

            elif abs(self.player_distance[0])<self.attack_distance:
                self.currentstate.handle_input('Attack')
                self.counter = 0

            elif self.player_distance[0] < -self.attack_distance:
                self.dir[0] = -1

                if random.randint(0, 100)==100:
                    self.currentstate.handle_input('Dash')
                else:
                    self.currentstate.handle_input('Walk')
            else:
                self.counter = 0
                self.currentstate.handle_input('Idle')

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

class Path_col(Staticentity):

    def __init__(self, pos, size, destination, spawn):
        super().__init__(pos, pygame.Surface(size))
        self.rect.bottomleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.destination = destination
        self.spawn = spawn

    def update(self, pos):
        super().update(pos)
        self.hitbox.center = self.rect.center

class Camera_Stop(Staticentity):

    def __init__(self,size,pos,dir):
        super().__init__(pos,pygame.Surface(size))
        self.hitbox = self.rect.inflate(0,0)
        self.dir = dir

    def update(self, pos):
        super().update(pos)
        self.hitbox.center = self.rect.center

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

class Abilities(pygame.sprite.Sprite):
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
        self.kill()

    def collision_plat(self):
        pass

    def reset_timer(self):
        if self.state == 'post':
            self.kill()

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
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,100,100)
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
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,40,40)
        self.hitbox = self.rect.copy()

    def collision_enemy(self,collision_enemy):
        self.sword_jump()
        collision_enemy.knock_back(self.dir[0])
        collision_enemy.hurt_particles(self.dir[0])
        #slash=Slash([collision_enemy.rect.x,collision_enemy.rect.y])#self.entity.cosmetics.add(slash)
        if self.dir[0]>0:
            self.clash_particles(self.rect.midright,self.dir[0])
        else:
            self.clash_particles(self.rect.midleft,self.dir[0])
        self.kill()

    def sword_jump(self):
        if self.dir[1] == -1:
            self.entity.velocity[1] = -11

    def clash_particles(self,pos,dir,number_particles=12):
        angle=random.randint(-180, 180)#the ejection anglex
        for i in range(0,number_particles):
            #obj2 = Sword_particles(pos,dir)
            #self.group.add(obj2)
            obj1=particles.General_particle(pos,distance=0,type='spark',lifetime=10,vel=[7,14],dir=angle,scale=0.3)
            #obj1 = particles.Sword_sparks(pos,dir)
            self.entity.game_objects.cosmetics.add(obj1)

class Aila_sword(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.dmg = 10

    #potrait stuff
    def init(self):
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

    def clash_particles(self,pos,dir,number_particles=12):
        angle = random.randint(-180, 180)#the ejection anglex
        for i in range(0,number_particles):
            obj1=particles.General_particle(pos,distance=0,type='spark',lifetime=10,vel=[7,14],dir=angle,scale=0.3,colour=self.colour[self.equip])
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

class Dynamic_animated(Dynamicentity):#animated stuff with hitbox
    def __init__(self,pos):
        super().__init__(pos)
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_basic.Idle(self)

    def update(self,scroll):
        self.update_pos(scroll)
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):
        pass

    def attract(self,pos):#the omamori calls on this in loot group
        pass

class Heart_container(Dynamic_animated):

    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/heart_container/')

    def __init__(self,pos,game_objects = None):
        super().__init__(pos)
        self.game_objects = game_objects#Soul_essence requries game_objects and it is the same static stamp
        self.velocity=[0,0]
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heart container'

    def update(self,scroll):
        super().update(scroll)
        self.velocity[1]=3

    def pickup(self,player):
        player.max_health += 1
        #a cutscene?
        self.kill()

class Spirit_container(Dynamic_animated):

    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/spirit_container/')

    def __init__(self,pos,game_objects = None):
        super().__init__(pos)
        self.game_objects = game_objects#Soul_essence requries game_objects and it is the same static stamp
        self.velocity=[0,0]
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A spirit container'

    def update(self,scroll):
        super().update(scroll)
        self.velocity[1]=3

    def pickup(self,player):
        player.max_spirit += 1
        #a cutscene?
        self.kill()

class Soul_essence(Dynamic_animated):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/soul_essence/')

    def __init__(self,pos,game_objects = None):
        super().__init__(pos)
        self.game_objects = game_objects
        self.velocity=[0,0]
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A essence container'

    def pickup(self,player):
        player.inventory['Soul_essence'] += 1
        #a cutscene?
        self.kill()

    def update(self,scroll):
        super().update(scroll)
        obj1 = particles.General_particle(self.rect.center,distance=100,lifetime=20,vel=[2,4],type='spark',dir='isotropic')
        self.game_objects.cosmetics.add(obj1)

class Tungsten(Dynamic_animated):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/tungsten/')

    def __init__(self,pos,game_objects = None):
        super().__init__(pos)
        self.game_objects = game_objects#Soul_essence requries game_objects and it is the same static stamp
        self.velocity=[0,0]
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        self.description = 'A heavy rock'

    def pickup(self,player):
        player.inventory['Tungsten'] += 1
        #a cutscene?
        self.kill()

class Enemy_drop(Dynamic_animated):
    def __init__(self,pos):
        super().__init__(pos)
        self.velocity=[random.randint(-3, 3),-4]
        self.lifetime=500

    def check_collisions(self):
        if self.collision_types['bottom']:
            self.velocity[0] = 0.5*self.velocity[0]
            self.velocity[1] = -0.7*self.velocity[1]
        elif self.collision_types['right'] or self.collision_types['left']:
            self.velocity[0] = -self.velocity[0]

    def update_vel(self):
        self.velocity[1] += 0.5

    def update(self,pos):
        self.check_collisions()#need to be before super.update
        self.update_vel()
        self.lifetime-=1
        super().update(pos)
        self.destory()

    def attract(self,pos):#the omamori calls on this in loot group
        if self.lifetime < 350:
            self.velocity=[0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def pickup(self,player):
        obj=(self.__class__.__name__)#get the loot in question
        player.inventory[obj]+=1
        self.kill()

class Amber_Droplet(Enemy_drop):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/amber_droplet/')

    def __init__(self,pos):
        super().__init__(pos)
        self.rect = pygame.Rect(pos[0],pos[1],5,5)#resize the rect
        self.hitbox = self.rect.copy()
        self.description = 'moneyy'

class Bone(Enemy_drop):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/bone/')

    def __init__(self,pos):
        super().__init__(pos)
        self.image = self.sprites['idle'][0]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.hitbox = self.rect.copy()
        self.description = 'Ribs from my daugther. You can respawn and stuff'

    def use_item(self,player):
        if player.inventory['Bone']>0:#if we have bones
            player.inventory['Bone']-=1
            if len(player.spawn_point)==2:#if there is already a bone
                player.spawn_point.pop()
            player.spawn_point.append({'map':player.game_objects.map.level_name, 'point':player.abs_dist})
            player.currentstate = states_player.Plant_bone(player)

class Spiritsorb(Enemy_drop):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/spiritorbs/')

    def __init__(self,pos):
        super().__init__(pos)
        rand_pos=[random.randint(-10, 10),random.randint(-10, 10)]
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0]+rand_pos[0],pos[1]+rand_pos[1],5,5)
        self.hitbox=self.rect.copy()

    def update_vel(self):
        self.velocity=[0.1*random.randint(-10, 10),0.1*random.randint(-10, 10)]

    def pickup(self,player):
        player.spirit += 10
        self.kill()

class Animatedentity(Staticentity):#animated stuff that doesn't move around
    def __init__(self,pos):
        super().__init__(pos)
        self.animation = animation.Basic_animation(self)
        self.currentstate = states_basic.Idle(self)

    def update(self,scroll):
        self.update_pos(scroll)
        self.currentstate.update()
        self.animation.update()

    def reset_timer(self):
        pass

class Player_Soul(Animatedentity):
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

class Spawneffect(Animatedentity):
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
        self.state=str(random.randint(1, 3))
        self.image = self.sprites[self.state][0]

    def reset_timer(self):
        self.kill()

class Interactable(Animatedentity):
    def __init__(self,pos):
        super().__init__(pos)
        self.interacted=False

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

    def interact(self):
        self.interacted=True

class Interactable_bushes(Interactable):
    def __init__(self,pos,game_objects,type):
        super().__init__(pos)
        self.game_objects = game_objects
        self.group = game_objects.interacting_cosmetics
        self.pause_group=game_objects.entity_pause

        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/'+type+'/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def update(self,scroll):
        super().update(scroll)
        self.group_distance()

    def collide(self):
        if not self.interacted:
            self.currentstate.handle_input('Hurt')
            self.interacted = True

    def cut(self):
        self.currentstate.handle_input('Cut')

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

class Door(Interactable):

    def __init__(self,pos):
        super().__init__(pos)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/Door/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        super().interact()
        self.currentstate.handle_input('Opening')
        try:
            self.game_objects.change_map(collision.next_map)
        except:
            pass

class Chest(Interactable):
    def __init__(self,pos,id,loot,state):
        super().__init__()
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/Chest/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-5)
        self.hitbox = self.rect.inflate(0,0)
        self.ID = id
        self.loot = {loot:1}
        if state == "opened":
            self.interacted = True
            self.currentstate = states_basic.Open(self)

    def interact(self):
        super().interact()
        try:
            chest_id = self.ID
            self.game_objects.map_state[self.game_objects.map.level_name]["chests"][self.ID][1] = "opened"
        except:
            pass

class Chest_Big(Chest):
    def __init__(self,pos,id,loot,state):
        super().__init__(pos,id,loot,state)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/Chest_big/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-13)
        self.hitbox = self.rect.inflate(0,0)

class Spawnpoint(Interactable):
    def __init__(self,pos,map):
        super().__init__(pos)
        self.sprites=Read_files.Sprites().load_all_sprites('Sprites/animations/Spawnpoint/')
        self.image = self.sprites[self.state][0]
        self.rect = self.image.get_rect()
        self.rect.center = (pos[0],pos[1]-16)
        self.hitbox=self.rect.copy()
        self.init_cor=pos
        self.map = map

    def interact(self,entity):
        if type(self.currentstate).__name__ == 'Idle':#single click
            entity.spawn_point[0]['map']=self.map
            entity.spawn_point[0]['point']=self.init_cor
            self.currentstate.handle_input('Once')
        else:#odoulbe click
            new_state = states.Soul_essence(entity.game_objects.game)
            new_state.enter_state()

    def reset_timer(self):
        self.currentstate.handle_input('Idle')

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

class Green_infinity_stone(Infinity_stones):#faster slash, changing framerate

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
        self.omamori_list=[Double_jump(entity),Loot_magnet(entity),More_spirit(entity)]#omamoris inventory.

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
