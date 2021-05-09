import pygame

class Entity(pygame.sprite.Sprite):

    acceleration=[1,0.8]
    def __init__(self):
        super().__init__()
        self.movement=[0,0]
        self.velocity=[0,0]
        self.frame = 0
        self.dir=[1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.ac_dir=[0,0]

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

    def update_action(self, new_action):
        if not self.action[new_action]:
            self.action[new_action] = True
            self.timer = 0

    def reset_timer(self):
        self.frame = 0
        self.ac_dir[0]=self.dir[0]
        self.ac_dir[1]=self.dir[1]

class Enemy_1(Entity):

    friction=[0.2,1]
    def __init__(self,pos,ID):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        #self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20}
        self.health=100
        self.dmg=10
        self.ID=ID
        #self.prioriy_list = ['death','hurt','sword','jump','run','stand']
        self.priority_action=['death','hurt','dash','sword','bow']
        self.nonpriority_action=['jump','wall','fall','run','stand']
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'hurt':False,'bow':False,'dash':False,'wall':False,'fall':False,'inv':False}
        self.state = 'stand'
        self.distance=[0,0]
        self.equip='sword'#can change to bow
        self.f_action=['sword','bow']
        self.f_action_cooldown=True
        self.inv=False#flag to check if collision with invisible blocks

    def AI(self,player):#maybe want different AI types depending on eneymy type

        self.distance[0]=(self.rect[0]-player.rect[0])#follow the player
        self.distance[1]=(self.rect[1]-player.rect[1])#follow the player

        if abs(self.distance[0])>200 and abs(self.distance[1])>50 or player.action['death'] or self.action['hurt']:#don't do anything if far away, or player dead or while taking dmg
            self.action['run']=False
            self.action['stand']=True

        elif abs(self.distance[0])>500 or abs(self.distance[1])>500:#remove the enmy if far away
            self.kill()

        elif self.distance[0]<0 and not self.action['death'] and abs(self.distance[1])<40:#if player close on right
            self.dir[0]=1
            self.action['run']=True
            self.action['stand']=False
            if self.distance[0]>-40:#don't get too close
                self.action['run']=False
                self.action['stand']=True

        elif self.distance[0]>0 and not self.action['death'] and abs(self.distance[1])<40:#if player close on left
            self.dir[0]=-1
            self.action['run']=True
            self.action['stand']=False
            if self.distance[0]<40:#don't get too close
                self.action['run']=False
                self.action['stand']=True

        if abs(self.distance[0])<40 and abs(self.distance[1])<40 and not player.action['death']:#swing sword when close
            self.action['sword']=True

    def attack_action(self):
        pass

class Player(Entity):

    friction=[0.2,1]
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health=50
        #self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20, 'stand':1}
        self.dmg=50
        #self.prioriy_list = ['death','hurt','sword','jump','run','stand']
        self.priority_action=['death','hurt','dash','sword','bow']#animation
        self.nonpriority_action=['jump','wall','fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'hurt':False,'bow':False,'dash':False,'wall':False,'fall':False,'inv':False}
        self.state = 'stand'
        self.equip='sword'#can change to bow
        self.f_action=['sword','bow']
        self.f_action_cooldown=True#True means you can use it

    def attack_action(self):
        if self.equip=='sword':
            return Sword(self)#make a sword
        elif self.equip=='bow':
            pass#return Bow(self)

    def dashing(self):
        self.velocity[0]=20*self.dir[0]#dash
        self.action['dash']=True
        self.action[self.equip]=False#cancel attack_action

    def jump(self):
        self.velocity[1]=-11
        self.action['jump']=True
        if self.action['wall']:
            self.velocity[0]=-self.dir[0]*10

class Block(Entity):

    images = {1 : pygame.image.load("sprites/block_castle.png"),
             2 : pygame.image.load("sprites/block_question.png")}

    def __init__(self,img,pos,chunk_key=False):
        super().__init__()
        self.image = self.images[img].convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key

class Invisible_block(Entity):

    def __init__(self,pos):
        super().__init__()
        self.rect=pygame.Rect(pos[0],pos[1],2,2)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

class Items():

    def __init__(self,entity):
        self.rect=pygame.Rect(entity.hitbox.midright[0],entity.hitbox.midright[1],10,15)
        self.hit=False

class Sword(Items):
    def __init__(self,entity):
        super().__init__(entity)
        self.movement=[0,0]

    def update(self,entity):
        if entity.ac_dir[0]>0 and entity.ac_dir[1]==0:#right
            self.rect=pygame.Rect(entity.hitbox.midright[0],entity.hitbox.midright[1]-20,40,40)
        elif entity.ac_dir[0]<0 and entity.ac_dir[1]==0:#left
            self.rect=pygame.Rect(entity.hitbox.midleft[0]-40,entity.hitbox.midleft[1]-20,40,40)
        elif entity.ac_dir[1]>0:#up
            self.rect=pygame.Rect(entity.hitbox.midtop[0]-10,entity.hitbox.midtop[1]-20,20,20)
        elif entity.ac_dir[1]<0:#down
            self.rect=pygame.Rect(entity.hitbox.midtop[0]-10,entity.hitbox.midtop[1]+50,20,20)

class NPC(Entity):
    friction=[0.2,1]
    acceleration=[0.3,0.8]

    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.action={'stand':True,'run':False,'death':False,'hurt':False,'dash':False,'inv':False}
        self.nonpriority_action=['run','stand']
        self.priority_action=['death','hurt','dash']
        self.health=50
        self.state = 'stand'

    def AI(self):
        self.action['run']=True
        if self.action['inv']:#collision with invisble block
            self.velocity[0]=-self.velocity[0]
            self.dir[0]=-self.dir[0]
            self.action['inv']=False
