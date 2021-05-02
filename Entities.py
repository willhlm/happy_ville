import pygame, sys

class Organisms(pygame.sprite.Sprite):

    acceleration=[1,1]
    friction=0.2

    def __init__(self):
        super().__init__()
        self.movement=[0,0]
        self.frame={'stand':1,'run':1,'sword':1,'jump':1,'death':1,'dmg':1}
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'dmg':False}
        self.dir=[1,0]#[horixontal (right 1, left -1),vertical (up 1, down -1)]

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Enemy_1(Organisms):
    images={1: pygame.image.load("sprites/HeroKnight_Run_0.png"),#right
            2: pygame.image.load("sprites/HeroKnight_Run_1.png"),#right
            3: pygame.image.load("sprites/HeroKnight_Run_2.png"),#right
            4: pygame.image.load("sprites/HeroKnight_Run_3.png"),#right
            5: pygame.image.load("sprites/HeroKnight_Run_4.png"),#right
            6: pygame.image.load("sprites/HeroKnight_Run_5.png"),#right
            7: pygame.image.load("sprites/HeroKnight_Run_6.png"),#right
            8: pygame.image.load("sprites/HeroKnight_Run_7.png"),#right
            9: pygame.image.load("sprites/HeroKnight_Run_8.png"),#right
            10: pygame.image.load("sprites/HeroKnight_Run_9.png"),#right
            11: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_0.png"),True,False),#left
            12: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_1.png"),True,False),#left
            13: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_2.png"),True,False),#left
            14: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_3.png"),True,False),#left
            15: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_4.png"),True,False),#left
            16: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_5.png"),True,False),#left
            17: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_6.png"),True,False),#left
            18: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_7.png"),True,False),#left
            19: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_8.png"),True,False),#left
            20: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_9.png"),True,False),#left
            21: pygame.image.load("sprites/HeroKnight_Jump_0.png"),#jumpright
            22: pygame.image.load("sprites/HeroKnight_Jump_1.png"),#jumpright
            23: pygame.image.load("sprites/HeroKnight_Jump_2.png"),#jumpright
            24: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Jump_0.png"),True,False),#jumpleft
            25: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Jump_1.png"),True,False),#jumpleft
            26: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Jump_2.png"),True,False),#jumpleft
            27: pygame.image.load("sprites/HeroKnight_Death_1.png"),#death
            28: pygame.image.load("sprites/HeroKnight_Death_2.png"),#death
            29: pygame.image.load("sprites/HeroKnight_Death_3.png"),#death
            30: pygame.image.load("sprites/HeroKnight_Death_4.png"),#death
            31: pygame.image.load("sprites/HeroKnight_Death_5.png"),#death
            32: pygame.image.load("sprites/HeroKnight_Death_6.png"),#death
            33: pygame.image.load("sprites/HeroKnight_Death_7.png"),#death
            34: pygame.image.load("sprites/HeroKnight_Death_8.png"),#death
            35: pygame.image.load("sprites/HeroKnight_Death_9.png"),#death
            36: pygame.image.load("sprites/HeroKnight_Hurt_1.png"),#dmg
            37: pygame.image.load("sprites/HeroKnight_Hurt_2.png")}#dmg

    images_sword={1: pygame.image.load("sprites/HeroKnight_Attack3_0.png"),#right
                  2: pygame.image.load("sprites/HeroKnight_Attack3_1.png"),#right
                  3: pygame.image.load("sprites/HeroKnight_Attack3_2.png"),#right
                  4: pygame.image.load("sprites/HeroKnight_Attack3_3.png"),#right
                  5: pygame.image.load("sprites/HeroKnight_Attack3_4.png"),#right
                  6: pygame.image.load("sprites/HeroKnight_Attack3_5.png"),#right
                  7: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_0.png"),True, False),#left
                  8: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_1.png"),True, False),#left
                  9: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_2.png"),True, False),#left
                  10: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_3.png"),True, False),#left
                  11: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_4.png"),True, False),#left
                  12: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_5.png"),True, False),#left
                  13: pygame.image.load("sprites/HeroKnight_Attack1_0.png"),#upright
                  14: pygame.image.load("sprites/HeroKnight_Attack1_1.png"),#upright
                  15: pygame.image.load("sprites/HeroKnight_Attack1_2.png"),#upright
                  16: pygame.image.load("sprites/HeroKnight_Attack1_3.png"),#upright
                  17: pygame.image.load("sprites/HeroKnight_Attack1_4.png"),#upright
                  18: pygame.image.load("sprites/HeroKnight_Attack1_5.png"),#upright
                  19: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_0.png"),True, False),#upleft
                  20: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_1.png"),True, False),#upleft
                  21: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_2.png"),True, False),#upleft
                  22: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_3.png"),True, False),#upleft
                  23: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_4.png"),True, False),#upleft
                  24: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_5.png"),True, False),#upleft
                  25: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_0.png"),True, False),#down
                  26: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_1.png"),True, False),#down
                  27: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_2.png"),True, False),#down
                  28: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_3.png"),True, False),#down
                  29: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_4.png"),True, False),#down
                  30: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_5.png"),True, False)}#down

    velocity=[0,0]
    def __init__(self,pos,ID):
        super().__init__()
        self.image = self.images[1]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20}

        self.health=100
        self.dmg=10
        self.ID=ID

    @staticmethod
    def move(player,group):#maybe want different AI types depending on eneymy type
        enemy_1_list = [i for i in group.sprites() if i.ID==1]#extract all enemy type ID

        for entity in enemy_1_list:#go through the enemy type
            distance=[0,0]
            distance[0]=(entity.rect[0]-player.rect[0])#follow the player
            distance[1]=(entity.rect[1]-player.rect[1])#follow the player

            if abs(distance[0])>200 and abs(distance[1])>50 or player.action['death'] or entity.action['dmg']:#don't do anything if far away, or player dead or while taking dmg
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

            if abs(distance[0])<40 and abs(distance[1])<40:#swing sword when close
                entity.action['sword']=True

