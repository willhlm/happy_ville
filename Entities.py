import pygame, random, sys, Read_files, states_player, states_NPC, states_enemy

class ExtendedGroup(pygame.sprite.Group):#adds a white glow around enteties
    def __init__(self):
        super().__init__()

    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            ExtendedGroup.add_colour(20,(20,20,20),surface,spr.rect)#addded this
        self.lostsprites = []

    @staticmethod
    def add_colour(radius,colour,screen,rect):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(rect.x,rect.y),special_flags=pygame.BLEND_RGB_ADD)

class Platform(pygame.sprite.Sprite):#has hitbox
    def __init__(self,pos,chunk_key=False):
        super().__init__()
        self.rect = pygame.Rect(pos,(16,16))
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key
        self.spike=False

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Invisible_block(Platform):
    def __init__(self,pos,chunk_key=False):
        super().__init__(pos,chunk_key=False)

class Collision_block(Platform):
    def __init__(self,pos,chunk_key=False):
        super().__init__(pos,chunk_key=False)

class Spikes(Platform):
    def __init__(self,pos,chunk_key=False):
        super().__init__(pos,chunk_key=False)
        self.image=pygame.image.load("Sprites/level_sheets/Spkies.png").convert_alpha()
        self.spike=True

class Staticentity(pygame.sprite.Sprite):#no hitbox but image
    def __init__(self,pos,img=pygame.Surface((16,16))):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self,pos):
        self.update_pos(pos)

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]

class BG_Block(Staticentity):
    def __init__(self,pos,img,paralex=1):
        super().__init__(pos,img)
        self.true_pos = self.rect.topleft
        self.paralex=paralex

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + self.paralex*pos[0], self.rect.topleft[1] + self.paralex*pos[1]]
        self.true_pos= [self.true_pos[0] + self.paralex*pos[0], self.true_pos[1] + self.paralex*pos[1]]
        self.rect.topleft = self.true_pos

class Dynamicentity(Staticentity):
    def __init__(self,pos):
        super().__init__(pos)
        self.dir = [1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]

    def update(self,pos):
        self.update_pos(pos)
        self.currentstate.update()
        self.currentstate.update_animation()#has to be here

class Character(Dynamicentity):#enemy, NPC,player
    def __init__(self,pos):
        super().__init__(pos)
        self.acceleration=[1,0.8]
        self.velocity=[0,0]
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.collision_spikes = {'top':False,'bottom':False,'right':False,'left':False}
        self.max_vel = 10
        self.hitbox_offset = (0,0)
        self.friction=[0.2,0]

    def update_pos(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.bottom=self.rect.bottom

    def take_dmg(self,dmg):
        if dmg>0:
            self.health-=dmg
            if self.health>0:#check if dead¨
                self.currentstate.change_state('Hurt')
            else:
                self.currentstate.change_state('Death')

    def check_collisions(self):
        if self.collision_types['top']:#knock back when hit head
            self.velocity[1]=0
        elif self.collision_spikes['bottom']:
            self.velocity[1]=-6#knock back
            self.take_dmg(10)
        elif self.collision_spikes['right']:
            self.velocity[0]=-6#knock back
            self.take_dmg(10)
        elif self.collision_spikes['left']:
            self.velocity[0]=6#knock back
            self.take_dmg(10)
        elif self.collision_spikes['top']:
            self.velocity[1]=6#knock back
            self.take_dmg(10)

    def update(self,pos):
        super().update(pos)
        self.check_collisions()

    def update_hitbox(self):
        self.hitbox.center = [self.rect.center[0] + self.hitbox_offset[0], self.rect.center[1] + self.hitbox_offset[1]]

    def update_rect(self):
        self.rect.center = [self.hitbox.center[0] - self.hitbox_offset[0], self.hitbox.center[1] - self.hitbox_offset[1]]

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.center = self.rect.center

class Enemy(Character):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos)
        self.projectiles = projectile_group
        self.loot_group = loot_group
        self.currentstate = states_enemy.Idle(self)
        self.inventory = {'Amber_Droplet':random.randint(0, 10)}#random.randint(0, 10)

    def update(self,pos,playerpos):
        super().update(pos)
        self.AI(playerpos)

    def draw(self,screen):#could be added to group draw somehow?
        self.add_colour(20,(20,20,20),screen)#radius, clolor, screen

    #a function to add glow around the entity
    def add_colour(self,radius,colour,screen):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(self.rect.x,self.rect.y),special_flags=pygame.BLEND_RGB_ADD)

    def loots(self):
        for key in self.inventory.keys():#go through all loot
            for i in range(0,self.inventory[key]):#make that many object for that specific loot and add to gorup
                obj=getattr(sys.modules[__name__], key)(self)#make a class based on the name of the key: need to import sys
                self.loot_group.add(obj)
            self.inventory[key]=0

    def knock_back(self):
        self.velocity[0]=-50*self.dir[0]
        self.stun(30)

    def stun(self,duration):
        self.currentstate = states_enemy.Stun(self,duration)

