import pygame, sys
import Read_files#for the fonts

class Game_UI():
    def __init__(self):
        pygame.init()#initilise
        self.WINDOW_SIZE = (480,270)
        self.scale = 3
        self.WINDOW_SIZE_scaled = tuple([int(x*self.scale) for x in self.WINDOW_SIZE])
        self.screen=pygame.Surface(self.WINDOW_SIZE)
        self.display = pygame.display.set_mode(self.WINDOW_SIZE_scaled, vsync = 1)
        self.start_BG=pygame.transform.scale(pygame.image.load('sprites/start_menu.jpg'),self.WINDOW_SIZE)
        self.clock=pygame.time.Clock()
        self.gameover=False
        self.ESC=False
        self.click=False
        self.font=Read_files.Alphabet("Sprites/aseprite/Alphabet/Alphabet.png",2)#intitilise the alphabet class, scale of alphabet
        self.health_sprites = Read_files.Hearts_Black().get_sprites()
        self.state = ['start']

    def game_loop(self):
        while True:
            pass

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
        self.font.render(self.display,'Start Game',(200,100))
        start_rect=pygame.Rect(200,100,100,100)
        self.font.render(self.display,'Options',(200,200))
        option_rect=pygame.Rect(200,200,100,100)
        self.font.render(self.display,'Exit Game',(200,400))
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

        self.font.render(self.display,'Resolution',(200,100))
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.click=False
            self.state.append('resolution')

        self.input_quit()


    def resolution_menu(self):
        self.display.fill((207,238,250))#fill game.screen

        self.font.render(self.display,'1000x800',(200,100))
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.screen=pygame.display.set_mode((1000,800))
            #self.start_BG=pygame.transform.scale(self.start_BG,(1000,800))#recale the BG
            #self.screen.blit(self.start_BG,(0,0))

        self.input_quit()

    def exit(self):
        pygame.quit()
        sys.exit()

    def blit_health(self, player):
        #this code is specific to using heart.png sprites
        sprite_dim = [9,8] #width, height specific to sprites used
        blit_surface = pygame.Surface((int(player.max_health/20)*(sprite_dim[0] + 1),sprite_dim[1]),pygame.SRCALPHA,32)
        health = player.health

        for i in range(int(player.max_health/20)):
            health -= 20
            if health >= 0:
                blit_surface.blit(self.health_sprites[0],(i*(sprite_dim[0] + 1),0))
            elif health > -20:
                blit_surface.blit(self.health_sprites[-(health//4)],(i*(sprite_dim[0] + 1),0))
            else:
                blit_surface.blit(self.health_sprites[5],(i*(sprite_dim[0] + 1),0))

        return blit_surface

    def blit_fps(self):

        fps_string = str(int(self.clock.get_fps()))
        self.font.render(self.screen,fps_string,(400,20))

        #blit_surface = pygame.Surface((50,10),pygame.SRCALPHA,32)
        #fps_string = str(int(self.clock.get_fps()))
        #self.font.render(blit_surface,fps_string,(0,0))

        #return blit_surface

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

                if player_class.state!='talk':#if not in conversation

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


                    if event.key == pygame.K_LSHIFT:#left shift
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
