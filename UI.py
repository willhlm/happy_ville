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
        self.health_sprites = Read_files.Hearts_Black().get_sprites()
        self.spirit_sprites = Read_files.Sprites().generic_sheet_reader("Sprites/UI/Spirit/spirit_orbs.png",9,9,1,3)
        self.state = ['start']
        self.map_state = Read_files.read_json("map_state.json")
        self.mixer = None

        self.collisions = Engine.Collisions()

        #initiate player
        self.player = Entities.Player([200,50])
        self.players = pygame.sprite.Group(self.player)

        #initiate all sprite groups
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bg = pygame.sprite.Group()
        self.bg_far = pygame.sprite.Group()
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
        self.weather = self.weather_paricles.create_particle('Sakura')#weather effects

        #initiate maps
        self.load_map('village1')

    def main_menu(self):
        while True:


    def game_loop(self, initiate_fade_in = False):

        while True:
            self.screen.fill((207,238,250))#fill game.screen

            # !!--change to load map--!!
            self.platforms,self.invisible_blocks=self.map.load_chunks()#chunks

            self.input()#game inputs

            # !!--change to one group--!!
            Engine.Physics.movement(self.players)
            Engine.Physics.movement(self.enemies)
            Engine.Physics.movement(self.npcs)

            self.collisions.check_collisions(self.players,self.platforms)
            self.collisions.check_collisions(self.enemies,self.platforms)
            self.collisions.check_collisions(self.npcs,self.platforms)
            self.collisions.check_invisible(self.npcs,self.invisible_blocks)
            self.collisions.check_collisions_loot(self.loot,self.platforms)
            self.collisions.pickup_loot(self.player,self.loot)
            self.collisions.check_enemy_collision(self.player,self.enemies,self.loot)

            self.scrolling()#need to be above action_collision
            self.draw()

            self.collisions.action_collision(self.fprojectiles,self.players,self.platforms,self.enemies,self.screen,self.loot,self.cosmetics)#f_action swinger, target1,target2
            self.collisions.action_collision(self.eprojectiles,self.enemies,self.platforms,self.players,self.screen,self.loot,self.cosmetics)#f_action swinger, target1,target2

            self.group_distance()#update the groups beased on if they are on screen or not

            change_map, chest_id = self.collisions.check_interaction(self.player,self.interactables)
            if change_map:
                self.change_map(change_map)
            elif chest_id:
                self.map_state[self.map.level_name]["chests"][chest_id][1] = "opened"

            for enemy in self.enemies:
                enemy.AI(self.player,self.screen)#the enemy Ai movement, based on knight position
            for npc in self.npcs:
                npc.AI()

            # !!--change to one group--!!   eventually change this to set animation image in update
            #Engine.Animation.set_img(self.players)
            #Engine.Animation.set_img(self.enemies)
            #Engine.Animation.set_img(self.npcs)
            #Engine.Animation.set_img(self.fprojectiles)

            pygame.draw.rect(self.screen, (255,0,0), self.player.rect,2)#checking hitbox
            pygame.draw.rect(self.screen, (0,255,0), self.player.hitbox,2)#checking hitbox

            self.blit_screen_info()

            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen

            Engine.Collisions.check_npc_collision(self.player,self.npcs,self.display)#need to be at the end so that the conversation text doesn't get scaled

            if initiate_fade_in:
                self.fade_in()
                first_loop_flag = False

            pygame.display.update()#update after every change
            self.clock.tick(60)#limmit FPS

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
        self.mixer.fadeout(int(1000*load_time/60))
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
        self.load_song("Audio/Music/Yellow.wav")

    def load_song(self, path):
        self.mixer = pygame.mixer.Sound(path)
        self.mixer.set_volume(0.1)
        self.mixer.play(-1)

    def initiate_groups(self):
        #clean and load bg
        self.bg.empty()
        self.bg_far.empty()
        for i, ele in enumerate(self.map.load_bg()):
            if i == 0:
                self.bg.add(ele)
            elif i == 1:
                self.bg_far.add(ele)

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
        self.platforms.update(scroll)
        self.bg_far.update(scroll)
        self.bg.update(scroll)
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
        self.bg_far.draw(self.screen)
        self.bg.draw(self.screen)
        #self.weather.draw(self.screen)

        self.platforms.draw(self.screen)
        self.interactables.draw(self.screen)
        self.players.draw(self.screen)
        self.enemies.draw(self.screen)
        self.npcs.draw(self.screen)
        self.fprojectiles.draw(self.screen)
        self.eprojectiles.draw(self.screen)
        self.loot.draw(self.screen)
        self.cosmetics.draw(self.screen)

    def inventory(self):
        pass

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
        self.font.render(self.screen,fps_string,(350,20),1)

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
        self.font.render(self.display,'Start Game',(200,100),1)
        start_rect=pygame.Rect(200,100,100,100)
        self.font.render(self.display,'Options',(200,200),1)
        option_rect=pygame.Rect(200,200,100,100)
        self.font.render(self.display,'Exit Game',(200,400),1)
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

        self.font.render(self.display,'Resolution',(200,100),1)
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.click=False
            self.state.append('resolution')

        self.input_quit()

    def resolution_menu(self):
        self.display.fill((207,238,250))#fill game.screen

        self.font.render(self.display,'1000x800',(200,100),1)
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.screen=pygame.display.set_mode((1000,800))
            #self.start_BG=pygame.transform.scale(self.start_BG,(1000,800))#recale the BG
            #self.screen.blit(self.start_BG,(0,0))

        self.input_quit()

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
        if self.player.state!='talk':#if not in conversation

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
                        self.player.action['run']=True
                        self.player.action['stand']=False
                        self.player.dir[0]=1

                    if event.key == pygame.K_LEFT:
                        self.player.action['run']=True
                        self.player.action['stand']=False
                        self.player.dir[0]=-1

                    if event.key == pygame.K_UP:#press up
                        self.player.dir[1]=1
                    if event.key == pygame.K_DOWN:#press down
                        self.player.dir[1]=-1

                    if event.key == pygame.K_TAB:
                        self.player.change_equipment()

                    if event.key==pygame.K_SPACE and not self.player.action['fall'] and not self.player.action['jump']:#jump
                        self.player.jump()

                    if event.key==pygame.K_f:
                        if not self.player.action['dash']:
                            self.player.action[self.player.equip]=True
                            self.player.charging[0] = True

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

                    if event.key==pygame.K_f:
                        if not self.player.action['dash']:
                            self.player.charging[0]=False
                            self.player.phase='main'
                            self.player.frame=0
