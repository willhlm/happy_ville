import pygame, Read_files

class Entity(pygame.sprite.Sprite):

    acceleration=[1,0.8]

    def __init__(self):
        super().__init__()
        self.movement=[0,0]
        self.velocity=[0,0]
        self.frame = 0
        self.dir=[1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.ac_dir=[0,0]
        self.world_state=0

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

    def update_action(self, new_action):
        if not self.action[new_action]:
            self.action[new_action] = True
            self.timer = 0

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect(self):
        self.rect.center = self.hitbox.center

    def reset_timer(self):
        self.frame = 0
        self.ac_dir[0]=self.dir[0]
        self.ac_dir[1]=self.dir[1]

class Enemy_1(Entity):

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
        self.friction=[0.2,1]

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

    friction=[0.2,0]
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 76
        self.max_health = 100
        #self.frame_timer={'run':40,'sword':18,'jump':21,'death':36,'dmg':20, 'stand':1}
        self.dmg=50
        #self.prioriy_list = ['death','hurt','sword','jump','run','stand']
        self.priority_action=['death','hurt','dash','sword','bow']#animation
        self.nonpriority_action=['jump','wall','fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'hurt':False,'bow':False,'dash':False,'wall':False,'fall':False,'inv':False,'talk':False}
        self.state = 'stand'
        self.equip='sword'#can change to bow
        self.f_action=['sword','bow']
        self.f_action_cooldown=True#True means you can use it
        self.hitbox_offset = 3
        self.sprites = Read_files.Sprites_player()

        #conversations with villigers
        self.letter_frame=1#to show one letter at the time: woudl ike to move this to NPC class instead
        self.text_frame=0#chosing which text to say: woudl ike to move this to NPC class instead


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
        self.friction[1] = 0
        self.velocity[1]=-11
        self.action['jump']=True
        if self.action['wall']:
            self.velocity[0]=-self.dir[0]*10

    def talk(self):
        self.action['talk']=True
        if self.state=='talk':#if finish talking, move on to the next text
            self.letter_frame=1#reset the letter frame
            self.text_frame+=1
            self.action['talk']=False
            self.state='stand'

        #if not self.action['talk']:
            #self.state=False

    def update(self,pos):
        super(Player, self).update(pos)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.center = [self.rect.center[0], self.rect.center[1] + self.hitbox_offset]

    def update_rect(self):
        self.rect.center = [self.hitbox.center[0], self.hitbox.center[1] - self.hitbox_offset]

class Block(Entity):

    def __init__(self,img,pos,chunk_key=False):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key

class BG_Block(Entity):

    def __init__(self,img,pos,chunk_key=False):
        super().__init__()
        self.image = img
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
    acceleration=[0.3,0.8]

    def __init__(self):
        super().__init__()
        self.action = {'stand':True,'run':False,'death':False,'hurt':False,'dash':False,'inv':False,'talk':False}
        self.nonpriority_action = ['run','stand']
        self.priority_action = ['death','hurt']
        self.health = 50
        self.state = 'stand'
        self.font=Read_files.Alphabet("Sprites/Alphabet/Alphabet.png",1)#intitilise the alphabet class
        self.friction=[0.2,0]

    def talk(self,game_screen,knight):
        self.action['run']=False
        self.action['stand']=True
        self.velocity=[0,0]
        self.action['talk']=True

        if knight.text_frame >= len(self.conversation.text[self.world_state]):
            knight.text_frame=0

        if knight.letter_frame//3!=len(self.conversation.text[self.world_state][knight.text_frame//1]):#if not everything has been said.
            text=self.conversation.text[self.world_state][knight.text_frame//1][:knight.letter_frame//3+1]
            knight.letter_frame+=1
            self.blit_conversation(text,game_screen)

        else:#if everything was said, print the whole text
            self.blit_conversation(self.conversation.text[self.world_state][knight.text_frame//1],game_screen)

    def blit_conversation(self,text,game_screen):#blitting of text from conversation
        game_screen.blit(self.text_surface,(100,100))#the text BG
        game_screen.blit(self.portrait,(200,100))#the portait
        self.font.render(game_screen,text,(100,100))#call the self made aplhabet blit

class NPC_1(NPC):
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png")
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load("Sprites/NPC/NPC_1/Woman1.png")
        self.text_surface=pygame.image.load("Sprites/aseprite/tile_sheets/House wall exterior 1.png")
        self.name = 'NPC_1'
        self.sprites = Read_files.NPC(self.name)
        self.conversation=Read_files.Conversations('Sprites/NPC/conversation.txt')#a dictionary with "world state" as keys

    def AI(self):
        self.action['run']=True
        if self.action['inv']:#collision with invisble block
            self.velocity[0] = -self.velocity[0]
            self.dir[0] = -self.dir[0]
            self.action['inv'] = False
