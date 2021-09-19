import pygame, Read_files, random, sys

class Entity(pygame.sprite.Sprite):

    acceleration=[1,0.8]

    def __init__(self):
        super().__init__()
        self.movement=[0,0]
        self.velocity=[0,0]
        self.frame = 0
        self.dir=[1,0]#[horizontal (right 1, left -1),vertical (up 1, down -1)]
        self.ac_dir=self.dir.copy()
        self.world_state=0#state of happyness thingy of the world
        self.loot={'coin':0}
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.collision_spikes = {'top':False,'bottom':False,'right':False,'left':False}
        self.phase='pre'
        self.max_vel = 10
        self.charging=[False]#a list beause to make it a pointer
        self.hitbox_offset=(0,0)
        self.framerate=4

    def death(self,loot):
        if self.health<=0:#if 0 health of enemy
            self.action['death']=True
            self.action['run']=False
            self.velocity=[0,0]
            self.loots(loot)
            return self.shake#screen shake when eneny dies
        return 0

    def take_dmg(self,dmg):
        self.health-=dmg
        if dmg>0:
            self.action['hurt']=True

    def set_img(self):#action is set to true- > pre animation. When finished, main animation and set action to false -> do post animatino
        all_action=self.priority_action+self.nonpriority_action

        for action in all_action:#go through the actions
            if self.action[action] and action in self.priority_action:#if the action is priority

                if action != self.state:
                    self.state = action
                    self.reset_timer()

                self.image = self.sprites.get_image(action,self.frame//self.framerate,self.ac_dir)
                self.frame += 1

                if self.frame == self.sprites.get_frame_number(action,self.ac_dir)*self.framerate:
                    if action == 'death':
                        self.kill()
                    else:
                        self.reset_timer()
                        self.action[action] = False
                        self.state = 'stand'
                        self.action[self.equip]=False#to cancel even if you get hurt
                break

            elif self.action[action] and action in self.nonpriority_action:#if the action is nonpriority

                #reset timer if the action is wrong
                if action != self.state:
                    self.state = action
                    self.reset_timer()

                self.image = self.sprites.get_image(action,self.frame//self.framerate,self.dir)
                self.frame += 1

                if self.frame == self.sprites.get_frame_number(action,self.dir)*self.framerate:
                        self.reset_timer()
                break#take only the higest priority of the nonpriority list

    def AI(self,knight):
        pass

    def attack_action(self,projectiles):
        return projectiles

    def check_collisions(self):
        self.friction[1]=0

        if self.collision_types['bottom']:#if on ground
            self.dashing_cooldown=10
            self.action['fall']=False
            self.action['stand']=True
            self.action['wall']=False
            #self.action['jump']=False

            #if self.dir[1]<0:#if on ground, cancel sword swing
            #    self.action['sword']=False

        else:#if not on ground
            #self.action['stand']=False
            if self.velocity[1]>=0:#if falling down
                self.action['jump']=False
                self.action['fall']=True
                if self.collision_types['right'] or self.collision_types['left']:#on wall and not on ground
                    self.action['wall']=True
                    self.action['dash']=False
                    self.action['fall']=False
                    self.friction[1]=0.4
                    self.dashing_cooldown=10
                else:
                    self.action['wall']=False
            else:#if going up
                self.action['jump']=True

        if self.collision_types['top']:#knock back when hit head
            self.velocity[1]=0

        if self.collision_spikes['bottom']:
            self.action['hurt']=True
            self.velocity[1]=-6
            self.health-=10
            if self.health<=0:
                self.action['death']=True

    def physics_movement(self):
        self.velocity[1]=self.velocity[1]+self.acceleration[1]-self.velocity[1]*self.friction[1]#gravity
        self.velocity[1]=min(self.velocity[1],7)#set a y max speed

        if self.action['dash']:
            self.dashing_cooldown-=1
            self.velocity[1]=0
            self.velocity[0]=self.velocity[0]+self.ac_dir[0]*0.5

            if abs(self.velocity[0])<10:#max horizontal speed
                self.velocity[0]=self.ac_dir[0]*10
            #entity.velocity[0]=max(10,entity.velocity[0])

        if self.action['run'] and not self.charging[0]:#accelerate horizontal to direction when not dashing
            self.velocity[0]+=self.dir[0]*self.acceleration[0]
            self.friction[0]=0.2
            if abs(self.velocity[0])>self.max_vel:#max horizontal speed
                self.velocity[0]=self.dir[0]*self.max_vel

        self.movement[1]=self.velocity[1]#set the vertical velocity

        self.velocity[0]=self.velocity[0]-self.friction[0]*self.velocity[0]#friction
        self.movement[0]=self.velocity[0]#set the horizontal velocity

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

        self.check_collisions()
        self.physics_movement()

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
        self.image = pygame.image.load("Sprites/Enteties/aila/main/stand/aila_idle_2.png").convert()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],16,35)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.sprites = Read_files.Sprites_Player('Sprites/Enteties/aila/',True)
        self.health = 100
        self.max_health = 250
        self.spirit = 100
        self.max_spirit = 100
        self.priority_action=['death','hurt','dash','sword','hammer','stone','force','heal','shield']#animation
        self.nonpriority_action=['jump','wall','fall','run','stand']#animation
        self.action={'stand':True,'run':False,'hammer':False,'sword':False,'jump':False,'death':False,'hurt':False,'stone':False,'dash':False,'wall':False,'fall':False,'inv':False,'talk':False,'force':False,'heal':False,'shield':False}
        self.state = 'stand'
        self.equip='hammer'#starting abillity
        self.sword=Sword(self.dir,self.hitbox)
        self.hammer=Sword(self.dir,self.hitbox)
        self.shield=Shield(self.ac_dir,self.hitbox)
        self.force=Force(self.ac_dir,self.hitbox)
        self.action_sfx_player = pygame.mixer.Channel(1)
        self.action_sfx_player.set_volume(0.1)
        self.action_sfx = {'run': pygame.mixer.Sound("Audio/SFX/player/footstep.mp3")}
        self.movement_sfx_timer = 110

        self.hitbox_offset = (0,13)
        self.interacting = False
        self.friction=[0.2,0]
        self.loot={'Amber_Droplet':10,'Arrow':2}#the keys need to have the same name as their respective classes
        self.action_cooldown=False
        self.shake=0
        self.dashing_cooldown=10
        self.abilities=['hammer','stone','force','heal','shield']#a list of abillities the player can do (should be updated as the game evolves)

        #frame rates per action
        self.framerate={'wall':4,'hammer':2,'death':2,'hurt':2,'dash':2,'sword':4,'stone':6,'force':6,'heal':4,'shield':2,'fall':5,'stand':4,'run':5,'jump':5}

    def load_sfx(self):
        if self.action['run'] and not self.action['fall'] and self.movement_sfx_timer > 15:
            self.action_sfx_player.play(self.action_sfx['run'])
            self.movement_sfx_timer = 0
        self.movement_sfx_timer += 1

    def combined_action(self,action):
        actions=['sword','jump','fall']#the animations in which should change if runnig or standing
        if action in actions:
            if self.action['run']:
                action=action+'_run'
            elif self.action['stand']:
                action=action+'_stand'
        return action

    def set_img(self):
        all_action=self.priority_action+self.nonpriority_action

        for action in all_action:#go through the actions
            if self.action[action]:

                if action != self.state and self.phase!='post':#changing action
                    self.state = action
                    self.reset_timer()#reset frame an remember the direction
                    self.phase = 'pre'
                    self.comb_action=self.combined_action(action)

                if action in self.nonpriority_action:
                    dir=self.dir
                else:#if priority action
                    dir=self.ac_dir

                if self.sprites.get_frame_number(self.comb_action,dir,'pre') == 0:#if there is no pre animation
                    self.phase='main'

                self.image = self.sprites.get_image(self.comb_action,self.frame//self.framerate[action],dir,self.phase)
                self.frame += 1

                if self.frame == self.sprites.get_frame_number(self.comb_action,dir,self.phase)*self.framerate[action]:
                    self.frame=0

                    if action == 'death':
                        self.kill()

                    if self.phase=='pre' or self.phase=='charge':
                        if self.charging[0] and action in self.abilities:#do not set chagre while standing/running

                            if action=='heal' and self.phase=='charge':#special for heal. After charge is finished, enter main phase
                                self.phase='main'
                            else:
                                self.phase='charge'
                        else:
                            self.phase = 'main'

                    elif self.phase == 'main':
                        if self.sprites.get_frame_number(self.comb_action,dir,'post') == 0:#if there is no post animation
                            if action in self.priority_action:
                                self.phase = 'pre'
                                self.action_cooldown = False#allow for new action after animation
                                self.action[action] = False
                                self.action[self.equip] = False#cancel abillity in case hurt
                        else:#if there is post animation
                            self.phase = 'post'

                    else:#if post animation
                        self.phase = 'pre'
                        self.action_cooldown = False#allow for new action after post animation
                        self.action[action] = False
                break

    def set_pos(self, pos):
        self.rect.center = (pos[0],pos[1])
        self.hitbox.center = self.rect.center

    def healing(self):
        if self.spirit>=1:
            self.health+=20
            self.spirit-=20

    def take_dmg(self,dmg):
        if self.shield.health<=0 or self.shield.lifetime<0:
            self.health-=dmg
            self.action['hurt']=True

    def spawn_sword(self):
        self.sword.dir=self.ac_dir
        self.sword.lifetime=7
        self.sword.spawn(self.hitbox)

    def spawn_hammer(self):
        self.hammer.dir=self.ac_dir
        self.hammer.lifetime=7
        self.hammer.spawn(self.hitbox)
        self.spirit -= 10
        self.hammer.state='pre'

    def spawn_shield(self):
        self.shield.hitbox=pygame.Rect(self.hitbox[0],self.hitbox[1],self.hitbox.width+5,self.hitbox.height)
        self.shield.lifetime=200
        self.shield.health=100
        self.state='pre'
        self.spirit -= 10

    def spawn_force(self):
        self.force.lifetime=20
        self.force.dir=self.ac_dir

        if self.force.dir[1]!=0:#shooting up or down
            self.force.velocity=[0,-self.force.dir[1]*10]
        else:#horizontal
            self.force.velocity=[self.force.dir[0]*10,0]

        self.force.state='pre'
        self.force.hitbox=pygame.Rect(self.hitbox[0],self.hitbox[1],30,30)
        self.force.rect.center=self.force.hitbox.center#match the positions of hitboxes
        self.spirit -= 10
        self.force_jump()

    #def quick_attack(self,projectiles):
    #    if not self.action_cooldown:
    #        self.action['sword']=True
    #        self.action_cooldown=True#cooldown flag
    #        self.spawn_sword()
            #self.sword=Sword(self.ac_dir,self.hitbox)
    #        return self.sword
    #    return projectiles

    def attack_action(self,projectiles):
        #always eneters in every iteration
        if self.action['sword'] and not self.action_cooldown:
            if self.phase == 'main':#produce the object in the main animation
                self.spawn_sword()
                projectiles.add(self.sword)
                self.action_cooldown=True#cooldown flag

        elif self.action[self.equip] and not self.action_cooldown:

            if self.phase == 'pre':
                if self.equip=='stone' and self.spirit >= 10:#creates the objct in pre phase

                    projectiles.add(Stone(self.ac_dir,self.hitbox,self.charging))
                    self.spirit -= 10
                    self.action_cooldown=True#cooldown flag

            elif self.phase == 'main':#produce the object in the main animation
                if self.equip=='hammer':
                    self.spawn_hammer()
                    projectiles.add(self.hammer)
                    #projectiles.add(Sword(self.ac_dir,self.hitbox))
                elif self.equip == 'force' and self.spirit >= 10:
                    self.spawn_force()
                    projectiles.add(self.force)
                    #projectiles.add(Force(self.ac_dir,self.hitbox))

                elif self.equip == 'shield' and self.spirit >= 10 and self.shield.lifetime<0:
                    #self.shield=Shield(self.ac_dir,self.hitbox)
                    self.spawn_shield()
                    projectiles.add(self.shield)

                elif self.equip=='heal':
                    self.healing()
                self.action_cooldown=True#cooldown flag

        return projectiles

    def force_jump(self):
        #if self.dir[1]!=0:
        self.velocity[1]=self.dir[1]*10#force jump

    def dashing(self):
        if self.spirit>=10 and not self.charging[0]:#if we have spirit
            self.velocity[0] = 30*self.dir[0]
            self.action['dash'] = True
            self.spirit -= 10
            self.action[self.equip]=False#cancel any action
            self.action['sword']=False#cancel any action

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
        #self.update_hitbox()
        if self.spirit <= self.max_spirit:
            self.spirit += 0.1

        self.sword.updates(self.hitbox)
        self.hammer.updates(self.hitbox)
        self.shield.updates(self.hitbox)
        self.set_img()
        self.load_sfx()

    def update_hitbox(self):
        self.hitbox.center = [self.rect.center[0] + self.hitbox_offset[0], self.rect.center[1] + self.hitbox_offset[1]]

    def update_rect(self):
        self.rect.center = [self.hitbox.center[0] - self.hitbox_offset[0], self.hitbox.center[1] - self.hitbox_offset[1]]

    def loots(self,loot):
        pass

class Enemy_1(Player):
    def __init__(self,pos):
        super().__init__(pos)
        self.health=10
        self.distance=[0,0]
        self.inv=False#flag to check if collision with invisible blocks
        self.sprites = Read_files.Sprites_enteties('Sprites/Enteties/enemies/evil_knight/')
        self.shake=self.hitbox.height/10

    def AI(self,player):#the AI

        self.distance[0]=int((self.rect[0]-player.rect[0]))#follow the player
        self.distance[1]=int((self.rect[1]-player.rect[1]))#follow the player

        if abs(self.distance[0])>150 and abs(self.distance[1])>40 or player.action['death'] or self.action['hurt']:#don't do anything if far away, or player dead or while taking dmg
            self.action['run']=False
            self.action['stand']=True

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

class Woopie(Entity):
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/Enteties/enemies/woopie/stand/Kodama_stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 1
        self.priority_action=['death','pick']#animation
        self.nonpriority_action=['run','stand']#animation
        self.action={'stand':True,'run':False,'death':False,'pick':False,'fall':False,'dash':False,'hurt':False}
        self.state = 'stand'
        self.equip='sword'
        self.sprites = Read_files.Sprites_enteties('Sprites/Enteties/enemies/woopie/')
        self.friction=[0.2,0]
        self.loot={'Amber_Droplet':10}#the keys need to have the same name as their respective classes
        self.shake=10
        self.counter=0
        self.acceleration=[1,0.2]
        self.max_vel = 1
        self.framerate=6

    @staticmethod#a function to add glow around the entity
    def add_white(radius,colour,screen,pos):
        surf=pygame.Surface((2*radius,2*radius))
        pygame.draw.circle(surf,colour,(radius,radius),radius)
        surf.set_colorkey((0,0,0))
        screen.blit(surf,(pos[0]-radius,pos[1]-radius),special_flags=pygame.BLEND_RGB_ADD)

    def update(self,pos):
        super().update(pos)
        self.set_img()

    def AI(self,player,screen):#the AI
        #light around the entity
        Woopie.add_white(20,(20,20,20),screen,self.rect.center)#radius, clolor, screen,position
        self.counter+=1

        choice=self.priority_action+self.nonpriority_action
        choice.remove('death')

        if self.counter>=100:
            action=random.choice(choice)
            self.action[action]=True
            self.counter=0

            if self.action['run']:
                self.dir[0]=-self.dir[0]
                self.action['run']=random.choice([False,True])

class Enemy_2(Entity):
    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/Enteties/enemies/flowy/stand/Stand1.png").convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.hitbox=pygame.Rect(pos[0],pos[1],20,40)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.health = 10
        self.priority_action=['death','hurt','sword','stone','trans']#animation
        self.nonpriority_action=['fall','run','stand']#animation
        self.action={'stand':True,'run':False,'sword':False,'death':False,'hurt':False,'stone':False,'fall':False,'trans':False,'dash':False}
        self.state = 'stand'
        self.equip='sword'
        self.sprites = Read_files.Sprites_enteties('Sprites/Enteties/enemies/flowy/')
        self.friction=[0.2,0]
        self.loot={'Amber_Droplet':2,'Arrow':1}#the keys need to have the same name as their respective classes
        self.distance=[0,0]
        self.shake=self.hitbox.height/10

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

        if 100 < abs(self.distance[0])<200 and abs(self.distance[1])<100 and not player.action['death']:#swing sword when close
            self.action['trans'] = True

        elif abs(self.distance[0])<100 and abs(self.distance[1])<100 and not player.action['death']:#swing sword when close
            self.action[self.equip] = True

#remove dev when working
class NPC(Entity):

    acceleration=[0.3,0.8]

    def __init__(self):
        super().__init__()
        self.name = '<always define name>'
        self.action = {'stand':True,'run':False,'death':False,'hurt':False,'dash':False,'inv':False,'talk':False}
        self.nonpriority_action = ['run','stand']
        self.priority_action = ['death','hurt']
        self.health = 50
        self.state = 'stand'
        self.conv_index = 0
        self.friction=[0.2,0]

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
        if self.action['talk']:
            self.action['run'] = False
        else:
            self.AI()
        self.set_img()

    def AI(self):
        pass

    def stay_still(self):
        self.acceleration=[0,0]
        self.action['stand']=True

    def move_again(self):
        self.acceleration=[1,0.8]

class Aslat(NPC):

    def __init__(self, pos):
        super().__init__()
        self.name = 'Aslat'
        self.sprites = Read_files.Sprites_enteties("Sprites/Enteties/NPC/" + self.name + "/animation/")
        self.image = self.sprites.get_image('stand', 0, self.dir)
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = pygame.Rect(pos[0],pos[1],18,40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox
        self.portrait=pygame.image.load('Sprites/Enteties/NPC/MrBanks/Woman1.png').convert_alpha()  #temp
        self.load_conversation()
        self.max_vel = 1.5

    def AI(self):
        self.action['run']=True
        if abs(self.rect[0])>500 or abs(self.rect[1])>500:#if far away
            self.stay_still()
        else:
            self.move_again()

        if self.action['inv']:#collision with invisble block
            self.velocity[0] = -self.velocity[0]
            self.dir[0] = -self.dir[0]
            self.action['inv'] = False

class MrBanks(NPC):
    def __init__(self,pos):
        super().__init__()
        self.name = 'MrBanks'
        self.image = pygame.image.load("Sprites/Enteties/player/run/HeroKnight_run_0.png").convert_alpha()
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

class Block(pygame.sprite.Sprite):

    def __init__(self,img,pos):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]

class Platform(Block):

    def __init__(self,img,pos,chunk_key=False):
        super().__init__(img,pos)
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key
        self.spike=False

    def update(self,pos):
        super().update(pos)
        self.hitbox.center=self.rect.center

class Spikes(Block):
    def __init__(self,img,pos,chunk_key=False):
        super().__init__(pygame.image.load("Sprites/level_sheets/Spkies.png").convert_alpha(),pos)
        self.hitbox = self.rect.inflate(0,0)
        self.chunk_key=chunk_key
        self.spike=True

    def update(self,pos):
        super().update(pos)
        self.hitbox.center=self.rect.center

class BG_Block(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)

class FG_fixed(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)

class FG_paralex(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=1.25

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + self.paralex*pos[0], self.rect.topleft[1] + self.paralex*pos[1]]

class BG_near(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=0.75
        self.true_pos = self.rect.topleft

    def update(self,pos):
        #self.true_pos= [self.true_pos[0] + self.paralex*pos[0], self.true_pos[1] + self.paralex*pos[1]]
        self.true_pos= [self.true_pos[0] + self.paralex*pos[0], self.true_pos[1] + pos[1]]
        self.update_pos()

    def update_pos(self):
        self.rect.topleft = self.true_pos

class BG_mid(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=0.5

    def update(self,pos):
        self.rect.topleft = [self.rect.topleft[0] + int(self.paralex*pos[0]), self.rect.topleft[1] + int(self.paralex*pos[1])]

class BG_far(Block):

    def __init__(self,img,pos):
        super().__init__(img,pos)
        self.paralex=0.03
        self.true_pos = self.rect.topleft

    def update(self,pos):
        self.true_pos= [self.true_pos[0] + self.paralex*pos[0], self.true_pos[1] + self.paralex*pos[1]]
        #self.true_pos= [self.true_pos[0] + self.paralex*pos[0], self.true_pos[1] + pos[1]]
        self.update_pos()

    def update_pos(self):
        self.rect.topleft = self.true_pos

class Invisible_block(pygame.sprite.Sprite):

    def __init__(self,pos):
        super().__init__()
        self.rect=pygame.Rect(pos[0],pos[1],2,2)
        self.rect.topleft = pos
        self.hitbox = self.rect.inflate(0,0)

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

class Weapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frame=0
        self.charging=[False]
        self.action=''
        self.shake=0

    def update(self,scroll,entity_ac_dir=[0,0],entity_hitbox=[0,0]):
        #remove the equipment if it has expiered
        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        self.set_img()
        self.destroy()

    def set_img(self):
        self.image = self.sprites.get_image(self.action,self.frame//4,self.dir,self.state)
        self.frame += 1

        if self.frame == self.sprites.get_frame_number(self.action,self.dir,self.state)*4:
            self.reset_timer()
            if self.state=='pre':
                if self.charging[0]:
                    self.state='charge'
                else:
                    self.state = 'main'
            #elif self.state=='charge' and not self.charging[0]:
            #    self.state='main'
            elif self.state=='post':
                self.kill()

    def reset_timer(self):
        self.frame = 0

    def destroy(self):
        if self.lifetime<0:
            self.kill()

class Sword(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()
        self.lifetime=7#need to be changed depending on the animation of sword of player
        self.dmg=10
        self.velocity=[0,0]
        #self.state='pre'

        self.image = pygame.image.load("Sprites/Attack/Sword/main/swing1.png").convert_alpha()

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],entity_hitbox.width+5,entity_hitbox.height)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

        self.dir=entity_dir.copy()
        self.spawn(entity_hitbox)#spawn hitbox based on entity position and direction

    def updates(self,entity_hitbox):
        self.lifetime-=1
        self.spawn(entity_hitbox)
        self.destroy()#check lifetime

    def spawn(self,entity_hitbox):
        if self.dir[1] > 0:#up
            self.hitbox.midbottom=entity_hitbox.midtop
        elif self.dir[1] < 0:#down
            self.hitbox.midtop=entity_hitbox.midbottom
        elif self.dir[0] > 0 and self.dir[1] == 0:#right
            self.hitbox.midleft=entity_hitbox.midright
        elif self.dir[0] < 0 and self.dir[1] == 0:#left
            self.hitbox.midright=entity_hitbox.midleft

    def update(self,scroll=0):
        pass

    def collision(self,entity=None,cosmetics=None,collision_ene=None):
        return self.shake
        #entity.velocity[1]=entity.dir[1]*10#nail jump
        #collision_ene.velocity[0]=entity.dir[0]*10#enemy knock back

class Shield(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()
        self.lifetime=1#need to be changed depending on the animation of sword of player
        self.health=100
        self.velocity=[0,0]
        self.state='pre'
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/Shield/',True)
        self.dmg=0

        self.image = pygame.image.load("Sprites/Attack/Shield/main/water_Shield1.png").convert_alpha()

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],20,20)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

        self.dir=entity_dir.copy()
        self.hitbox.center=entity_hitbox.center#spawn hitbox based on entity position and direction

    def update(self,scroll=0):
        pass

    def destroy(self):
        if self.lifetime<0 or self.health<=0:
            self.kill()

    def updates(self,entity_hitbox):
        self.lifetime-=1
        self.hitbox.center=entity_hitbox.center#spawn hitbox based on entity position and direction
        self.rect.center=self.hitbox.center

        self.set_img()
        self.destroy()#check lifetime and health

    def collision(self,entity=None,cosmetics=None,collision_ene=None):
        self.health-=10#reduce the health of this object
        return self.shake

class Stone(Weapon):
    def __init__(self,entity_dir,entity_rect,charge):
        super().__init__()
        self.velocity=[0,0]
        self.lifetime=100
        self.dmg=10
        self.state='pre'
        self.action='small'
        self.dir=entity_dir.copy()#direction of the projectile
        self.sprites = Read_files.Sprites_Player('Sprites/Attack/Stone/',True)

        self.image = pygame.image.load("Sprites/Attack/Stone/pre/small/force_stone1.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_rect.center[0]-5+self.dir[0]*20,entity_rect.center[1]])
        self.hitbox=pygame.Rect(entity_rect.center[0]-5+self.dir[0]*20,entity_rect.center[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

        self.charging=charge#pointed to player charge state
        self.charge_velocity=self.dir[0]

    def update(self,scroll,entity_ac_dir=[0,0],entity_hitbox=[0,0]):
        #remove the equipment if it has expiered
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        self.set_img()#set the animation
        self.speed()#set the speed
        self.destroy()#if lifetime expires

    def speed(self):
        if self.state=='charge':#charging
            self.charge_velocity=self.charge_velocity+0.5*self.dir[0]
            self.charge_velocity=self.dir[0]*min(20,self.dir[0]*self.charge_velocity)#set max velocity

            if abs(self.charge_velocity)>=20:#increase the ball size when max velocity is reached
                self.action='medium'
                self.shake=2#add shake effect if the ball is big

            if not self.charging[0]:#when finish chaging
                self.frame=0
                self.state='main'
                self.velocity[0]=self.charge_velocity#set the velocity

        elif self.state=='main':#main pahse
            self.lifetime-=1#affect only the lifetime in main state
            if self.action=='small':#only have gravity if small
                self.velocity[1]+=0.1#graivity

    def collision(self,entity=None,cosmetics=None,collision_ene=None):
        self.velocity=[0,0]
        self.dmg=0
        self.state='post'
        return self.shake

    def rotate(self):
        angle=self.dir[0]*max(-self.dir[0]*self.velocity[0]*self.velocity[1],-60)

        self.image=pygame.transform.rotate(self.original_image,angle)#fig,angle,scale
        x, y = self.rect.center  # Save its current center.
        self.rect = self.image.get_rect()  # Replace old rect with new rect.
        self.hitbox=pygame.Rect(x,y,10,10)

        self.rect.center = (x, y)  # Put the new rect's center at old center.

class Force(Weapon):
    def __init__(self,entity_dir,entity_hitbox):
        super().__init__()

        if entity_dir[1]!=0:#shppting up or down
            self.velocity=[0,-entity_dir[1]*10]
        else:#horizontal
            self.velocity=[entity_dir[0]*10,0]

        self.lifetime=20
        self.dmg=0
        self.dir=entity_dir.copy()

        self.sprites = Read_files.Sprites_Player('Sprites/Attack/Force/')
        self.state='pre'

        self.image = pygame.image.load("Sprites/Attack/Force/pre/fly3.png").convert_alpha()
        if self.velocity[0]<0:#if shoting left
            self.image=pygame.transform.flip(self.image,True,False)

        self.rect = self.image.get_rect(center=[entity_hitbox[0],entity_hitbox[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0],entity_hitbox[1],30,30)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

    def collision(self,entity=None,cosmetics=None,collision_ene=None):#if hit something
        #push_strength=[500/(self.rect[0]-entity.rect[0]),500/(self.rect[1]-entity.rect[1])]
        self.state='post'
        self.frame=0
        self.velocity=[0,0]

        if collision_ene:#if collision with enemy
            cosmetics.add(Spirits([collision_ene.rect[0],collision_ene.rect[1]]))#spawn cosmetic spirits
            #if self.dir[1]!=0:
            #    entity.velocity[1]=self.dir[1]*abs(push_strength[1])#force jump
            if self.dir[1]==0:#push enemy back
                collision_ene.velocity[0]=self.dir[0]*10#abs(push_strength[0])
                collision_ene.velocity[1]=-6
            return self.shake
        return self.shake
        #if self.dir[1]!=0:#if patform down
        #    entity.velocity[1]=self.dir[1]*abs(push_strength[1])*0.75#force jump

class Loot(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        choice=[-20,-18,-16,-14,-12,-10,-8,-6,-4,-2,2,4,6,8,10,12,14,16,18,20]#just not 0
        self.pos=[random.choice(choice),random.choice(choice)]
        self.lifetime=300
        self.movement=[0,0]#for platfform collisions
        dir=self.pos[0]/abs(self.pos[0])#horizontal direction
        self.velocity=[dir*random.randint(0, 3),-4]
        self.collision_types = {'top':False,'bottom':False,'right':False,'left':False}
        self.collision_spikes = {'top':False,'bottom':False,'right':False,'left':False}
        self.animation_timer = 0

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def update_rect(self):
        self.rect.center = self.hitbox.center

    def platform_int(self):
        if self.collision_types['bottom']:
            self.velocity=[0,0]

    def update(self,scroll):
        #remove the equipment if it has expiered
        self.speed()

        self.lifetime-=1
        self.rect.topleft = [self.rect.topleft[0] + self.velocity[0]+scroll[0], self.rect.topleft[1] + self.velocity[1]+scroll[1]]
        self.hitbox.center = self.rect.center

        if self.lifetime<0:#remove after a while
            self.kill()

        self.platform_int()
        self.set_img()

    def set_img(self, frame_rate = 0.25):
        self.image = self.sprites['idle'][int(self.animation_timer)]
        if self.animation_timer == len(self.sprites['idle'])-1:
            self.animation_timer = 0
        self.animation_timer += frame_rate

    def speed(self):
        self.velocity[1]+=0.3#gravity

        self.velocity[1]=min(self.velocity[1],4)#set a y max speed
        self.movement[1]=self.velocity[1]#set the vertical velocity

class Coin(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/Enteties/Items/coin.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes

class Amber_Droplet(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/Enteties/Items/amber_droplet/idle/amber_droplet1.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/amber_droplet/')

class Arrow(Loot):
    def __init__(self,entity_hitbox):
        super().__init__()

        self.image = pygame.image.load("Sprites/Enteties/Items/arrow/idle/arrow.png").convert_alpha()
        self.rect = self.image.get_rect(center=[entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1]])
        self.hitbox=pygame.Rect(entity_hitbox[0]+self.pos[0],entity_hitbox[1]+self.pos[1],10,10)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.sprites = Read_files.Sprites().load_all_sprites('Sprites/Enteties/Items/arrow/')

class Spirits(pygame.sprite.Sprite):

    def __init__(self,pos):
        super().__init__()
        self.image = pygame.image.load("Sprites/animations/Spirits/Spirits1.png").convert_alpha()
        self.rect = self.image.get_rect(center=[pos[0],pos[1]])
        self.hitbox=pygame.Rect(pos[0],pos[1],5,5)
        self.rect.center=self.hitbox.center#match the positions of hitboxes
        self.frame=0
        self.lifetime=10

    def update(self,pos):
        self.lifetime -= 1

        self.rect.topleft = [self.rect.topleft[0] + pos[0], self.rect.topleft[1] + pos[1]]
        self.hitbox.center=self.rect.center

        if self.lifetime<0:
            self.kill()
