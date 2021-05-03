import pygame, sys

class Entity(pygame.sprite.Sprite):

    acceleration=[1,0.8]

    def __init__(self):
        super().__init__()
        self.movement=[0,0]
        self.frame = 0
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'hurt':False}
        self.dir=[1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.vdir=0

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

    def update_action(self, new_action):
        if not self.action[new_action]:
            self.action[new_action] = True
            self.timer = 0

    def reset_timer(self):
        self.frame = 0


class Enemy_1(Entity):

    friction=0.2
    def __init__(self,pos,ID):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        #self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20}
        self.velocity=[0,0]
        self.health=100
        self.dmg=10
        self.ID=ID
        self.prioriy_list = ['death','hurt','sword','jump','run','stand']
        self.state = 'stand'

    @staticmethod
    def move(player,group):#maybe want different AI types depending on eneymy type
        enemy_1_list = [i for i in group.sprites() if i.ID==1]#extract all enemy type ID

        for entity in enemy_1_list:#go through the enemy type
            distance=[0,0]
            distance[0]=(entity.rect[0]-player.rect[0])#follow the player
            distance[1]=(entity.rect[1]-player.rect[1])#follow the player

            if abs(distance[0])>200 and abs(distance[1])>50 or player.action['death'] or entity.action['hurt']:#don't do anything if far away, or player dead or while taking dmg
                entity.action['run']=False
                entity.action['stand']=True

            elif abs(distance[0])>500 or abs(distance[1])>500:#remove the enmy if far away
                entity.kill()

            elif distance[0]<0 and not entity.action['death'] and abs(distance[1])<40:#if player close on right
                entity.dir[0]=1
                entity.action['run']=True
                entity.action['stand']=False
                if distance[0]>-40:#don't get too close
                    entity.action['run']=False
                    entity.action['stand']=True

            elif distance[0]>0 and not entity.action['death'] and abs(distance[1])<40:#if player close on left
                entity.dir[0]=-1
                entity.action['run']=True
                entity.action['stand']=False
                if distance[0]<40:#don't get too close
                    entity.action['run']=False
                    entity.action['stand']=True

            if abs(distance[0])<40 and abs(distance[1])<40 and not player.action['death']:#swing sword when close
                entity.action['sword']=True

class Player(Entity):

    friction=0.2
    velocity=[0,0]
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health=50
        #self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20, 'stand':1}
        self.dmg=50
        self.prioriy_list = ['death','hurt','sword','jump','run','stand']
        self.state = 'stand'

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

class Items():

    def __init__(self,entity):
        self.movement=[0,0]
        self.rect=pygame.Rect(entity.hitbox.midright[0],entity.hitbox.midright[1],10,15)

    def update(self,entity):
        if entity.dir[0]>0 and entity.dir[1]==0:#right
            self.rect=pygame.Rect(entity.hitbox.midright[0],entity.hitbox.midright[1]-20,40,40)
        elif entity.dir[0]<0 and entity.dir[1]==0:#left
            self.rect=pygame.Rect(entity.hitbox.midleft[0]-40,entity.hitbox.midleft[1]-20,40,40)
        elif entity.dir[1]>0:#up
            self.rect=pygame.Rect(entity.hitbox.midtop[0]-10,entity.hitbox.midtop[1]-20,20,20)
        elif entity.dir[1]<0:#down
            self.rect=pygame.Rect(entity.hitbox.midtop[0]-10,entity.hitbox.midtop[1]+50,20,20)

#class Sword(Items):
#    def __init__(self,entity):
#        super().__init__()
#        self.rect.center = entity.rect.midright
