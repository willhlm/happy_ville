import pygame, sys
import Read_files
import Engine

class Game_State():
    def __init__(self,game):
        self.font = Read_files.Alphabet("Sprites/UI/Alphabet/Alphabet.png")#intitilise the alphabet class, scale of alphabet
        self.game = game

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

class Title_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.time_active = 0
        self.initiate_buttons()

        #
        self.current_button = 0

    def update(self):
        self.time_active += 1
        if self.time_active > 300:
            new_state = Gameplay(self.game)
            new_state.enter_state()

    def render(self):
        self.game.screen.fill((255,255,255))#fill game.screen
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.new_game, self.rect_new_game.topleft)
        self.game.screen.blit(self.load_game, self.rect_load_game.topleft)
        self.game.screen.blit(self.options, self.rect_options.topleft)
        self.game.screen.blit(self.quit_game, self.rect_quit_game.topleft)

    def initiate_buttons(self):
        self.title = self.font.render(text = 'HAPPY VILLE')
        self.new_game = self.font.render(text = 'NEW GAME')
        self.load_game = self.font.render(text = 'LOAD GAME')
        self.options = self.font.render(text = 'OPTIONS')
        self.quit_game = self.font.render(text = 'QUIT')
        self.rect_new_game = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.new_game.get_width()/2, 90),self.new_game.get_size())
        self.rect_load_game = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.load_game.get_width()/2, 110),self.load_game.get_size())
        self.rect_options = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.options.get_width()/2, 130),self.options.get_size())
        self.rect_quit_game = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.quit_game.get_width()/2, 150),self.quit_game.get_size())

    def handle_events(self):

        if event


class Gameplay(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game.load_level()

    def update(self):
        pass

    def render(self):
        pass

    def handle_events():
        pass