class Player(Organisms):

    images={1: pygame.image.load("sprites/HeroKnight_Run_0.png"),#right
            2: pygame.image.load("sprites/HeroKnight_Run_1.png"),#right
            3: pygame.image.load("sprites/HeroKnight_Run_2.png"),#right
            4: pygame.image.load("sprites/HeroKnight_Run_3.png"),#right
            5: pygame.image.load("sprites/HeroKnight_Run_4.png"),#right
            6: pygame.image.load("sprites/HeroKnight_Run_5.png"),#right
            7: pygame.image.load("sprites/HeroKnight_Run_6.png"),#right
            8: pygame.image.load("sprites/HeroKnight_Run_7.png"),#right
            9: pygame.image.load("sprites/HeroKnight_Run_8.png"),#right
            10: pygame.image.load("sprites/HeroKnight_Run_9.png"),#right
            11: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_0.png"),True,False),#left
            12: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_1.png"),True,False),#left
            13: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_2.png"),True,False),#left
            14: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_3.png"),True,False),#left
            15: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_4.png"),True,False),#left
            16: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_5.png"),True,False),#left
            17: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_6.png"),True,False),#left
            18: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_7.png"),True,False),#left
            19: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_8.png"),True,False),#left
            20: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Run_9.png"),True,False),#left
            21: pygame.image.load("sprites/HeroKnight_Jump_0.png"),#jumpright
            22: pygame.image.load("sprites/HeroKnight_Jump_1.png"),#jumpright
            23: pygame.image.load("sprites/HeroKnight_Jump_2.png"),#jumpright
            24: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Jump_0.png"),True,False),#jumpleft
            25: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Jump_1.png"),True,False),#jumpleft
            26: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Jump_2.png"),True,False),#jumpleft
            27: pygame.image.load("sprites/HeroKnight_Death_1.png"),#death
            28: pygame.image.load("sprites/HeroKnight_Death_2.png"),#death
            29: pygame.image.load("sprites/HeroKnight_Death_3.png"),#death
            30: pygame.image.load("sprites/HeroKnight_Death_4.png"),#death
            31: pygame.image.load("sprites/HeroKnight_Death_5.png"),#death
            32: pygame.image.load("sprites/HeroKnight_Death_6.png"),#death
            33: pygame.image.load("sprites/HeroKnight_Death_7.png"),#death
            34: pygame.image.load("sprites/HeroKnight_Death_8.png"),#death
            35: pygame.image.load("sprites/HeroKnight_Death_9.png"),#death
            36: pygame.image.load("sprites/HeroKnight_Hurt_1.png"),#dmg
            37: pygame.image.load("sprites/HeroKnight_Hurt_2.png")}#dmg

    images_sword={1: pygame.image.load("sprites/HeroKnight_Attack3_0.png"),#right
                  2: pygame.image.load("sprites/HeroKnight_Attack3_1.png"),#right
                  3: pygame.image.load("sprites/HeroKnight_Attack3_2.png"),#right
                  4: pygame.image.load("sprites/HeroKnight_Attack3_3.png"),#right
                  5: pygame.image.load("sprites/HeroKnight_Attack3_4.png"),#right
                  6: pygame.image.load("sprites/HeroKnight_Attack3_5.png"),#right
                  7: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_0.png"),True, False),#left
                  8: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_1.png"),True, False),#left
                  9: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_2.png"),True, False),#left
                  10: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_3.png"),True, False),#left
                  11: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_4.png"),True, False),#left
                  12: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack3_5.png"),True, False),#left
                  13: pygame.image.load("sprites/HeroKnight_Attack1_0.png"),#upright
                  14: pygame.image.load("sprites/HeroKnight_Attack1_1.png"),#upright
                  15: pygame.image.load("sprites/HeroKnight_Attack1_2.png"),#upright
                  16: pygame.image.load("sprites/HeroKnight_Attack1_3.png"),#upright
                  17: pygame.image.load("sprites/HeroKnight_Attack1_4.png"),#upright
                  18: pygame.image.load("sprites/HeroKnight_Attack1_5.png"),#upright
                  19: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_0.png"),True, False),#upleft
                  20: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_1.png"),True, False),#upleft
                  21: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_2.png"),True, False),#upleft
                  22: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_3.png"),True, False),#upleft
                  23: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_4.png"),True, False),#upleft
                  24: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack1_5.png"),True, False),#upleft
                  25: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_0.png"),True, False),#down
                  26: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_1.png"),True, False),#down
                  27: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_2.png"),True, False),#down
                  28: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_3.png"),True, False),#down
                  29: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_4.png"),True, False),#down
                  30: pygame.transform.flip(pygame.image.load("sprites/HeroKnight_Attack2_5.png"),True, False)}#down

    velocity=[0,0]
    def __init__(self,pos):
        super().__init__()
        self.image = self.images[1]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health=50
        self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20}
        self.dmg=50

    def move(self):#define the movements

        #game input
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.action['run']=True
                    self.action['stand']=False
                    self.dir[0]=1
                if event.key == pygame.K_LEFT:
                    self.action['run']=True
                    self.action['stand']=False
                    self.dir[0]=-1
                if event.key == pygame.K_UP:#press up
                    self.dir[1]=1
                if event.key == pygame.K_DOWN:#press down
                    self.dir[1]=-1
                if event.key==pygame.K_SPACE and self.action['jump']==False:#jump
                    self.movement[1]=-10
                    self.action['jump']=True
                if event.key==pygame.K_f:
                    self.action['sword']=True

            elif event.type == pygame.KEYUP:#lift bottom
                if event.key == pygame.K_RIGHT and self.dir[0]>0:
                    self.action['stand']=True
                    self.action['run']=False
                if event.key == pygame.K_LEFT and self.dir[0]<0:
                    self.action['stand']=True
                    self.action['run']=False
                if event.key == pygame.K_UP:
                    self.dir[1]=0
                if event.key == pygame.K_DOWN:
                    self.dir[1]=0

class Block(Organisms):

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
