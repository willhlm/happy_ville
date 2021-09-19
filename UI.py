import pygame, sys
import Read_files
import Engine
import Entities
import Level
import BG

class Game_UI():

    def __init__(self):
        pygame.init()#initilise
        self.WINDOW_SIZE = (432,243)
        self.scale = 3
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen = pygame.Surface(self.WINDOW_SIZE)
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled, vsync = 1)
        self.start_BG = pygame.transform.scale(pygame.image.load('Sprites/UI/Menu/Start/start_menu.jpg').convert(),self.WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.ESC = False
        self.click = False
        self.font = Read_files.Alphabet("Sprites/UI/Alphabet/Alphabet.png")#intitilise the alphabet class, scale of alphabet
        self.text_bg_dict = Read_files.Sprites().generic_sheet_reader("Sprites/utils/text_bg4.png",16,16,3,3)
        self.health_sprites = Read_files.Sprites().generic_sheet_reader("Sprites/UI/health/hearts_black.png",9,8,2,3)
        self.spirit_sprites = Read_files.Sprites().generic_sheet_reader("Sprites/UI/Spirit/spirit_orbs.png",9,9,1,3)
        self.state = ['start']
        self.map_state = Read_files.read_json("map_state.json") #check this file for structure of object
        pygame.mixer.init
        self.bg_music = pygame.mixer.Channel(0)

        self.ability_menu=False#a flag to enter "abillity changing menue"
        self.ab_index=0#index for the ability selection

        self.collisions = Engine.Collisions()

        #initiate player
        self.player = Entities.Player([200,50])
        self.players = pygame.sprite.Group(self.player)

        #initiate all sprite groups
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bg_fixed = pygame.sprite.Group()
        self.bg_far = pygame.sprite.Group()
        self.bg_mid = pygame.sprite.Group()
        self.bg_near = pygame.sprite.Group()
        self.fg_fixed = pygame.sprite.Group()
        self.fg_paralex = pygame.sprite.Group()
        self.bgs = [self.bg_fixed,self.bg_far,self.bg_mid,self.bg_near,self.fg_fixed,self.fg_paralex]
        self.invisible_blocks = pygame.sprite.Group()
        self.weather = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.fprojectiles = pygame.sprite.Group()#arrows and sword
        self.eprojectiles = pygame.sprite.Group()#arrows and sword
        self.loot = pygame.sprite.Group()
        self.enemy_pause = pygame.sprite.Group() #include all entities that are far away
        self.npc_pause = pygame.sprite.Group() #include all entities that are far away
        self.cosmetics = pygame.sprite.Group() #spirits

        self.individuals = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group()

        self.weather_paricles=BG.Weather()#initiate whater
        self.weather = self.weather_paricles.create_particle('Snow')#weather effects

        #initiate maps
        self.load_map('village1')

    def game_loop(self, initiate_fade_in = False):

        while True:
            self.screen.fill((207,238,250))#fill game.screen

            self.platforms,self.invisible_blocks=self.map.load_chunks()#chunks

            self.input()#game inputs

            self.collisions.collide(self.players,self.platforms)
            self.collisions.collide(self.enemies,self.platforms)
            self.collisions.collide(self.npcs,self.platforms)
            self.collisions.check_invisible(self.npcs,self.invisible_blocks)
            self.collisions.check_collisions_loot(self.loot,self.platforms)
            self.collisions.pickup_loot(self.player,self.loot)
            self.collisions.check_enemy_collision(self.player,self.enemies,self.loot)

            self.scrolling() #need to be above action_collision, also includes group updates
            self.draw()

            self.collisions.action_collision(self.fprojectiles,self.players,self.platforms,self.enemies,self.screen,self.loot,self.cosmetics)#f_action swinger, target1,target2
            self.collisions.action_collision(self.eprojectiles,self.enemies,self.platforms,self.players,self.screen,self.loot,self.cosmetics)#f_action swinger, target1,target2

            self.group_distance() #update the groups beased on if they are on screen or not
            self.interactions()

            #!! -- maybe move this to update method in npc/enemy class
            for enemy in self.enemies:
                enemy.AI(self.player,self.screen)#the enemy Ai movement, based on knight position

            pygame.draw.rect(self.screen, (255,0,0), self.player.rect,2)#checking hitbox
            pygame.draw.rect(self.screen, (0,255,255), self.player.hitbox,2)#checking hitbox

            self.blit_screen_info()

            npc = Engine.Collisions.check_npc_collision(self.player,self.npcs)#need to be at the end so that the conversation text doesn't get scaled
            if npc:
                self.conversation_loop(npc)

            if self.ability_menu:
                self.change_abilities()#chaning ability menue

            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen

            if initiate_fade_in:
                self.fade_in()
                first_loop_flag = False

            pygame.display.update()
            self.clock.tick(60) #set FPS to 60

    def conversation_loop(self, npc):

        letter_frame = 0
        print_speed = 3 # higher number gives lower speed

        #convo specific inputs
        def input_conv():
            for event in pygame.event.get():

                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        self.player.action['talk'] = False

                    if event.key == pygame.K_t:
                        #finish sentence, or get next sentence if finished
                        nonlocal letter_frame
                        if letter_frame//print_speed < len(npc.get_conversation('state_1')):
                            letter_frame = 1000
                        else:
                            letter_frame = 0
                            npc.increase_conv_index()


        #main loop
        while(self.player.action['talk']):

            self.screen.fill((207,238,250))
            self.update_groups()
            self.draw()
            self.blit_screen_info()

            conv = npc.get_conversation('state_1') #return None if last conv have been had
            if not conv:
                self.player.action['talk'] = False
                break

            text_WINDOW_SIZE = (352, 96)
            text_window = self.fill_text_bg(text_WINDOW_SIZE)
            text_window.blit(npc.portrait,(0,10))

            text = self.font.render((272,80), conv, int(letter_frame//print_speed))
            text_window.blit(text,(64,8))

            blit_x = int((self.WINDOW_SIZE[0]-text_WINDOW_SIZE[0])/2) #make the text in the center
            self.screen.blit(text_window,(blit_x,60))

            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))
            pygame.display.update()

            self.clock.tick(60) #set FPS to 60
            letter_frame += 1
            input_conv()

        npc.action['talk'] = False

    def interactions(self):
        change_map, chest_id = self.collisions.check_interaction(self.player,self.interactables)
        if change_map:
            self.change_map(change_map)
        elif chest_id:
            self.map_state[self.map.level_name]["chests"][chest_id][1] = "opened"

    def fade_in(self):
    #fade if first loop
        timer = 0
        fade_time = 20
        while timer < fade_time:
            self.screen.fill((207,238,250))
            self.interactables.update((0,0))
            self.draw()
            self.blit_screen_info()
            fade_surface = pygame.Surface(self.WINDOW_SIZE, pygame.SRCALPHA)
            fade_surface.fill((0,0,0,255-int((timer)*255/fade_time)))
            self.screen.blit(fade_surface,(0,0))
            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen
            pygame.display.update()#update after every change
            self.clock.tick(60)#limmit FPS
            timer += 1

        self.game_loop()

    def group_distance(self):#remove the eneteies if it is off screen from thir group
        bounds=[-100,600,-100,350]#-x,+x,-y,+y

        for entity in self.enemies:
            if entity.rect[0]<bounds[0] or entity.rect[0]>bounds[1] or entity.rect[1]<bounds[2] or entity.rect[1]>bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
                self.enemies.remove(entity)
                self.enemy_pause.add(entity)

        for entity in self.enemy_pause:
            if bounds[0]<entity.rect[0]<bounds[1] and bounds[2]<entity.rect[1]<bounds[3]: #or abs(entity.rect[1])<300:#this means it is outside of screen
                self.enemies.add(entity)
                self.enemy_pause.remove(entity)

        for entity in self.npcs:
            if entity.rect[0]<bounds[0] or entity.rect[0]>bounds[1] or entity.rect[1]<bounds[2] or entity.rect[1]>bounds[3]: #or abs(entity.rect[1])>300:#this means it is outside of screen
                self.npcs.remove(entity)
                self.npc_pause.add(entity)

        for entity in self.npc_pause:
            if bounds[0]<entity.rect[0]<bounds[1] and bounds[2]<entity.rect[1]<bounds[3]: #or abs(entity.rect[1])<300:#this means it is outside of screen
                self.npcs.add(entity)
                self.npc_pause.remove(entity)

    def change_map(self, map_name):
        timer = 0
        load_time = 50
        self.bg_music.fadeout(int(1000*load_time/60))
        #fade before loading new map
        while timer < load_time:
            self.screen.fill((207,238,250))
            self.interactables.update((0,0))
            self.draw()
            self.blit_screen_info()
            fade_surface = pygame.Surface(self.WINDOW_SIZE, pygame.SRCALPHA)
            fade_surface.fill((0,0,0,int(timer*255/load_time)))
            self.screen.blit(fade_surface,(0,0))
            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen
            pygame.display.update()#update after every change
            self.clock.tick(60)#limmit FPS
            timer += 1

        #actually load the new map
        self.load_map(map_name)
        self.game_loop(True)

    def load_map(self, map_name):
        self.map = Level.Tilemap(map_name)
        self.initiate_groups()
        self.load_music()

    def load_music(self):
        self.bg_music.play(self.map.load_bg_music(),-1)
        self.bg_music.set_volume(0.1)

    def initiate_groups(self):
        #clean and load bg
        for bg in self.bgs:
            bg.empty()
        for i, bg in enumerate(self.map.load_bg()):
            self.bgs[i].add(bg)

        #clean all groups
        #self.players.empty()
        self.npcs.empty()
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()
        self.enemy_pause.empty()
        self.npc_pause.empty()

        #load all objects
        player_pos, self.npcs, self.enemies, self.interactables = self.map.load_statics(self.map_state[self.map.level_name])
        self.player.set_pos(player_pos)
        self.platforms,self.invisible_blocks=self.map.load_chunks()#chunks
        #self.players.add(self.player)

    def scrolling(self):
        self.map.scrolling(self.player.rect,self.collisions.shake)
        scroll = [-self.map.camera.scroll[0],-self.map.camera.scroll[1]]
        self.update_groups(scroll)

    def update_groups(self, scroll = (0,0)):
        self.platforms.update(scroll)
        for bg in self.bgs:
            bg.update(scroll)
        self.players.update(scroll)
        self.enemies.update(scroll)
        self.npcs.update(scroll)
        self.interactables.update(scroll)
        self.invisible_blocks.update(scroll)
        self.weather.update(scroll,self.screen)
        self.fprojectiles.update(scroll)
        self.eprojectiles.update(scroll)
        self.loot.update(scroll)
        self.npc_pause.update(scroll)
        self.enemy_pause.update(scroll)
        self.cosmetics.update(scroll)

    def draw(self):
        for i in range(1,4):
            self.bgs[i].draw(self.screen)
        self.bg_fixed.draw(self.screen)
        #self.weather.draw(self.screen)

        self.platforms.draw(self.screen)
        self.interactables.draw(self.screen)
        self.enemies.draw(self.screen)
        self.npcs.draw(self.screen)
        self.players.draw(self.screen)
        self.fprojectiles.draw(self.screen)
        self.eprojectiles.draw(self.screen)
        self.loot.draw(self.screen)
        self.cosmetics.draw(self.screen)
        for i in range(4,6):
            self.bgs[i].draw(self.screen)

    def inventory(self):
        pass

    def change_abilities(self):
        if self.player.state not in self.player.priority_action:#don't change if you are doing some attack

            self.screen.fill((20,20,20),special_flags=pygame.BLEND_RGB_ADD)#change the overall colour while changing equip
            pygame.time.wait(100)#slow motion

            positions=[]#placeholder
            for index,abillity in enumerate(self.player.abilities):
                coordinate=[100+50*index,200]

                self.screen.blit(self.font.render((50,50),abillity),(coordinate))
                positions.append(coordinate)#coordinates of all blits

            self.screen.blit(self.font.render((20,20),'o'),(positions[self.ab_index][0],positions[self.ab_index][1]-20))#the pointer

    def change_equipment(self):
        if self.player.state not in self.player.priority_action:#don't change if you are doing some attack
            self.ab_index=self.player.abilities.index(self.player.equip)

            while(self.ability_menu):

                self.screen.fill((207,238,250),special_flags=pygame.BLEND_RGB_ADD)#change the overall colour while changing equip
                self.update_groups()
                self.draw()
                self.blit_screen_info()

                positions=[]#placeholder
                for index,abillity in enumerate(self.player.abilities):
                    coordinate=[100+50*index,200]

                    self.screen.blit(self.font.render((50,50),abillity),(coordinate))
                    positions.append(coordinate)#coordinates of all blits

                self.screen.blit(self.font.render((20,20),'o'),(positions[self.ab_index][0],positions[self.ab_index][1]-20))#the pointer

                self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))
                pygame.display.update()

                self.clock.tick(60) #set FPS to 60
                self.input_ability()

    def input_ability(self):
        for event in pygame.event.get():

            if event.type == pygame.KEYDOWN:
                if event.type==pygame.QUIT:
                    self.exit()

                if event.key == pygame.K_RIGHT:
                    self.ab_index+=1
                    self.ab_index=min(len(self.player.abilities)-1,self.ab_index)
                if event.key == pygame.K_LEFT:
                    self.ab_index-=1
                    self.ab_index=max(0,self.ab_index)

            elif event.type == pygame.KEYUP:#lift bottom
                if event.key==pygame.K_TAB:
                    self.ability_menu=False
                    self.player.equip=self.player.abilities[self.ab_index]

                if event.key == pygame.K_RIGHT and self.player.dir[0]>0:
                    self.player.action['stand']=True
                    self.player.action['run']=False

                if event.key == pygame.K_LEFT and self.player.dir[0]<0:
                    self.player.action['stand']=True
                    self.player.action['run']=False

    def exit(self):
        pygame.quit()
        sys.exit()

    def blit_screen_info(self):
        self.blit_health()
        self.blit_spirit()
        self.blit_fps()

    def blit_health(self):
        #this code is specific to using heart.png sprites
        sprite_dim = [9,8] #width, height specific to sprites used
        blit_surface = pygame.Surface((int(self.player.max_health/20)*(sprite_dim[0] + 1),sprite_dim[1]),pygame.SRCALPHA,32)
        health = self.player.health

        for i in range(int(self.player.max_health/20)):
            health -= 20
            if health >= 0:
                blit_surface.blit(self.health_sprites[0],(i*(sprite_dim[0] + 1),0))
            elif health > -20:
                blit_surface.blit(self.health_sprites[-(health//4)],(i*(sprite_dim[0] + 1),0))
            else:
                blit_surface.blit(self.health_sprites[5],(i*(sprite_dim[0] + 1),0))

        self.screen.blit(blit_surface,(20, 20))

    def blit_spirit(self):

        sprite_dim = [9,9] #width, height specific to sprites used
        blit_surface = pygame.Surface((int(self.player.max_spirit/20)*(sprite_dim[0] + 1),sprite_dim[1]),pygame.SRCALPHA,32)
        spirit = self.player.spirit

        for i in range(int(self.player.max_spirit/20)):
            spirit -= 20
            if spirit > -10:
                blit_surface.blit(self.spirit_sprites[0],(i*(sprite_dim[0] + 1),0))
            elif spirit > -20:
                blit_surface.blit(self.spirit_sprites[1],(i*(sprite_dim[0] + 1),0))
            else:
                blit_surface.blit(self.spirit_sprites[2],(i*(sprite_dim[0] + 1),0))

        self.screen.blit(blit_surface,(20, 34))

    def blit_fps(self):
        fps_string = str(int(self.clock.get_fps()))
        self.screen.blit(self.font.render((30,12),'fps ' + fps_string),(350,20))

    def pause_menu(self):
        #self.screen.blit(self.start_BG,(0,0))
        #self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))
        self.display.fill((207,238,250))#fill game.screen

        while self.ESC:
            if self.state[-1] == 'start':
                self.start_menu()
            elif self.state[-1] == 'option':
                self.option_menu()
            elif self.state[-1] == 'resolution':
                self.resolution_menu()

    def start_menu(self):
        self.display.blit(self.font.render((50,50),'Start Game'),(200,100))
        start_rect=pygame.Rect(200,100,100,100)
        self.display.blit(self.font.render((50,50),'Options'),(200,200))
        option_rect=pygame.Rect(200,200,100,100)
        self.display.blit(self.font.render((50,50),'Exit Game'),(200,400))
        exit_rect=pygame.Rect(200,400,100,100)

        if start_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.ESC=False
            self.click=False
        elif option_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.click=False
            self.state.append('option')
        elif exit_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.exit()

        self.input_quit()

    def option_menu(self):
        self.display.fill((207,238,250))#fill game.screen

        self.display.blit(self.font.render((50,50),'Resolution'),(200,100))
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.click=False
            self.state.append('resolution')

        self.input_quit()

    def resolution_menu(self):
        self.display.fill((207,238,250))#fill game.screen

        self.display.blit(self.font.render((50,50),'1000x800'),(200,100))
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.screen=pygame.display.set_mode((1000,800))
            #self.start_BG=pygame.transform.scale(self.start_BG,(1000,800))#recale the BG
            #self.screen.blit(self.start_BG,(0,0))

        self.input_quit()

    # returns a surface with correct borders for text/menu bg,
    # size as input
    def fill_text_bg(self, surface_size):
        col = int(surface_size[0]/16)
        row = int(surface_size[1]/16)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32)

        for r in range(0,row):
            for c in range(0,col):
                if r==0:
                    if c==0:
                        surface.blit(self.text_bg_dict[0],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[2],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[1],(c*16,r*16))
                elif r==row-1:
                    if c==0:
                        surface.blit(self.text_bg_dict[6],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[8],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[7],(c*16,r*16))
                else:
                    if c==0:
                        surface.blit(self.text_bg_dict[3],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[5],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[4],(c*16,r*16))
        return surface

    def input_quit(self):#to exits between option menues
        pygame.display.update()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN:
                self.click=True
            if event.type==pygame.MOUSEBUTTONUP:
                self.click=False
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:#escape button
                    self.display.fill((207,238,250))#fill game.screen
                    #self.screen.blit(self.start_BG,(0,0))
                    #self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))
                    if len(self.state)!=1:
                        self.state.pop()#un-remember the last page

    def input(self):#input while playing
        #if self.player.state!='talk':#this can be removed

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:#escape button
                    self.ESC=True
                    self.pause_menu()

                if event.key == pygame.K_t:
                    self.player.talk()

                if event.key == pygame.K_RIGHT:
                    if not self.ability_menu:
                        self.player.action['run']=True
                        self.player.action['stand']=False
                        self.player.dir[0]=1
                    else:
                        self.ab_index+=1
                        self.ab_index=min(len(self.player.abilities)-1,self.ab_index)

                if event.key == pygame.K_LEFT:
                    if not self.ability_menu:
                        self.player.action['run']=True
                        self.player.action['stand']=False
                        self.player.dir[0]=-1
                    else:
                        self.ab_index-=1
                        self.ab_index=max(0,self.ab_index)

                if event.key == pygame.K_UP:#press up
                    self.player.dir[1]=1
                if event.key == pygame.K_DOWN:#press down
                    self.player.dir[1]=-1

                if event.key == pygame.K_TAB:
                    #self.player.change_equipment()
                    self.player.action['stand']=True
                    self.player.action['run']=False
                    self.ability_menu=True
                    #self.change_equipment()

                if event.key==pygame.K_SPACE and not self.player.action['fall'] and not self.player.action['jump']:#jump
                    #self.player.action['jump']=True
                    self.player.jump()

                if event.key==pygame.K_e:#aillities
                    if not self.player.action['dash']:
                        self.player.action[self.player.equip]=True
                        self.player.charging[0] = True

                if event.key==pygame.K_f:
                    if not self.player.action['dash']:
                        self.fprojectiles.add(self.player.quick_attack(self.fprojectiles))

                if event.key==pygame.K_g:
                    self.player.interacting = True

                if event.key == pygame.K_i:
                    self.inventory()#open inventort

                if event.key == pygame.K_LSHIFT and self.player.dashing_cooldown>9:#left shift
                    self.player.dashing()

            elif event.type == pygame.KEYUP:#lift bottom
                if event.key == pygame.K_RIGHT and self.player.dir[0]>0:
                    self.player.action['stand']=True
                    self.player.action['run']=False

                if event.key == pygame.K_t:#if release button
                    if self.player.state!='talk':#if not in conversation
                        self.player.state='stand'
                        self.player.action['talk']=False

                if event.key == pygame.K_LEFT and self.player.dir[0]<0:
                    self.player.action['stand']=True
                    self.player.action['run']=False

                if event.key == pygame.K_UP:
                    self.player.dir[1]=0

                if event.key == pygame.K_DOWN:
                    self.player.dir[1]=0

                if event.key==pygame.K_g:
                    self.player.interacting = False

                if event.key==pygame.K_TAB:
                    self.ability_menu=False
                    self.player.equip=self.player.abilities[self.ab_index]#select ability

                if event.key==pygame.K_e:
                    if not self.player.action['dash']:
                        self.player.charging[0]=False