class Woopie(Enemy):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos,projectile_group,loot_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/woopie/main/Idle/Kodama_stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1
        self.spirit=100
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.shake=10
        self.counter=0
        #self.max_vel = 1
        self.friction=[0.5,0]

    def AI(self,playerpos):#the AI based on playerpos
        self.counter += 1
        if self.counter>100:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.currentstate.change_state('Idle')
            else:
                self.currentstate.change_state('Walk')

class Vatt(Enemy):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos,projectile_group,loot_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/woopie/main/Idle/Kodama_stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1
        self.spirit=100
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/woopie/')#Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.shake=10
        self.counter=0
        #self.max_vel = 1
        self.friction=[0.5,0]

    def AI(self,playerpos):#the AI based on playerpos
        self.counter += 1
        if self.counter>100:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.currentstate.change_state('Idle')
            else:
                self.currentstate.change_state('Walk')

class Flowy(Enemy):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos,projectile_group,loot_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/flowy/main/Idle/Stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/flowy/')
        self.distance=[0,0]
        self.shake=self.hitbox.height/10
        self.spirit=10

    def AI(self,playerpos):#the AI
        self.distance[0]=int((self.rect.x-playerpos.x))
        self.distance[1]=int((self.rect.y-playerpos.y))

        if 100 < abs(self.distance[0])<200 and abs(self.distance[1])<100:
            pass
        elif abs(self.distance[0])<100 and abs(self.distance[1])<100:#swing sword when close
            pass#self.currentstate.enter_state('Trans')

