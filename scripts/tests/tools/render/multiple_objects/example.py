from time import time
from pathlib import Path
import pygame
from pygame_render import RenderEngine
import numpy as np

# Initialize pygame
pygame.init()

# Create a render engine
width, height = 1280, 720
engine = RenderEngine(width, height)

# Load texture
tex = engine.load_texture("sprite.png")

# Clock
clock = pygame.time.Clock()

num_sprites = 500

# Main game loop
running = True
total_time = 0
while running:
    # Tick the clock at 60 frames per second
    clock.tick()
    t0 = time()
    print(f"FPS: {clock.get_fps()}")

    # Clear the screen
    engine.clear(0,0,0)

    # Update the time
    total_time += clock.get_time()

    for i in range(num_sprites):
        engine.render(tex, engine.screen, shader = None)

    # Update the display
    pygame.display.flip()

    # Display mspt
    t = time()
    mspt = (t - t0) * 1000
    pygame.display.set_caption(
        f"Rendering {num_sprites} sprites at {mspt:.3f} ms per tick!"
    )

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
