import pygame, sys
import Read_files#for the fonts
import Engine
import Entities
import Level
import Action
import BG

class Game_UI():

    def __init__(self):
        pygame.init()#initilise
        self.WINDOW_SIZE = (576,324)
        self.scale = 2
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen = pygame.Surface(self.WINDOW_SIZE)
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled, vsync = 1)
        self.start_BG = pygame.transform.scale(pygame.image.load('sprites/start_menu.jpg').convert(),self.WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.gameover = False
        self.ESC = False
        self.click = False
        self.font = Read_files.Alphabet("Sprites/aseprite/Alphabet/Alphabet.png")#intitilise the alphabet class, scale of alphabet
        self.health_sprites = Read_files.Hearts_Black().get_sprites()
        self.state = ['start']
        self.shake=False
        self.weather_paricles=BG.Weather()

        #initiate player
        self.player = Entities.Player([200,50])
        self.players = pygame.sprite.Group()

        #initiate all sprite groups
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bg = pygame.sprite.Group()
        self.invisible_blocks = pygame.sprite.Group()
        self.weather = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.fprojectiles = pygame.sprite.Group()#arrows
        self.eprojectiles = pygame.sprite.Group()#arrows
        self.loot = pygame.sprite.Group()

        self.individuals = pygame.sprite.Group()
        self.all_entities = pygame.sprite.Group()

        #initiate maps
        self.load_map('village1')

        #initiate weather
        self.weather = self.weather_paricles.create_particle('Sakura')#weather effects

    def game_loop(self, initiate_fade_in = False):

        while True:
            self.screen.fill((207,238,250))#fill game.screen

            # !!--change to load map--!!
            self.platforms,self.invisible_blocks=self.map.load_chunks()#chunks

            # !!--remove passing knight--!!
            self.input(self.player)#game inputs

            # !!--change to one group--!!
            Engine.Physics.movement(self.players)
            Engine.Physics.movement(self.enemies)
            Engine.Physics.movement(self.npcs)

            Engine.Collisions.check_collisions(self.players,self.platforms)
            Engine.Collisions.check_collisions(self.enemies,self.platforms)
            Engine.Collisions.check_collisions(self.npcs,self.platforms)
            Engine.Collisions.check_invisible(self.npcs,self.invisible_blocks)
            Engine.Collisions.check_collisions_loot(self.loot,self.platforms)
            Engine.Collisions.pickup_loot(self.player,self.loot)
            Engine.Collisions.check_enemy_collision(self.player,self.enemies,self.loot)

            check_map = Engine.Collisions.check_interaction(self.player,self.interactables)
            if check_map:
                self.change_map(check_map)


            for enemy in self.enemies:
                enemy.AI(self.player,self.screen)#the enemy Ai movement, based on knight position
            for npc in self.npcs:
                npc.AI()

            # !!--check later--!!
            Action.actions(self.fprojectiles,self.players,self.platforms,self.enemies,self.screen,self.loot)#f_action swinger, target1,target2
            Action.actions(self.eprojectiles,self.enemies,self.platforms,self.players,self.screen,self.loot)#f_action swinger, target1,target2

            # !!--change to one group--!!   eventually change this to set animation image in update
            Engine.Animation.set_img(self.players)
            Engine.Animation.set_img(self.enemies)
            Engine.Animation.set_img(self.npcs)

            pygame.draw.rect(self.screen, (255,0,0), self.player.rect,2)#checking hitbox
            pygame.draw.rect(self.screen, (0,255,0), self.player.hitbox,2)#checking hitbox

            self.draw()
            self.scrolling()

            self.blit_screen_info()

            self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))#scale the screen

            Engine.Collisions.check_npc_collision(self.player,self.npcs,self.display)#need to be at the end so that the conversation text doesn't get scaled

            if initiate_fade_in:
                self.fade_in()
                first_loop_flag = False

            pygame.display.update()#update after every change
            self.clock.tick(60)#limmit FPS

            #fade if first loop


    def fade_in(self):
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



    def main_menu(self):
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

    def change_map(self, map_name):
        timer = 0
        load_time = 50
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

    def initiate_groups(self):
        #clean and load bg
        self.bg.empty()
        self.bg.add(Entities.BG_Block(self.map.load_bg(),(0,0)))

        #clean all groups
        self.players.empty()
        self.npcs.empty()
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()

        #load player and statics
        self.player, self.npcs, self.enemies, self.interactables = self.map.load_statics()
        self.players.add(self.player)

    def scrolling(self):
        self.map.scrolling(self.player.rect,self.player.shake)
        scroll = [-self.map.camera.scroll[0],-self.map.camera.scroll[1]]
        self.platforms.update(scroll)
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

    def draw(self):
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

    def inventory(self):
        pass

    def exit(self):
        pygame.quit()
        sys.exit()

    def blit_screen_info(self):
        self.blit_health()
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

    def blit_fps(self):
        fps_string = str(int(self.clock.get_fps()))
        self.font.render(self.screen,fps_string,(400,20),1)

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

    def input(self,player_class):#input while playing
        #game input
        player_class.shake-=1
        player_class.shake=max(-1,player_class.shake)#to not let it go to too low valyes

        if player_class.state!='talk':#if not in conversation

            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:#escape button
                        self.ESC=True
                        self.main_menu()

                    if event.key == pygame.K_t:
                        player_class.talk()

                    if event.key == pygame.K_RIGHT:
                        player_class.action['run']=True
                        player_class.action['stand']=False
                        player_class.dir[0]=1

                    if event.key == pygame.K_LEFT:
                        player_class.action['run']=True
                        player_class.action['stand']=False
                        player_class.dir[0]=-1

                    if event.key == pygame.K_UP:#press up
                        player_class.dir[1]=1
                    if event.key == pygame.K_DOWN:#press down
                        player_class.dir[1]=-1

                    if event.key == pygame.K_TAB:
                        player_class.change_equipment()

                    if event.key==pygame.K_SPACE and not player_class.action['fall'] and not player_class.action['jump']:#jump
                        player_class.jump()

                    if event.key==pygame.K_f:
                        player_class.action[player_class.equip]=True
                        #player_class.attack_action()

                    if event.key==pygame.K_g:
                        player_class.interacting = True

                    if event.key == pygame.K_i:
                        self.inventory()#open inventort

                    if event.key == pygame.K_LSHIFT and player_class.dashing_cooldown>9:#left shift
                        player_class.dashing()

                elif event.type == pygame.KEYUP:#lift bottom
                    if event.key == pygame.K_RIGHT and player_class.dir[0]>0:
                        player_class.action['stand']=True
                        player_class.action['run']=False

                    if event.key == pygame.K_t:#if release button
                        if player_class.state!='talk':#if not in conversation
                            player_class.state='stand'
                            player_class.action['talk']=False

                    if event.key == pygame.K_LEFT and player_class.dir[0]<0:
                        player_class.action['stand']=True
                        player_class.action['run']=False

                    if event.key == pygame.K_UP:
                        player_class.dir[1]=0

                    if event.key == pygame.K_DOWN:
                        player_class.dir[1]=0

                    if event.key==pygame.K_g:
                        player_class.interacting = False
