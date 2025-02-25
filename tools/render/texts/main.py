import sys
sys.path.insert(0, '/Users/olakenjiforslund/OKF/Leisure/Programming/Python/projects/pygame-render/src/') 

import pygame
from pygame_render import RenderEngine

pygame.init()
display_size = (800, 600)

engine = RenderEngine(display_size[0], display_size[1])

screen = engine.make_layer(display_size)
text_layer = engine.make_layer((400, 300))

running = True
time = 0
while running:
    screen.clear(0,0,0,0)
    text_layer.clear(0,0,0,0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    time += 0.01
   
    layer = engine.render_text(text_layer, 'hello world', letter_frame = int(time))
    engine.render(layer.texture, screen)
    engine.render(screen.texture, engine.screen) 
    pygame.display.flip()

pygame.quit()