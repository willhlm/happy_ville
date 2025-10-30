import pygame, random
from pygame_render import RenderEngine

pygame.init()

screen_width, screen_height = 1280, 720
engine = RenderEngine(screen_width, screen_height)
bg_texture = engine.surface_to_texture(pygame.image.load('bg2.png'))
shader_blur = engine.load_shader_from_path('vertex.glsl', 'fragment_blur.glsl')
   
ref_screen = engine.make_layer((640,360))

positions = []
screens = []
layers_number = 10#change here to 0
for i in range(layers_number):
    screens.append(engine.make_layer((640,360)))
    positions.append([random.randint(0, 342),random.randint(0, 180)])

shader_blur['blurRadius'] = 1
blur_bg_texture = engine.make_layer(bg_texture.size)
engine.use_alpha_blending(False)#remove thr black outline
engine.render(bg_texture, blur_bg_texture, shader = shader_blur)
engine.use_alpha_blending(True)#remove thr black outline

clock = pygame.time.Clock()
running = True
while running:
    clock.tick()    
    ref_screen.clear(255, 255, 255, 255)#white to highlight the outlines

    if layers_number > 0:
                
        for screen in screens:#clear the layer screens
            screen.clear(0, 0, 0, 0)#make it whie to show the issue clearer
        
        for index, screen in enumerate(screens):#render a texture
            if index < 0.5 * layers_number:
                engine.use_alpha_blending(False)
                engine.render(blur_bg_texture.texture, screen, position = positions[index])
                engine.use_alpha_blending(True)
            else:
                engine.render(bg_texture, screen, position = positions[index])

        for screen in screens:#render to ref screen
            engine.render(screen.texture, ref_screen)

    else:
        #render directly to ref screen
        engine.render(blur_bg_texture.texture, ref_screen, position = (100,100))
    
    #final render
    engine.render(ref_screen.texture, engine.screen, scale=(3,3))

    pygame.display.flip()
    pygame.display.set_caption(f'FPS: {clock.get_fps():.2f}')

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
