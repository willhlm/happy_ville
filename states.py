import pygame, sys
import Read_files

class Game_States():
    def __init__(self,game):
        self.font=Read_files.Alphabet("Sprites/UI/Alphabet/Alphabet.png")#intitilise the alphabet class, scale of alphabet
        self.game=game

    def update(self):
        pass

    def render(self,display):
        pass

    def handle_events(self,event):
        pass

    def enter_state(self):
        self.game.stack_states.append(self)

    def exit_state(self):
        self.game.stack_states.pop()

class Splash(Game_States):
    def __init__(self,game):
        super().__init__(game)
        self.time_active=0

    def update(self):
        self.time_active+=1
        if self.time_active>100:
            new_state=Start_menu(self.game)
            new_state.enter_state()

    def render(self,display):
        display.fill((255,255,255))#fill game.screen
        display.blit(self.font.render((50,50),'welcome screen'),(200,200))


class Menu(Game_States):
    def __init__(self,game):
        super().__init__(game)
        self.click=False

    def handle_events(self,event):#to exits between option menues
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type==pygame.MOUSEBUTTONDOWN:
            self.click=True
        if event.type==pygame.MOUSEBUTTONUP:
            self.click=False
        if event.type == pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:#escape button
                #self.display.fill((207,238,250))#fill game.screen
                #self.screen.blit(self.start_BG,(0,0))
                #self.display.blit(pygame.transform.scale(self.screen,self.WINDOW_SIZE_scaled),(0,0))
                if len(self.game.stack_states)!=1:
                    self.exit_state()
                else:
                    self.game.update_state(self,'Gameplay')
        elif event.type==pygame.JOYBUTTONDOWN:#press a botton
            if event.button==self.controller.bottons['start']:#escape button
                #self.display.fill((207,238,250))#fill game.screen
                if len(self.game.stack_states)!=1:
                    self.exit_state()
                else:
                    self.game.update_state(self,'Gameplay')

class Start_menu(Menu):
    def __init__(self,game):
        super().__init__(game)

    def update(self):
        start_rect=pygame.Rect(200,100,100,100)
        option_rect=pygame.Rect(200,200,100,100)
        exit_rect=pygame.Rect(200,400,100,100)

        if start_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.ESC=False
            self.click=False
        elif option_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.click=False
            new_state=Option_menu(self.game)
            new_state.enter_state()

        elif exit_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            pygame.quit()
            sys.exit()

    def render(self,display):
        display.fill((207,238,250))#fill game.screen

        display.blit(self.font.render((50,50),'Start Game'),(200,100))
        display.blit(self.font.render((50,50),'Options'),(200,200))
        display.blit(self.font.render((50,50),'Exit Game'),(200,400))


class Option_menu(Menu):
    def __init__(self,game):
        super().__init__(game)

    def update(self):
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.click=False
            new_state=Resolution_menu(self.game)
            new_state.enter_state()

    def render(self,display):
        display.fill((207,238,250))#fill game.screen
        display.blit(self.font.render((50,50),'Resolution'),(200,100))

class Resolution_menu(Menu):
    def __init__(self,game):
        super().__init__(game)

    def update(self):
        Resolution_rect=pygame.Rect(200,100,100,100)

        if Resolution_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
            self.screen=pygame.display.set_mode((1000,800))
            #self.start_BG=pygame.transform.scale(self.start_BG,(1000,800))#recale the BG
            #self.screen.blit(self.start_BG,(0,0))

    def render(self,display):
        display.fill((207,238,250))#fill game.screen
        display.blit(self.font.render((50,50),'1000x800'),(200,100))
