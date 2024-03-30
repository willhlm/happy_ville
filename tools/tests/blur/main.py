import pygame
from pygame_render import RenderEngine

pygame.init()

screen_width, screen_height = 1280, 720
engine = RenderEngine(screen_width, screen_height)
bg = pygame.image.load('bg2.png')
bg_texture = engine.surface_to_texture(bg)

shader_blur = engine.load_shader_from_path('vertex.glsl', 'fragment_blur.glsl')

screen = engine.make_layer((640,360))
    
blur_init = False#change this one
if blur_init:    
    temp = engine.make_layer((640,360))
    shader_blur['blurRadius'] = 10
    engine.render(bg_texture,temp,shader = shader_blur)

t = 0
clock = pygame.time.Clock()
running = True
while running:
    clock.tick()
    t += clock.get_time()
    screen.clear(255,255,255,255)#make it whie to show the issue clearer
    
    if blur_init:#blur the saved texture
        engine.render(temp.texture,screen)
    else:#blur live
        shader_blur['blurRadius'] = 10
        engine.render(bg_texture, screen, shader = shader_blur)

    engine.render(screen.texture,engine.screen,scale=(2,2))

    pygame.display.flip()
    pygame.display.set_caption(f'FPS: {clock.get_fps():.2f}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