class Larv(Enemy):
    def __init__(self,pos,projectile_group,loot_group):
        super().__init__(pos,projectile_group,loot_group)
        self.image = pygame.image.load("Sprites/Enteties/enemies/flowy/main/Idle/Stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=self.rect.copy()
        #self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/enemies/larv/')
        self.distance=[0,0]
        self.shake=self.hitbox.height/10
        self.spirit=10
        self.counter=0
        self.friction=[0.5,0]

    def AI(self,playerpos):#the AI
        self.counter += 1
        if self.counter>100:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.currentstate.change_state('Idle')
            else:
                self.currentstate.change_state('Walk')

class Player(Character):
    def __init__(self,pos,projectile_group,cosmetics_group):
        super().__init__(pos)
        self.image = pygame.image.load("Sprites/Enteties/aila/main/Idle/aila_idle1.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,35)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/aila/',True)
        self.max_health = 250
        self.max_spirit = 100
        self.health = 100
        self.spirit = 100

        self.cosmetics = cosmetics_group

        self.projectiles = projectile_group#pygame.sprite.Group()
        self.abilities={'Hammer':Hammer,'Force':Force,'Arrow':Arrow,'Heal':Heal,'Darksaber':Darksaber}#'Shield':Shield#the objects are referensed but made in states
        self.equip='Hammer'#ability pointer
        self.sword=Sword(self)
        self.shield=Shield(self)

        self.action_sfx_player = pygame.mixer.Channel(1)
        self.action_sfx_player.set_volume(0.1)
        self.action_sfx = {'run': pygame.mixer.Sound("Audio/SFX/player/footstep.mp3")}
        self.movement_sfx_timer = 110
        self.hitbox_offset = (0,13)

        self.inventory={'Amber_Droplet':10}#the keys need to have the same name as their respective classes
        self.shake = 0

        self.currentstate = states_player.Idle(self)

    def load_sfx(self):
        if self.action['run'] and not self.action['fall'] and self.movement_sfx_timer > 15:
            self.action_sfx_player.play(self.action_sfx['run'])
            self.movement_sfx_timer = 0
        self.movement_sfx_timer += 1

    def update(self,pos):
        super().update(pos)
        #self.load_sfx()xxx

class NPC(Character):
    def __init__(self,pos):
        super().__init__(pos)
        self.name = '<always define name>'
        self.health = 50
        self.conv_index = 0
        self.currentstate = states_NPC.Idle(self)
        self.friction=[0.5,0]

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

    def update(self, pos):
        super().update(pos)
        self.AI()

    def idle(self):
        self.currentstate = states_NPC.Idle(self)

    def walk(self):
        self.currentstate = states_NPC.Walk(self)

class Aslat(NPC):
    def __init__(self, pos):
        super().__init__(pos)
        self.name = 'Aslat'
        self.sprites = Read_files.Sprites_Player("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.image = self.sprites.get_image('Idle', 0, self.dir, 'main')
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/MrBanks/Woman1.png').convert_alpha()  #temp
        self.load_conversation()
        #self.max_vel = 1.5
        self.counter=0

    def AI(self):
        self.counter+=1
        if self.counter>100:
            self.counter=0
            rand=random.randint(0,1)
            if rand==0:
                self.idle()
            else:
                self.walk()
#        if self.action['inv']:#collision with invisble block
#            self.velocity[0] = -self.velocity[0]
#            self.dir[0] = -self.dir[0]
#            self.action['inv'] = False

class MrBanks(NPC):
    def __init__(self,pos,img=pygame.Surface((16,16))):
        super().__init__(pos,img=pygame.Surface((16,16)))
        self.name = 'MrBanks'
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],20,48)
        self.rect.center = self.hitbox.center#match the positions of hitboxes
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/'+self.name+ '/Woman1.png').convert_alpha()
        self.text_surface=pygame.image.load("Sprites/Enteties/NPC/conv/Conv_BG.png").convert_alpha()
        self.sprites = Read_files.Sprites_enteties("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.conversation=Read_files.Conversations('Sprites/Enteties/NPC/'+self.name+ '/conversation.txt')#a dictionary of conversations with "world state" as keys
        self.conv_action=['deposit','withdraw']
        self.conv_action_BG=pygame.image.load("Sprites/Enteties/NPC/conv/Conv_action_BG.png").convert_alpha()
        self.conv_possition=[[400],[300]]

        self.loot={'Coin':2}#the keys need to have the same name as their respective classes
        self.business=False
        self.ammount=0


    def AI(self):
        if abs(self.rect[0])>500 or abs(self.rect[1])>500:#if far away
            self.stay_still()
        else:
            self.move_again()



    def blit_conv_action(self,game_screen):
        game_screen.blit(self.conv_action_BG,(850,200))#the text BG

        if not self.business:#if not busness

            if self.conv_idx[1]<=0:
                self.conv_idx[1]=0
            elif self.conv_idx[1]>=len(self.conv_action):
                self.conv_idx[1]=len(self.conv_action)-1

            self.font.render(game_screen,'o',(930,self.conv_possition[1][self.conv_idx[1]]),1)#call the self made aplhabet blit and blit the conversation
            self.conv_possition=[[],[]]

            scale=[1]*len(self.conv_action)
            scale[self.conv_idx[1]]=2
            i=1

            for conv in self.conv_action:
                self.font.render(game_screen,conv,(950,250+50*i),scale[i-1])#call the self made aplhabet blit and blit the conversation
                self.conv_possition[1].append(250+50*i)
                i+=1
        else:#if buisness
            game_screen.blit(self.conv_action_BG,(850,200))#the text BG
            self.font.render(game_screen,str(self.ammount)+' coins?',(940,300),1)#call the self made aplhabet blit and blit the conversation
            self.font.render(game_screen,self.conv_action[self.conv_idx[1]]+'?',(930,270),1)#call the self made aplhabet blit and blit the conversation

            self.conv_possition[0]=[920,1020]

            if self.conv_idx[0]<=0:
                self.conv_idx[0]=0
            elif self.conv_idx[0]>=2:
                self.conv_idx[0]=1
            scale=[1,1]#yes or no
            scale[self.conv_idx[0]]=2

            self.font.render(game_screen,'Yes',(940,400),scale[0])#call the self made aplhabet blit and blit the conversation
            self.font.render(game_screen,'No',(1040,400),scale[1])#call the self made aplhabet blit and blit the conversation
            self.font.render(game_screen,'o',(self.conv_possition[0][self.conv_idx[0]],400),1)#call the self made aplhabet blit and blit the conversation

    def trade(self,player):#exchane of money
        if self.conv_idx[0]==0:#if press yes
            if self.conv_action[self.conv_idx[1]] == 'deposit':
                player.loot['Coin']-=self.ammount
                self.loot['Coin']+=self.ammount
            elif self.conv_action[self.conv_idx[1]] == 'withdraw':
                player.loot['Coin']+=self.ammount
                self.loot['Coin']-=self.ammount
        else:#if press no
            self.buisness=False
            self.ammount=0

    def upinteger(self,player):
        self.ammount+=1*int(self.business)
        if self.conv_action[self.conv_idx[1]] == 'deposit':
            self.ammount=min(player.loot['Coin'],self.ammount)
        elif self.conv_action[self.conv_idx[1]] == 'withdraw':
            self.ammount=min(self.loot['Coin'],self.ammount)

    def downinteger(self,player):
        self.ammount-=1*int(self.business)
        self.ammount=max(0,self.ammount)#minimum 0

class Trigger(pygame.sprite.Sprite):

    def __init__(self,pos):
        super().__init__()
        self.rect = pygame.Rect(pos, (16,16))
        self.hitbox = self.rect.inflate(0,0)

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Path_Col_v(Trigger):


    def __init__(self,pos,destination):
        super().__init__(pos)
        ext = 32
        self.rect = pygame.Rect((pos[0],pos[1]-ext), (16,16+(2*ext)))
        self.hitbox = self.rect.inflate(0,0)
        self.next_map = destination
        self.image = pygame.Surface((16,16+(2*ext)))
        self.image.fill((0,0,0))

class Path_Col_h(Trigger):

    def __init__(self,pos,destination):
        super().__init__(pos)
        ext = 32
        self.rect = pygame.Rect((pos[0]-ext,pos[1]), (16+(2*ext),16))
        self.hitbox = self.rect.inflate(0,0)
        self.next_map = destination
        self.image = pygame.Surface((16+(2*ext),16))
        self.image.fill((0,0,0))

class Camera_Stop(pygame.sprite.Sprite):

    def __init__(self,pos,dir):
        super().__init__()
        self.rect=pygame.Rect((pos),(16,16))
        self.hitbox = self.rect.inflate(0,0)
        self.dir = dir
        self.image = pygame.Surface((16,16))
        self.image.fill((0,0,0))

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Interactable(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.interacted = False

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

class Pathway(Interactable):

    def __init__(self, destination):
        super().__init__()
        self.next_map = destination

class Door(Pathway):

    def __init__(self,pos,destination):
        super().__init__(destination)
        self.image_sheet = Read_files.Sprites().generic_sheet_reader("Sprites/animations/Door/door.png",32,48,1,4)
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 21:
                self.image = self.image_sheet[self.timer//7]
                self.timer += 1
            else:
                self.image = self.image_sheet[3]

class Chest(Interactable):
    def __init__(self,pos,id,loot,state):
        super().__init__()
        self.image_sheet = Read_files.Sprites().generic_sheet_reader("Sprites/animations/Chest/chest.png",16,21,1,3)
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-5)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0
        self.ID = id
        self.loot = {loot:1}
        if state == "opened":
            self.opened()

    def opened(self):
        self.image = self.image_sheet[2]
        self.timer = 9
        self.interacted = True

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 8:
                self.image = self.image_sheet[1]
                self.timer += 1
            else:
                self.image = self.image_sheet[2]

class Chest_Big(Interactable):
    def __init__(self,pos,id,loot,state):
        super().__init__()
        self.image_sheet = Read_files.Sprites().generic_sheet_reader("Sprites/animations/Chest/chest_big.png",32,29,1,5)
        self.image = self.image_sheet[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos[0],pos[1]-13)
        self.hitbox = self.rect.inflate(0,0)
        self.timer = 0
        self.ID = id
        self.loot = loot
        if state == "opened":
            self.opened()

    def opened(self):
        self.image = self.image_sheet[4]
        self.timer = 29
        self.interacted = True

    def update(self,pos):
        super().update(pos)
        if self.interacted:
            if self.timer < 28:
                self.image = self.image_sheet[self.timer//7]
                self.timer += 1
            else:
                self.image = self.image_sheet[4]
                self.interacted = False

class Abilities(pygame.sprite.Sprite):
    def __init__(self,entity):
        super().__init__()
        self.entity=entity
        self.frame=0
        self.phase='main'
        self.phases=['main']
        self.action=''
        self.frame_rate=4

    def update(self,pos):
        self.lifetime-=1
        self.update_pos(pos)
        self.update_animation()
        self.destroy()

    def update_animation(self):
        self.image = self.sprites.get_image(self.action,self.frame//self.frame_rate,self.dir,self.phase)
        self.frame += 1

        if self.frame == self.sprites.get_frame_number(self.action,self.dir,self.phase)*self.frame_rate:
            self.reset_timer()
            self.increase_phase()

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='main'
        elif self.phase=='main':
            pass
        elif self.phase=='post':
            self.kill()

    def reset_timer(self):
        self.frame = 0

    def destroy(self):
        if self.lifetime<0:
            self.kill()

    def collision_ene(self,collision_ene):
        self.kill()

    def collision_plat(self):
        pass

    def countered(self):
        self.entity.stun(30)
        self.kill()

class Heal(Abilities):
    def __init__(self,entity):
        super().__init__(entity)

class Projectiles(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.dir=self.entity.dir.copy()
        self.rectangle()
        self.update_hitbox()

    def rectangle(self):
        self.image = self.sprites.sprite_dict['main'][self.action][0]
        self.rect = self.image.get_rect()
        self.hitbox=self.rect.copy()

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

    def update_hitbox(self):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
            self.velocity=[0,-10]
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
            self.velocity=[0,10]
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
            self.velocity=[10,0]
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
            self.velocity=[-10,0]
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def knock_back(self):
        self.velocity[0]=-self.velocity[0]
        self.velocity[1]=-self.velocity[1]

    def countered(self):
        super().countered()
        self.knock_back()

class Melee(Abilities):
    def __init__(self,entity):
        super().__init__(entity)
        self.rectangle()

    def rectangle(self):
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,50,50)
        self.hitbox = self.rect.copy()

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]
        self.hitbox.center = self.rect.center

    def update_hitbox(self):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

class Sword(Melee):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Sword/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=10

    def update(self,pos):
        super().update(pos)
        self.update_hitbox()

    def collision_ene(self,collision_ene):
        slash=Slash(self)
        self.entity.cosmetics.add(slash)
        self.kill()

class Darksaber(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=0
        self.lifetime=10#swrod hitbox duration

    def collision_ene(self,collision_ene):
        if collision_ene.spirit>=10:
            collision_ene.spirit-=10
            spirits=Spiritsorb(collision_ene)
            collision_ene.loot_group.add(spirits)
        self.kill()

class Hammer(Sword):
    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=10#swrod hitbox duration

class Shield(Melee):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Shield/')

    def __init__(self,entity):
        super().__init__(entity)
        self.dmg=0

    def update(self,pos):
        super().update(pos)
        self.update_hitbox()

    def collision_ene(self,collision_ene):
        collision_ene.knock_back()
        self.kill()

class Stone(Abilities):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Stone/',True)

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=100
        self.dmg=10
        self.charge_velocity=0
        self.action='small'
        self.initiate()
        self.hitbox=pygame.Rect(self.rect.x,self.rect.y,10,10)

    def update_hitbox(self):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=self.entity.hitbox.midtop
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=self.entity.hitbox.midbottom
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=self.entity.hitbox.midright
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=self.entity.hitbox.midleft
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def update(self,pos):
        self.update_pos(pos)
        self.update_animation()#has to be here
        self.speed()#set the speed
        self.destroy()

    def increase_phase(self):
        if self.phase=='pre':
            self.phase='charge'
        elif self.phase=='main':
            pass
        elif self.phase=='post':
            self.kill()

    def speed(self):
        if self.phase=='charge':#charging
            self.charge_velocity=self.charge_velocity+0.5*self.dir[0]
            self.charge_velocity=self.dir[0]*min(20,self.dir[0]*self.charge_velocity)#set max velocity

            if abs(self.charge_velocity)>=20:#increase the ball size when max velocity is reached
                self.action='medium'
                self.shake=2#add shake effect if the ball is big

        elif self.phase=='main':#main pahse
            self.lifetime-=1#affect only the lifetime in main state
            if self.action=='small':#only have gravity if small
                self.velocity[1]+=0.1#graivity

    def collision_ene(self,collision_ene):
        self.velocity=[0,0]
        self.dmg=0
        self.phase='post'

    def collision_plat(self):
        self.velocity=[0,0]
        self.dmg=0
        self.phase='post'

    def rotate(self):
        angle=self.dir[0]*max(-self.dir[0]*self.velocity[0]*self.velocity[1],-60)

        self.image=pygame.transform.rotate(self.original_image,angle)#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

    def knock_back(self):
        self.velocity[0]=-self.velocity[0]
        self.velocity[1]=-self.velocity[1]

    def countered(self):
        super().countered()
        self.knock_back()

class Force(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Force/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=30
        self.dmg=0
        self.phase='pre'
        self.phases=['pre','main','post']

    def collision_plat(self):
        self.phase='post'
        self.frame=0
        self.velocity=[0,0]

    def collision_ene(self,collision_ene):#if hit something
        self.phase='post'
        self.frame=0
        self.velocity=[0,0]

        collision_ene.velocity[0]=self.dir[0]*10#abs(push_strength[0])
        collision_ene.velocity[1]=-6

class Arrow(Projectiles):
    sprites = Read_files.Sprites_Player('Sprites/Attack/Arrow/')

    def __init__(self,entity):
        super().__init__(entity)
        self.lifetime=100
        self.dmg=10

    def collision_ene(self,collision_ene):
        self.velocity=[0,0]
        self.dmg=0
        self.kill()

    def collision_plat(self):
        self.velocity=[0,0]
        self.dmg=0

class Loot(pygame.sprite.Sprite):
    def __init__(self,entity):
        super().__init__()
        self.entity=entity
        self.lifetime=500
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.collision_spikes = {'top':False,'bottom':False,'right':False,'left':False}
        self.frame = 0

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect(self):
        self.rect.center = self.hitbox.center

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]
        self.hitbox.center = self.rect.center

    def destory(self):
        if self.lifetime<0:#remove after a while
            self.kill()

    def update(self,scroll):
        self.lifetime-=1
        self.update_pos(scroll)
        self.update_vel()
        self.update_animation()
        self.destory()

    def update_animation(self, frame_rate = 0.25):
        self.image = self.sprites['idle'][int(self.frame)]
        if self.frame == len(self.sprites['idle'])-1:
            self.frame = 0
        self.frame += frame_rate

class Amber_Droplet(Loot):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/amber_droplet/')

    def __init__(self,entity):
        super().__init__(entity)
        self.velocity=[random.randint(-3, 3),-4]
        self.rectangle()

    def rectangle(self):#rectangle
        self.rect = pygame.Rect(self.entity.rect.x,self.entity.rect.y,5,5)
        self.hitbox = self.rect.copy()

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
        super().update(pos)

    def pickup(self,player):
        obj=(self.__class__.__name__)#get the loot in question
        player.inventory[obj]+=1
        self.kill()

class Spiritsorb(Loot):
    sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/spiritorbs/')

    def __init__(self,entity):
        super().__init__(entity)
        self.pos=[random.randint(-10, 10),random.randint(-10, 10)]
        self.rectangle()
        self.image = self.sprites['idle'][int(self.frame)]

    def rectangle(self):#rectangle
        self.rect = pygame.Rect(self.entity.hitbox.x+self.pos[0],self.entity.hitbox.y+self.pos[1],5,5)
        self.hitbox=self.rect.copy()

    def update_vel(self):
        self.velocity=[0.1*random.randint(-10, 10),0.1*random.randint(-10, 10)]

    def pickup(self,player):
        player.spirit += 10
        self.kill()

class Cosmetics(pygame.sprite.Sprite):
    def __init__(self,entity):
        super().__init__()
        self.entity=entity
        self.frame=0

    def update(self,scroll):
        self.lifetime-=1
        self.update_pos(scroll)
        self.destroy()

    def update_pos(self,scroll):
        self.rect.topleft = [self.rect.topleft[0] + scroll[0], self.rect.topleft[1] + scroll[1]]

    def destroy(self):
        if self.lifetime<0:
            self.kill()

class Slash(Cosmetics):
    def __init__(self,entity):
        super().__init__(entity)
        self.image = pygame.image.load("Sprites/animations/Spirits/Spirits1.png").convert_alpha()
        self.rect = self.image.get_rect(center=self.entity.hitbox.center)
        self.lifetime=10

class Spirits(Cosmetics):
    def __init__(self,entity):
        super().__init__(entity)
        self.image = pygame.image.load("Sprites/animations/Spirits/Spirits1.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.lifetime=10

class Menu_Arrow():

    def __init__(self):
        self.img = pygame.image.load("Sprites/utils/arrow.png")
        self.rect = self.img.get_rect()

    #note: sets pos to input, doesn't update with an increment of pos like other entities
    def update(self,pos):
        self.rect.topleft = pos

    def draw(self,screen):
        screen.blit(self.img, self.rect.topleft)
