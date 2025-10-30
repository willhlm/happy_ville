import pygame
from engine.game import Game

if __name__ == '__main__':    
    pygame.mixer.pre_init(44100, -16, 2, 4096)# Optimize audio before pygame.init()
    pygame.init()
    
    pygame.display.set_caption("My Game")# Optionally set window title

    # Create game instance and run
    game = Game()
    game.run()