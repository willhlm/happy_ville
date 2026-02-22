from time import time
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

# Instance data
num_sprites = 200000
rng = np.random.default_rng(42)
indices = np.arange(num_sprites)
positions = np.empty((num_sprites, 2))
positions[:, 0] = rng.uniform(0, width, size=num_sprites)
positions[:, 1] = rng.uniform(0, height, size=num_sprites)

# Load fragment shader by path; engine reads + compiles it.
shader_glow = engine.load_fragment_shader_from_path(
    "fragment_glow.glsl",
    instanced=True,
)

# Main game loop
running = True
total_time = 0

while running:
    # Tick the clock at 60 frames per second
    clock.tick()
    t0 = time()
    print(f"FPS: {clock.get_fps()}")

    # Clear the screen
    engine.clear(64, 128, 64)

    # Update the time
    total_time += clock.get_time()

    # Send time uniform to glow shader
    shader_glow["time"] = total_time

    # Render texture to screen
    sprite_scale = (16.0 * np.sin(indices * 0.1))
    scales = np.empty((num_sprites, 2))
    scales[:, 0] = sprite_scale
    scales[:, 1] = sprite_scale

    angles = (
        (total_time * np.sin(indices * 0.001)) * np.pi / 180.0
    ).reshape(-1, 1)

    base_tint = np.sin(indices * 0.1)
    tints = np.empty((num_sprites, 4))
    tints[:, 0] = base_tint
    tints[:, 1] = base_tint
    tints[:, 2] = base_tint
    tints[:, 3] = base_tint

    glow_strengths = np.sin(0.4 * indices + indices * 0.001).reshape(-1, 1)

    engine.render_batch_instanced(
        tex,
        engine.screen,
        positions=positions,
        scales=scales,
        angles=angles,
        shader=shader_glow,
        instance_attributes={
            "tint": tints,
            "glow": glow_strengths,
        },
    )

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
