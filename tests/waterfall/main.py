import pygame
from pygame_render import RenderEngine

pygame.init()

screen_width, screen_height = 1280, 720
engine = RenderEngine(screen_width, screen_height)
bg = pygame.image.load('bg2.png')
bg_texture = engine.surface_to_texture(bg)

shader_noise = engine.load_shader_from_path('vertex.glsl', 'fragment_perlin.glsl')
shader_noise2 = engine.load_shader_from_path('vertex.glsl', 'fragment_perlin.glsl')

bg_texture= engine.surface_to_texture(bg)

screen = engine.make_layer((640,360))
noise1 = engine.make_layer((640,360))
noise2 = engine.make_layer((640,360))
empty = engine.make_layer((640,360))
water = engine.make_layer((640,360))

shader_water = engine.load_shader_from_path('vertex.glsl', 'fragment_water.glsl')
shader_noise['u_resolution'] = (640,360)
shader_noise2['u_resolution'] = (640,360)


t = 0
clock = pygame.time.Clock()
running = True
while running:
    clock.tick()
    t += clock.get_time()
    screen.clear(0,0,0,255)

    engine.render(bg_texture,screen)

    shader_noise['u_time'] = t*0.001
    shader_noise['shift'] = [0,0]

    engine.render(empty.texture, noise1, shader=shader_noise)#make perlin noise
    engine.render(empty.texture, noise2, shader=shader_noise2)#make perlin noise

    shader_water['refraction_map'] = noise1.texture
    shader_water['water_mask'] = noise2.texture
    shader_water['SCREEN_TEXTURE'] = screen.texture#stuff to reflect
    shader_water['TIME'] = t*0.001

    engine.render(noise1.texture, screen,shader = shader_water)
    engine.render(screen.texture, engine.screen, scale = (2,2))

    pygame.display.flip()
    pygame.display.set_caption(f'FPS: {clock.get_fps():.2f}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
