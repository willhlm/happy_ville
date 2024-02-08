import pygame
from pygame_render import RenderEngine
import numpy as np
from noise import snoise2
pygame.init()

screen_width, screen_height = 1280, 720
engine = RenderEngine(screen_width, screen_height)
bg = pygame.image.load('bg2.png')


bg_texture= engine.surface_to_texture(bg)

screen = engine.make_layer((640,360))
water = engine.make_layer((640,360))

bg_colour = (0,0,255,255)

shader_water = engine.load_shader_from_path('vertex.glsl', 'fragment_water.glsl')
#shader_water['SCREEN_UV'] = (640,360)

def generate_noise_texture(width, height, scale, octaves=6, persistence=0.1, lacunarity=2, repeatx=1024, repeaty=1024, base=0):
    noise_texture = np.zeros((width, height), dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            value = snoise2(x / scale, y / scale, octaves, persistence=persistence, lacunarity=lacunarity, repeatx=repeatx, repeaty=repeaty, base=base)
            # Map values to [0, 255] and reduce contrast
            noise_texture[x][y] = int((value + 1) * 127.5 * 0.3)
    return noise_texture

noise_texture_data = generate_noise_texture(screen_width, screen_height, scale=50, persistence=0.1, lacunarity=2,repeatx=1024, repeaty=1024,base=0)
noise_texture_surface = pygame.surfarray.make_surface(noise_texture_data)
noise_texture= engine.surface_to_texture(noise_texture_surface)

noise_texture_data = generate_noise_texture(screen_width, screen_height, scale=100,persistence=0, lacunarity=1,repeatx=1024, repeaty=1024, base=4)
noise_texture_surface = pygame.surfarray.make_surface(noise_texture_data)
noise_texture2= engine.surface_to_texture(noise_texture_surface)

t = 0
clock = pygame.time.Clock()
running = True
while running:
    clock.tick()
    t += clock.get_time()
    engine.screen.clear(0,0,0,255)

    shader_water['noise_texture'] = noise_texture
    shader_water['SCREEN_TEXTURE'] = bg_texture
    shader_water['noise_texture2'] = noise_texture2
    shader_water['TIME'] = t*0.0001

    engine.render(water.texture, screen, shader=shader_water)
    engine.render(screen.texture, engine.screen, scale = (2,2))

    pygame.display.flip()
    pygame.display.set_caption(f'FPS: {clock.get_fps():.2f}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
