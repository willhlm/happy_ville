import pygame, random
from pygame_render import RenderEngine

pygame.init()

screen_width, screen_height = 640*2, 360*2
engine = RenderEngine(screen_width, screen_height)

#shaders
noise_shader = engine.load_shader_from_path('vertex_noise.glsl', 'fragment_perlin.glsl')
fog_shader = engine.load_shader_from_path('vertex_fog.glsl', 'fragment_fog.glsl')

#screens
ref_screen = engine.make_layer((640, 360))
noise_layer = engine.make_layer((640, 360))
fog_layer = engine.make_layer((640, 360))
empty_layer = engine.make_layer((640, 360))

positions = []
screens = []
layers_number = 10
for i in range(layers_number):
    screens.append(engine.make_layer((640,360)))
    positions.append([random.randint(0, 640),random.randint(0, 360)])

bg_texture = engine.surface_to_texture(pygame.image.load('bg2.png'))

clock = pygame.time.Clock()
time = 0
running = True
direct = False '''toggle this one'''
while running:
    clock.tick()    
    ref_screen.clear(255, 255, 255, 255)#white to highlight the outlines
    time += 1
    noise_shader['u_time'] = time * 0.001
    fog_shader['TIME'] = time*0.001

    if not direct:#render first to layer screens
        for index, screen in enumerate(screens):#clear the layer screens
            screen.clear(0, 0, 0, 0)#make it whie to show the issue clearer
            engine.render(bg_texture, screen, position = positions[index])

            #render fog on top each layer
            #engine.use_alpha_blending(False)  
            engine.render(empty_layer.texture, noise_layer, shader = noise_shader)#make noise textire              
            fog_shader['noise'] = noise_layer.texture            
            engine.render(empty_layer.texture, screen, shader = fog_shader)#render noise
            #engine.use_alpha_blending(True)

        for screen in screens:#render resulrs to ref screen at the end
            engine.render(screen.texture, ref_screen)
            
    else:#render eveyrhitng directly to ref screen   
        for index, screen in enumerate(screens):#clear the layer screens
            screen.clear(0, 0, 0, 0)#make it whie to show the issue clearer
            engine.render(bg_texture, ref_screen, position = positions[index])

            #render fog on top each layer
            #engine.use_alpha_blending(False)  
            engine.render(empty_layer.texture, noise_layer, shader = noise_shader)#make noise textire              
            fog_shader['noise'] = noise_layer.texture            
            engine.render(empty_layer.texture, ref_screen, shader = fog_shader)#render noise
            #engine.use_alpha_blending(True)        

    #final render
    engine.render(ref_screen.texture, engine.screen, scale=(2,2))
    pygame.display.flip()
    pygame.display.set_caption(f'FPS: {clock.get_fps():.2f}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
