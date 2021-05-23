import pygame, Read_files, random, sys

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
        self.loot={'coin':1}
        self.shake=0

    def AI(self,knight):
        pass

    def attack_action(self,projectiles):
        return projectiles

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

    def loots(self,loot):
        for key in self.loot.keys():#go through all loot
            for i in range(0,self.loot[key]):#make that many object for that specific loot and add to gorup
                #obj=globals()[key]#make a class based on the name of the key: using global stuff
                obj=getattr(sys.modules[__name__], key)#make a class based on the name of the key: need to import sys
                #obj=eval(key)#make a class based on the name of the key: apperently not a good solution
                loot.add(obj(self.hitbox))
            self.loot[key]=0
        return loot

class Player(Entity):

    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 200
        self.max_health = 250
        self.priority_action=['death','hurt','dash','sword','bow']#animation
        self.nonpriority_action=['jump','wall','fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'jump':False,'death':False,'hurt':False,'bow':False,'dash':False,'wall':False,'fall':False,'inv':False,'talk':False}
        self.state = 'stand'
        self.equip='sword'#can change to bow
        self.hitbox_offset = 3
        self.sprites = Read_files.Sprites_player()
        self.interacting = False
        self.friction=[0.2,0]
        self.loot={'Coin':10,'Arrow':20}#the keys need to have the same name as their respective classes

    def attack_action(self,projectiles):
        if self.action[self.equip]:
            if self.state not in self.priority_action:#do not create an action if it has been created, until the animation is done
                if self.equip=='sword':
                    projectiles.add(Sword(self.dir,self.hitbox))
                elif self.equip=='bow' and self.loot['Arrow']>0:
                    projectiles.add(Bow(self.dir,self.hitbox))
                    self.loot['Arrow']-=1
        return projectiles

    def change_equipment(self):#don't change if there are arrows or sword already
        if self.equip == 'sword':
            self.equip='bow'
        else:
            self.equip='sword'

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
        self.action['talk']=not self.action['talk']

    def update(self,pos):
        super(Player, self).update(pos)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.center = [self.rect.center[0], self.rect.center[1] + self.hitbox_offset]

    def update_rect(self):
        self.rect.center = [self.hitbox.center[0], self.hitbox.center[1] - self.hitbox_offset]

class Enemy_1(Player):
    def __init__(self,pos,ID):
        super().__init__(pos)
        self.ID=ID
        self.health=10
        self.distance=[0,0]
        self.inv=False#flag to check if collision with invisible blocks
        self.friction=[0.2,1]
        self.sprites = Read_files.Sprites_evil_knight()
        self.shake=10#screen shake duration

    def AI(self,player):#the AI

        self.distance[0]=int((self.rect[0]-player.rect[0]))#follow the player
        self.distance[1]=int((self.rect[1]-player.rect[1]))#follow the player

        if abs(self.distance[0])>150 and abs(self.distance[1])>40 or player.action['death'] or self.action['hurt']:#don't do anything if far away, or player dead or while taking dmg
            self.action['run']=False
            self.action['stand']=True

        elif abs(self.distance[0])>500 or abs(self.distance[1])>500:#remove the enmy if far away
            self.kill()

        elif abs(self.distance[0]<150) and abs(self.distance[1])<40:

            self.dir[0]=-Enemy_1.sign(self.distance[0])
            self.action['run']=True
            self.action['stand']=False

            if abs(self.distance[0])<40:#don't get too close
                self.action['run']=False
                self.action['stand']=True

        if abs(self.distance[0])<80 and abs(self.distance[1])<40 and not player.action['death']:#swing sword when close
            self.action[self.equip] = True

    @staticmethod
    def sign(x):
        if x>0: return 1
        return -1

class Enemy_2(Entity):
    def __init__(self,pos,ID):
        super().__init__()
        self.ID=ID
        self.image = pygame.image.load("Sprites/enemies/flowy/stand/Stand1.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.priority_action=['death','hurt','sword','bow','trans']#animation
        self.nonpriority_action=['fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'death':False,'hurt':False,'bow':False,'fall':False,'trans':False}
        self.state = 'stand'
        self.equip='sword'
        self.sprites = Read_files.Flowy()
        self.friction=[0.2,0]
        self.loot={'Coin':10,'Arrow':2}#the keys need to have the same name as their respective classes
        self.distance=[0,0]
        self.shake=3

    @staticmethod#a function to add glow around the entity
    def add_white(radius,colour,screen,pos):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(pos[0]-radius,pos[1]-radius),special_flags=pygame.BLEND_RGB_ADD)

    def AI(self,player,screen):#the AI
        #light around the entity
        radius=max(20-abs(self.distance[0])//10,1)
        Enemy_2.add_white(radius,(20,0,0),screen,self.rect.center)#radius, clolor, screen,position

        self.distance[0]=int((self.rect[0]-player.rect[0]))#follow the player
        self.distance[1]=int((self.rect[1]-player.rect[1]))#follow the player

        if 30 < abs(self.distance[0])<80 and abs(self.distance[1])<100 and not player.action['death']:#swing sword when close
            self.action['trans'] = True

        elif abs(self.distance[0])<30 and abs(self.distance[1])<100 and not player.action['death']:#swing sword when close
            self.action[self.equip] = True

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

class Interactable(Entity):

    def __init__(self):
        super().__init__()
        self.interacted = False

class Door(Interactable):

    def __init__(self,img,pos,chunk_key=False):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key

class Chest(Interactable):
    def __init__(self,pos):
        super().__init__()
        self.image_sheet = Read_files.Chest().get_sprites()
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-5)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 8:
                self.image = self.image_sheet[1]
                self.timer += 1
            else:
                self.image = self.image_sheet[2]
                self.interacted = False

class Chest_Big(Interactable):
    def __init__(self,pos):
        super().__init__()
        self.image_sheet = Read_files.Chest_Big().get_sprites()
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-13)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 28:
                self.image = self.image_sheet[self.timer//7]
                self.timer += 1
            else:
                self.image = self.image_sheet[4]
                self.interacted = False

class NPC(Entity):
    acceleration=[0.3,0.8]

    def __init__(self):
        super().__init__()
        self.action = {'stand':True,'run':False,'death':False,'hurt':False,'dash':False,'inv':False,'talk':False}
        self.nonpriority_action = ['run','stand']
        self.priority_action = ['death','hurt']
        self.health = 50
        self.state = 'stand'
        self.font=Read_files.Alphabet("Sprites/aseprite/Alphabet/Alphabet.png")#intitilise the alphabet class
        self.page_frame=0#if there are pages of text
        self.text_frame=-1#chosing which text to say: woudl ike to move this to NPC class instead
        self.letter_frame=1#to show one letter at the time: woudl ike to move this to NPC class instead
        self.conv_idx=0

    def blit_conversation(self,text,game_screen):#blitting of text from conversation
        self.text_surface.blit(self.portrait,(550,100))#the portait on to the text_surface
        game_screen.blit(self.text_surface,(200,200))#the text BG
        self.font.render(game_screen,text,(400,300),1)#call the self made aplhabet blit and blit the conversation
        self.font.render(game_screen,self.name,(750,400),1)#blit the name

    def new_page(self):
        if '&' in self.conversation.text[self.world_state][self.text_frame//1]:#& means there is a new page
            conversation=self.conversation.text[self.world_state][self.text_frame//1]
            indices = [i for i, x in enumerate(conversation) if x == "&"]#all indexes for &
            self.number_of_pages=len(indices)

            for i in range(self.page_frame,self.number_of_pages+1):
                start=min(indices[self.page_frame-1],self.page_frame*10000)
                if self.page_frame>=self.number_of_pages:
                    end=-1
                else:
                    end=indices[self.page_frame]
            return self.conversation.text[self.world_state][self.text_frame//1][start:end]
        else:
            self.number_of_pages=0
            return self.conversation.text[self.world_state][self.text_frame//1]

    def talking(self):
        self.action['talk']=True
        self.action['run']=False
        self.action['stand']=True
        self.velocity=[0,0]

    def talk(self,game_screen,player):
        if not self.action['talk']:#if first time
            self.page_frame=0
            self.letter_frame=1#reset the letter frame
            self.text_frame+=1

        if self.text_frame >= len(self.conversation.text[self.world_state]):
            self.text_frame=0#reset the conversation tree

        self.talking()#settign flags
        conv=self.new_page()#preparing the conversation if new page exits
        self.blit_conv_action(game_screen)

        if self.letter_frame//3!=len(conv):#if not everything has been said.
            text=conv[:self.letter_frame//3+1]
            self.letter_frame+=1
            self.blit_conversation(text,game_screen)
        else:#if everything was said, print the whole text
            self.page_frame=min(self.number_of_pages,self.page_frame)
            self.blit_conversation(conv,game_screen)

        self.input_quit(player)

    def input_quit(self,player):#to exits between option menues
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                #for action conversations
                if event.key == pygame.K_UP:#up
                    self.conv_idx-=1*int(not self.business)
                    self.ammount+=1*int(self.business)
                    self.ammount=min(player.loot['Coin'],self.ammount)

                if event.key == pygame.K_DOWN:#up
                    self.conv_idx+=1*int(not self.business)
                    self.ammount-=1*int(self.business)
                    self.ammount=max(0,self.ammount)

                if event.key == pygame.K_RETURN:#enter the option
                    self.business = not self.business

                #exit/skip conversation
                if event.key == pygame.K_t:
                    if self.page_frame<self.number_of_pages:
                        self.page_frame+=1#next page
                    else:
                        self.action['talk']=False
                        player.action['talk']=False
                        self.page_frame=0#reset page
                    self.letter_frame=1#reset the letter frame

    def business(self):
        pass

    def blit_conv_action(self,game_screen):
        pass

class NPC_1(NPC):
    def __init__(self,pos):
        super().__init__()
        self.name = 'NPC_1'
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load('Sprites/NPC/'+self.name+ '/Woman1.png').convert_alpha()
        self.text_surface=pygame.image.load("Sprites/aseprite/conversation/Conv_BG.png").convert_alpha()
        self.sprites = Read_files.NPC(self.name)
        self.conversation=Read_files.Conversations('Sprites/NPC/'+self.name+ '/conversation.txt')#a dictionary of conversations with "world state" as keys
        self.friction=[0.2,0]

    def AI(self):
        self.action['run']=True

        if abs(self.rect[0]+self.rect[1])>800:#if far away
            self.kill()
        elif self.action['inv']:#collision with invisble block
            self.velocity[0] = -self.velocity[0]
            self.dir[0] = -self.dir[0]
            self.action['inv'] = False

class MrBanks(NPC):
    def __init__(self,pos):
        super().__init__()
        self.name = 'MrBanks'
        self.image = pygame.image.load("Sprites/player/run/HeroKnight_run_0.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load('Sprites/NPC/'+self.name+ '/Woman1.png').convert_alpha()
        self.text_surface=pygame.image.load("Sprites/aseprite/conversation/Conv_BG.png").convert_alpha()
        self.sprites = Read_files.NPC(self.name)
        self.conversation=Read_files.Conversations('Sprites/NPC/'+self.name+ '/conversation.txt')#a dictionary of conversations with "world state" as keys
        self.friction=[0.2,0]
        self.conv_action=['deposit','withdraw']
        self.conv_action_BG=pygame.image.load("Sprites/aseprite/conversation/Conv_action_BG.png").convert_alpha()
        self.conv_possition=[300]
        self.conv_idx=0
        self.loot={'Coin':0}#the keys need to have the same name as their respective classes
        self.business=False
        self.ammount=0

    def AI(self):
        if abs(self.rect[0]+self.rect[1])>800:#if far away
            self.kill()

    def blit_conv_action(self,game_screen):
        game_screen.blit(self.conv_action_BG,(850,200))#the text BG

        if self.conv_idx<=0:
            self.conv_idx=0
        elif self.conv_idx>=len(self.conv_action):
            self.conv_idx=len(self.conv_action)-1

        self.font.render(game_screen,'o',(930,self.conv_possition[self.conv_idx]),1)#call the self made aplhabet blit and blit the conversation
        self.conv_possition=[]

        scale=[1]*len(self.conv_action)
        scale[self.conv_idx]=2
        i=1

        for conv in self.conv_action:
            self.font.render(game_screen,conv,(950,250+50*i),scale[i-1])#call the self made aplhabet blit and blit the conversation
            self.conv_possition.append(250+50*i)
            i+=1

        if self.business:
            game_screen.blit(self.conv_action_BG,(850,200))#the text BG
            self.font.render(game_screen,str(self.ammount),(930,250),1)#call the self made aplhabet blit and blit the conversation


class Weapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hit=False

    def update(self,scroll,entity_ac_dir,entity_hitbox):
        #remove the equipment if it has expiered
        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

class Sword(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()
        self.lifetime=10
        self.dmg=10
        self.velocity=[0,0]
        self.type='sword'
        self.image = pygame.image.load("Sprites/aseprite/Items/sword.png").convert_alpha()

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

        self.spawn(entity_dir,entity_hitbox)#spawn hitbox based on entity position and direction

    def update(self,scroll,entity_ac_dir=[0,0],entity_hitbox=0):
        #remove the equipment if it has expiered
        self.lifetime-=1
        self.spawn(entity_ac_dir,entity_hitbox)

    def spawn(self,entity_dir,entity_hitbox):
        if entity_dir[1] > 0:#up
            self.hitbox=pygame.Rect(entity_hitbox.midtop[0]-10,entity_hitbox.midtop[1]-20,20,20)
        elif entity_dir[1] < 0:#down
            self.hitbox=pygame.Rect(entity_hitbox.midtop[0]-10,entity_hitbox.midtop[1]+40,20,20)
        elif entity_dir[0] > 0 and entity_dir[1] == 0:#right
            self.hitbox=pygame.Rect(entity_hitbox.midright[0],entity_hitbox.midright[1]-20,40,30)
        elif entity_dir[0] < 0 and entity_dir[1] == 0:#left
            self.hitbox=pygame.Rect(entity_hitbox.midleft[0]-40,entity_hitbox.midleft[1]-20,40,30)

class Bow(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()
        self.velocity=[entity_dir[0]*10,-5]
        self.lifetime=40
        self.dmg=10
        self.type='bow'
        self.image = pygame.image.load("Sprites/aseprite/Items/arrow.png").convert_alpha()
        if self.velocity[0]<0:#if shoting left
            self.image=pygame.transform.flip(self.image,True,False)

        self.original_image=self.image.copy()

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def update(self,scroll,entity_ac_dir=[0,0],entity_hitbox=[0,0]):
        #remove the equipment if it has expiered
        self.speed()
        self.rotate()

        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

    def speed(self):#gravity
        self.velocity[1]+=0.5

    def rotate(self):
        self.image=pygame.transform.rotate(self.original_image,-self.velocity[0]*self.velocity[1])#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

class Loot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        choice=[-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,2,4,6,8,10,12,14,16,18,20]#just not 0
        self.pos=[random.choice(choice),random.choice(choice)]
        self.lifetime=200
        self.movement=[0,0]#for platfform collisions
        dir=self.pos[0]/abs(self.pos[0])#horizontal direction
        self.velocity=[dir*random.randint(0, 3),-11]

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect(self):
        self.rect.center = self.hitbox.center

    def update(self,scroll):
        #remove the equipment if it has expiered
        self.speed()

        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        if self.lifetime<0:#remove after a while
            self.kill()

    def speed(self):
        self.velocity[1]+=0.9#gravity

        self.velocity[1]=min(self.velocity[1],7)#set a y max speed
        self.movement[1]=self.velocity[1]#set the vertical velocity

class Coin(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/aseprite/Items/coin.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

class Arrow(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/aseprite/Items/arrow.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
