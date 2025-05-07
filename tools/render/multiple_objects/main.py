import pygame
import math
from pygame_render import RenderEngine

pygame.init()
display_size = (800, 600)

engine = RenderEngine(display_size[0], display_size[1])
screen = engine.make_layer(display_size)
aila  = engine.load_texture('idle1.png')

running = True
while running:
    screen.clear(0, 0, 0, 0)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    position = (display_size[0] // 2, display_size[1] // 2)
    engine.render_objects(
        tex=aila,
        layer=screen,
        shader = None,
        instances=[
            {
                "pos": position,
                "scale": (1.0, 1.0),
                "rotation": 0.0,
                "custom": 0.0  # Can be used for anim param if needed
            }
        ]
    )

    engine.render(screen.texture, engine.screen)
    pygame.display.flip()

pygame.quit()
