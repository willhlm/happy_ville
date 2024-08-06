import pygame, sys, random
import Read_files
import entities_UI
import cutscene
import constants as C
import animation
import UI_select_menu, UI_facilities
import Entities
import particles

class Game_State():
    def __init__(self,game):
        self.game = game

    def update(self):
        pass

    def render(self):
        pass

    def handle_events(self,event):
        pass

    def enter_state(self):
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

    def release_texture(self):
        pass

class Title_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow(game.game_objects)
        self.title = self.game.game_objects.font.render(text = 'HAPPY VILLE')
        self.sprites = {'idle': Read_files.load_sprites_list('Sprites/UI/load_screen/new_game',game.game_objects)}
        self.image = self.sprites['idle'][0]
        self.animation = animation.Animation(self)

        #create buttons        
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def initiate_buttons(self):
        buttons = ['NEW GAME','LOAD GAME','OPTIONS','QUIT']
        self.buttons = []
        y_pos = 200
        for b in buttons:
            text = (self.game.game_objects.font.render(text = b))
            self.buttons.append(entities_UI.Button(self.game.game_objects, image = text, position = [100,y_pos]))
            y_pos += 20

    def define_BG(self):
        size = (90,100)
        bg = pygame.Surface(size, pygame.SRCALPHA,32).convert_alpha()
        pygame.draw.rect(bg,[200,200,200,100],(0,0,size[0],size[1]),border_radius=10)
        self.bg = self.game.display.surface_to_texture(bg)

    def reset_timer(self):
        pass

    def update(self):#update menu arrow position
        self.animation.update()
        ref_pos = self.buttons[self.current_button].rect.topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        self.game.display.render(self.image, self.game.screen)#shader render

        #blit title
        self.game.display.render(self.title, self.game.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5,50))
        self.game.display.render(self.bg, self.game.screen, position = (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.display.render(b.image, self.game.screen, position = b.rect.topleft)

        #blit arrow
        self.game.display.render(self.arrow.image, self.game.screen, position = self.arrow.rect.topleft)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] in ('return', 'a'):
                self.arrow.pressed()#if we want to make it e.g. glow or something
                self.buttons[self.current_button].pressed()#if we want to make it e.g. glow or something
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def change_state(self):
        if self.current_button == 0:#new game
            new_state = Gameplay(self.game)
            new_state.enter_state()

            #load new game level
            #self.game.game_objects.load_map(self,'light_forest_cave_10','1')
            self.game.game_objects.load_map(self,'village_ola2_5','1')

        elif self.current_button == 1:
            new_state = Load_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 2:
            new_state = Option_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Load_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow(game.game_objects)
        self.title = self.game.game_objects.font.render(text = 'LOAD GAME') #temporary
        self.sprites = {'idle': Read_files.load_sprites_list('Sprites/UI/load_screen/new_game',game.game_objects)}
        self.image = self.sprites['idle'][0]
        self.animation = animation.Animation(self)

        #create buttons
        self.buttons = ['SLOT 1','SLOT 2','SLOT 3','SLOT 4']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (90,100)
        bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(bg,[200,200,200,100],(0,0,size[0],size[1]),border_radius=10)
        self.bg = self.game.display.surface_to_texture(bg)

    def reset_timer(self):
        pass

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.display.render(self.image, self.game.screen)

        #blit title
        self.game.display.render(self.title, self.game.screen, position = (self.game.window_size[0]/2 - self.title.width/2,50))
        self.game.display.render(self.bg, self.game.screen, position = (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.game.screen, position = self.button_rects[b].topleft)

        #blit arrow
        #self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] == 'start':
                self.exit_state()
            elif event[-1] in ('return', 'a'):
                self.game.game_objects.load_game()#load saved game data

                new_state = Gameplay(self.game)
                new_state.enter_state()
                map = self.game.game_objects.player.spawn_point['map']
                point=self.game.game_objects.player.spawn_point['point']
                self.game.game_objects.load_map(self,map,point)

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].size)
            y_pos += 20

class Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow(game.game_objects)
        self.title = self.game.game_objects.font.render(text = 'OPTIONS') #temporary

        #create buttons
        self.buttons = ['Display','Sounds']
        if self.game.DEBUG_MODE:
            self.buttons += ['Render FPS', 'Render Hitboxes']
        self.current_button = 0
        self.initiate_buttons()

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.clear(255,255,255)

        #blit title
        self.game.display.render(self.title, self.game.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5,50))

        #blit buttons
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.game.screen, position = self.button_rects[b].topleft)

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.game.screen, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])

        #self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] == 'start':
                self.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options()

    def update_options(self):
        if self.current_button == 0:#resolution
            new_state = Option_Menu_display(self.game)
            new_state.enter_state()
        elif self.current_button == 1:#sounds
            new_state = Option_Menu_sounds(self.game)
            new_state.enter_state()
        if self.current_button == 2:
            self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
        elif self.current_button == 3:
            self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

class Option_Menu_sounds(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow(game.game_objects)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = Read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['overall', 'SFX','music']
        self.current_button = 0
        self.initiate_buttons()

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def blit_buttons(self):
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.game.screen, position = self.button_rects[b].topleft)

            volume_string = self.game.game_objects.font.render((30,12), str(self.game.game_objects.sound.volume[b]))
            self.game.game_objects.shaders['colour']['colour'] = (0,0,0,255)
            self.game.display.render(volume_string, self.game.screen, position = [self.button_rects[b].centerx + 10,self.button_rects[b].centery] ,shader = self.game.game_objects.shaders['colour'])#shader render
            volume_string.release()

    def render(self):
        #fill game.screen
        self.game.screen.clear(255,255,255)

        #blit title
        self.game.display.render(self.title, self.game.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5, 50))

        #blit buttons
        self.blit_buttons()

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.game.screen, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])

        #self.arrow.draw(self.game.screen)

    def exit_state(self):
        super().exit_state()
        self.game_settings['sounds'] = self.game.game_objects.sound.volume
        Read_files.write_json(self.game_settings, 'game_settings.json')#overwrite

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                self.current_button =  max(self.current_button, 0)
            elif event[-1] == 'down':
                self.current_button += 1
                self.current_button = min(self.current_button, len(self.buttons) - 1)
            elif event[-1] == 'start':
                self.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options(1)
            elif event[-1] in ('b'):
                self.update_options(-1)

    def update_options(self, int):
        if self.current_button == 0:#overall
            self.game.game_objects.sound.intensity_overall(int)
        if self.current_button == 1:#SFX
            self.game.game_objects.sound.intensity_SFX(int)
        elif self.current_button == 2:#music
            self.game.game_objects.sound.intensity_music(int)

class Option_Menu_display(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow(game.game_objects)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = Read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['vsync', 'fullscreen','resolution']
        self.current_button = 0
        self.initiate_buttons()

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def blit_buttons(self):
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.game.screen, position = self.button_rects[b].topleft)

            settig_string = self.game.game_objects.font.render((60,12), str(self.game_settings['display'][b]))
            self.game.game_objects.shaders['colour']['colour'] = (0,0,0,255)
            self.game.display.render(settig_string, self.game.screen, position = [self.button_rects[b].centerx + 50,self.button_rects[b].centery] ,shader = self.game.game_objects.shaders['colour'])#shader render
            settig_string.release()

    def render(self):
        #fill game.screen
        self.game.screen.clear(255,255,255)

        #blit title
        self.game.display.render(self.title, self.game.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5, 50))

        #blit buttons
        self.blit_buttons()

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.game.screen, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])

        #self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                self.current_button =  max(self.current_button, 0)
            elif event[-1] == 'down':
                self.current_button += 1
                self.current_button = min(self.current_button, len(self.buttons) - 1)
            elif event[-1] == 'start':
                self.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options(1)
            elif event[-1] in ('b'):
                self.update_options(-1)

    def exit_state(self):
        super().exit_state()
        Read_files.write_json(self.game_settings, 'game_settings.json')#overwrite

    def update_options(self, int):
        if self.current_button == 0:#vsync
            self.game_settings['display']['vsync'] = not self.game_settings['display']['vsync']
        if self.current_button == 1:#fullsceren
            self.game_settings['display']['fullscreen'] = not self.game_settings['display']['fullscreen']
        elif self.current_button == 2:#resolution
            pass

class Gameplay(Game_State):
    def __init__(self, game):
        super().__init__(game)

    def update(self):
        self.game.game_objects.update()
        self.game.game_objects.collide_all()
        self.game.game_objects.UI['gameplay'].update()

    def render(self):
        self.game.game_objects.render_state.render()#handles normal and portal rendering
        self.game.game_objects.UI['gameplay'].render()
        if self.game.RENDER_FPS_FLAG:
            self.blit_fps()

    def blit_fps(self):
        fps_string = str(int(self.game.clock.get_fps()))
        image = self.game.game_objects.font.render((30,12),'fps ' + fps_string)
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game.display.render(image, self.game.screen, position = (self.game.window_size[0]-40,20),shader = self.game.game_objects.shaders['colour'])#shader render
        image.release()

    def handle_events(self, input):
        self.game.game_objects.player.currentstate.handle_movement(input)#move around
        if input[0]:#press
            if input[-1]=='start':#escape button
                new_state = Pause_Menu(self.game)
                new_state.enter_state()

            elif input[-1]=='rb':
                new_state = Ability_menu(self.game)
                new_state.enter_state()

            elif input[-1] == 'y':
                self.game.game_objects.collisions.check_interaction_collision()

            elif input[-1] == 'select':
                new_state = Select_menu(self.game)
                new_state.enter_state()

            elif input[-1] == 'down':
                self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

            else:
                self.game.game_objects.player.currentstate.handle_press_input(input)
                self.game.game_objects.player.abilities.handle_input(input)#to change movement ability with d pad
                #self.game.game_objects.player.omamoris.handle_input(input)
        elif input[1]:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)

        elif input[2]['l_stick'][1] > 0.85:
            self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

class Pause_Menu(Gameplay):#when pressing ESC duing gameplay
    def __init__(self, game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow(game.game_objects)
        self.title = self.game.game_objects.font.render(text = 'Pause menu') #temporary
        #create buttons
        self.buttons = ['RESUME','OPTIONS','QUIT TO MAIN MENU','QUIT GAME']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (100,120)
        bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(bg,[200,200,200,100],(0,0,size[0],size[1]),border_radius=10)
        self.bg = self.game.display.surface_to_texture(bg)
        self.background = self.game.display.make_layer(self.game.window_size)#make a layer ("surface")
        self.background.clear(50,50,50,100)

    def initiate_buttons(self):
        y_pos = 140
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update(self):
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        super().render()
        self.game.display.render(self.bg, self.background, position = (self.game.window_size[0]/2 - self.bg.width/2,100))#shader render

        #blit title
        self.game.display.render(self.title, self.background, position = (self.game.window_size[0]/2 - self.title.width/2,110))#shader render

        #blit buttons
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.background, position = self.button_rects[b].topleft)#shader render

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.background, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])

        self.game.display.render(self.background.texture, self.game.screen)#shader render

    def release_texture(self):
        self.title.release()
        self.bg.release()
        self.background.release()
        self.arrow.image.release()
        for key in self.button_surfaces.keys():
            self.button_surfaces[key].release()

    def handle_events(self, event):
        if event[0]:
            if event[-1] == 'up':
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
            elif event[-1] == 'down':
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
            elif event[-1] in ('return', 'a'):
                self.change_state()
            elif event[-1] == 'start':
                self.exit_state()

    def exit_state(self):
        super().exit_state()
        self.release_texture()

    def change_state(self):
        if self.current_button == 0:
            self.exit_state()

        elif self.current_button == 1:
            new_state = Option_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 2:#exit to main menu
            for state in self.game.state_stack[1:]:#except the first one
                state.release_texture()
            self.game.state_stack = [self.game.state_stack[0]]

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Pause_gameplay(Gameplay):#a pause screen with optional shake. = when enteties takes dmg
    def __init__(self,game, **kwarg):
        super().__init__(game)
        self.duration = kwarg.get('duration', 12)
        amp = kwarg.get('amplitude', 0)
        scale = kwarg.get('scale', 0.9)
        self.game.game_objects.camera.camera_shake(amplitude = amp, duration = self.duration, scale = scale)

    def update(self):
        self.game.game_objects.camera_blocks.update()#need to be before camera: caemras stop needs tobe calculated before the scroll
        self.game.game_objects.camera.update()#need to be before camera: caemras stop needs tobe calculated before the scroll

        self.duration -= self.game.dt
        if self.duration < 0:
            self.exit_state()

    def render(self):
        self.game.state_stack[-2].render()

class Slow_gameplay(Gameplay):#called from aila when heal < 0
    def __init__(self, game, **kwarg):
        super().__init__(game)
        self.rate = kwarg.get('rate', 0.5)#determines the rate of slow motion, between 0 and 1
        self.duration = kwarg.get('duration', 100)

    def update(self):
        self.duration -= self.game.dt
        self.game.dt *= self.rate#slow motion
        super().update()
        self.exit()

    def exit(self):
        if self.duration < 0:
            self.exit_state()

class Slow_motion_gameplay(Slow_gameplay):#called from aila ability
    def __init__(self, game, **kwarg):
        super().__init__(game, **kwarg)
        self.bar = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites['bar'][0]
        self.meter = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites['meter'][0]
        self.width = self.meter.width

        self.pos = [self.game.window_size[0]*0.5 - self.width*0.5,3]
        self.bar_rate =self.width/self.duration

        self.surface = self.game.display.make_layer(self.game.window_size)#TODO

    def render(self):
        super().render()
        self.surface.clear(20,20,20,100)
        self.game.display.render(self.surface.texture, self.game.screen)

        self.width -= self.game.dt*self.bar_rate
        self.width = max(self.width,0)

    def exit_state(self):
        super().exit_state()
        self.game.game_objects.player.slow_motion = 1

class Ability_menu(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.abilities = list(self.game.game_objects.player.abilities.spirit_abilities.keys())
        self.index = self.abilities.index(self.game.game_objects.player.abilities.equip)

        self.sprites = Read_files.load_sprites_list('Sprites/UI/ability_HUD/',game.game_objects)#TODO
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]
        self.surface = self.game.display.make_layer(self.game.window_size)#TODO
        print(self.sprites)

    def update(self):
        self.game.dt *= 0.5#slow motion
        super().update()

    def render(self):
        super().render()
        self.surface.clear(20,20,20,100)

        self.game.display.render(self.surface.texture, self.game.screen)

        hud=self.sprites[self.index]
        for index,ability in enumerate(self.abilities):
            pos = [self.coordinates[index][0] + 250, self.coordinates[index][1] + 100]
            self.game.display.render(self.game.game_objects.player.abilities.spirit_abilities[ability].sprites['active_1'][0], self.game.screen,position =pos)

        self.game.display.render(hud, self.game.screen,position = (250,100))

    def handle_events(self, input):
        if input[0]:#press
            if input[-1] == 'right':
                self.index+=1
                if self.index>len(self.abilities)-1:
                    self.index=0
            elif input[-1] =='left':
                self.index-=1
                if self.index<0:
                    self.index=len(self.abilities)-1
        elif input [1]:#release
            if input[-1]=='rb':
                self.game.game_objects.player.abilities.equip=self.abilities[self.index]
                self.exit_state()

class Fadein(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.count = 0
        self.fade_length = 20
        self.init()
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)

    def init(self):
        self.aila_state = 'Idle_main'
        for state in self.game.state_stack:
            if 'Death' == type(state).__name__:
                self.aila_state = 'Invisible_main'
                self.game.game_objects.player.currentstate.enter_state('Invisible_main')
                break

    def update(self):
        self.game.game_objects.update()
        self.game.game_objects.platform_collision()
        self.game.game_objects.UI['gameplay'].update()

        self.count += self.game.dt
        if self.count > self.fade_length*2:
            self.exit()

    def exit(self):
        self.game.game_objects.load_bg_music()
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.currentstate.enter_state(self.aila_state)
        self.fade_surface.release()
        self.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

    def handle_events(self, input):
        pass

class Fadeout(Fadein):
    def __init__(self,game, previous_state, map_name, spawn, fade):
        super().__init__(game)
        self.previous_state = previous_state
        self.fade_length = 60
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))
        self.map_name = map_name
        self.spawn = spawn
        self.fade = fade

    def init(self):
        pass

    def update(self):
        self.previous_state.update()
        self.count += self.game.dt
        if self.count > self.fade_length:
            self.exit()

    def exit(self):
        self.fade_surface.release()
        self.exit_state()#has to be before loadmap
        self.game.game_objects.load_map2(self.map_name, self.spawn, self.fade)

    def render(self):
        self.previous_state.render()
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

class Safe_spawn_1(Gameplay):#fade
    def __init__(self, game):
        super().__init__(game)
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.count = 0
        self.fade_length = 60
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))

    def update(self):
        super().update()
        self.count += self.game.dt
        if self.count > self.fade_length:
            self.exit_state()
            new_state = Safe_spawn_2(self.game)
            new_state.enter_state()

    def render(self):
        super().render()#gameplay render
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

    def handle_events(self, input):
        pass

class Safe_spawn_2(Gameplay):#fade
    def __init__(self, game):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.count = 0
        self.fade_length = 20
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)
        self.game.game_objects.player.set_pos(self.game.game_objects.player.spawn_point['safe_spawn'])
        self.game.game_objects.player.currentstate.enter_state('Stand_up_main')

    def update(self):
        super().update()
        self.count += self.game.dt
        if self.count > self.fade_length*2:
            self.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

    def handle_events(self, input):
        pass

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.velocity = [0,0]
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_window_size = (352, 96)
        self.blit_pos = [int((self.game.window_size[0]-self.text_window_size[0])*0.5),50]
        self.background = self.game.display.make_layer(self.text_window_size)#make a layer ("surface")
        self.conv_screen = self.game.display.make_layer(self.game.window_size)#make a layer ("surface")

        self.clean_slate()
        self.conv = self.npc.dialogue.get_conversation()
        self.alpha = 10#alpha of the conversation screen
        self.sign = 1#fade in and back

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.game.game_objects.font.fill_text_bg(self.text_window_size)
        self.game.display.render(self.text_window, self.background)#shader render

    def update(self):
        super().update()
        self.letter_frame += self.print_frame_rate*self.game.dt
        self.alpha += self.sign * self.game.dt*5
        self.alpha = min(self.alpha,230)
        if self.alpha < 10:
            self.exit_state()

    def render(self):
        super().render()
        self.conv_screen.clear(10,10,10,100)#needed to make the self.background semi trasnaprant

        text = self.game.game_objects.font.render((272,80), self.conv, int(self.letter_frame))
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game.display.render(self.background.texture, self.conv_screen, position = self.blit_pos)#shader render
        self.game.display.render(text, self.conv_screen, position = (180,self.blit_pos[1] + 20), shader = self.game.game_objects.shaders['colour'])#shader render
        self.npc.render_potrait(self.conv_screen)#some conversation target may not have potraits

        self.game.game_objects.shaders['alpha']['alpha'] = self.alpha
        self.game.display.render(self.conv_screen.texture,self.game.screen,shader = self.game.game_objects.shaders['alpha'])#shader render

    def handle_events(self, input):
        if input[0]:
            if input[-1] == 'start':
                self.fade_back()

            elif input[-1] == 'y':
                if self.letter_frame < len(self.conv):
                    self.letter_frame = 10000

                else:#check if we have a series of conversations or not
                    self.npc.dialogue.increase_conv_index()
                    conv = self.npc.dialogue.get_conversation()
                    if not conv:
                        self.fade_back()
                    else:
                        self.clean_slate()
                        self.conv = conv

    def fade_back(self):
        self.sign = -1

    def exit_state(self):
        super().exit_state()
        self.conv_screen.release()
        self.background.release()
        self.npc.buisness()

class Select_menu(Gameplay):#pressing i: map, inventory, omamori, journal
    def __init__(self, game):
        super().__init__(game)
        self.screen = self.game.display.make_layer(self.game.window_size)#TODO
        self.shader = game.game_objects.shaders['alpha']
        self.state = [getattr(UI_select_menu, 'Inventory')(self)]#should it alway go to inventory be default?

    def update(self):
        super().update()
        self.state[-1].update()

    def render(self):
        super().render()
        self.state[-1].render()

    def handle_events(self,input):
        self.state[-1].handle_events(input)

class Facilities(Gameplay):#fast_travel (menu and unlock), ability upgrade (spurit and movement), bank, soul essence, vendor, smith
    def __init__(self, game,type,*arg):#args could be npc or travel point etc
        super().__init__(game)
        self.state = [getattr(UI_facilities, type)(self,*arg)]

    def update(self):
        super().update()
        self.state[-1].update()

    def render(self):
        super().render()
        self.state[-1].render()

    def handle_events(self,input):
        self.state[-1].handle_events(input)

class Cutscenes(Gameplay):
    def __init__(self, game,scene):
        super().__init__(game)
        self.current_scene = getattr(cutscene, scene)(self)#make an object based on string

    def update(self):
        self.current_scene.update()

    def render(self):
        self.current_scene.render()

    def handle_events(self, input):
        self.current_scene.handle_events(input)

class Blit_image_text(Gameplay):#when player obtaines a new ability, pick up inetractable item
    def __init__(self, game, img, text = ''):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]

        self.image = game.display.make_layer(img.size)#TODO
        self.game.display.render(img, self.image)#make a copy of the image
        self.text = self.game.game_objects.font.render((140,80), text)

        self.game.game_objects.player.reset_movement()

        self.surface = game.display.make_layer(game.window_size)#TODO
        self.fade = [0,0]

    def render(self):
        super().render()
        self.render_fade[self.page]()

        self.game.game_objects.shaders['alpha']['alpha'] = self.fade[1]
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,self.fade[1])

        self.surface.clear(40, 40, 40, self.fade[0])

        self.game.display.render(self.surface.texture, self.game.screen)
        self.game.display.render(self.image.texture, self.game.screen, position = (320, 120), shader = self.game.game_objects.shaders['alpha'])
        self.game.display.render(self.text, self.game.screen, position = (320,140), shader = self.game.game_objects.shaders['colour'])

    def render_in(self):
        self.fade[0] += 1
        self.fade[1] += 1
        self.fade[0] = min(self.fade[0],150)
        self.fade[1] = min(self.fade[1],255)

    def render_out(self):
        self.fade[0] -= 1
        self.fade[1] -= 1
        self.fade[0] = max(self.fade[0],0)
        self.fade[1] = max(self.fade[1],0)

        if self.fade[0] == 0:
            self.game.game_objects.player.currentstate.handle_input('Pray_post')#needed when picked up Interactable_item
            self.exit_state()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'start':
                self.page = 1
            elif input[-1] == 'a':
                self.page = 1

#encountters and corresponding cutscenes
class Cutscene_engine(Gameplay):#cut scenens that is based on game engien
    def __init__(self,game):
        super().__init__(game)
        self.timer = 0
        self.pos = [-self.game.window_size[1],self.game.window_size[1]]
        self.const = [0.8,0.8]#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.rect1 = game.display.make_layer(self.game.window_size)#TODO
        self.rect2 = game.display.make_layer(self.game.window_size)#TODO

        self.rect2.clear(0,0,0,255)
        self.rect1.clear(0,0,0,255)

    def render(self):
        super().render()
        self.cinematic()

    def cinematic(self):#black box stuff
        self.pos[0] += self.game.dt#the upper balck box
        self.pos[1] -= self.game.dt#the lower balck box

        self.pos[0] = min(-self.game.window_size[1]*self.const[0], self.pos[0])
        self.pos[1] = max(self.game.window_size[1]*self.const[1], self.pos[1])

        self.game.display.render(self.rect1.texture, self.game.screen, position = [0,self.pos[0]])
        self.game.display.render(self.rect2.texture, self.game.screen, position = [0,self.pos[1]])

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'start':
                self.exit_state()
            elif input[-1] == 'a':
                self.press = True

class New_game(Cutscene_engine):#first screen to be played when starying a new game -> needs to be called after that the map has loaded
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.camera.set_camera('New_game')#when starting a new game, should be a cutscene
        self.camera_stops = []#temporary remove the came stops
        for camera_stop in self.game.game_objects.camera_blocks:
            self.camera_stops.append(camera_stop)
        self.game.game_objects.camera_blocks.empty()

    def cinematic(self):
        pass

    def update(self):
        super().update()
        self.timer += self.game.dt
        if self.timer > 500:
            self.exit_state()

    def exit_state(self):
        for camera_stop in self.camera_stops:
            self.game.game_objects.camera_blocks.add(camera_stop)
        self.game.game_objects.camera.exit_state()
        super().exit_state()

class Title_screen(Cutscene_engine):#screen played after waking up from boss dream
    def __init__(self,game):
        super().__init__(game)
        self.title_name = self.game.game_objects.font.render(text = 'Happy Ville')
        self.text1 = self.game.game_objects.font.render(text = 'A game by Hjortron games')
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.cosmetics.empty()

    def update(self):
        super().update()
        self.timer += self.game.dt

    def render(self):
        super().render()
        if self.timer>250:
            self.game.display.render(self.title_name,self.game.screen,position = (190,150))

        if self.timer>500:
            self.game.display.render(self.text1,self.game.screen,position = (190,170))

        if self.timer >700:
            self.game.game_objects.player.acceleration[0] *= 2#bacl to normal speed
            self.exit_state()

    def handle_events(self,input):
        super().handle_events(input)
        if input[2]['l_stick'][0] > 0: return#can only go left
        input[2]['l_stick'][0] *= 0.5#half the speed
        self.game.game_objects.player.currentstate.handle_movement(input)

class Deer_encounter(Cutscene_engine):#first deer encounter in light forest by waterfall
    def __init__(self,game):
        super().__init__(game)
        spawn_pos=(2920,900)
        self.entity = Entities.Reindeer(spawn_pos, self.game.game_objects)
        self.entity.AI.deactivate()

        self.game.game_objects.enemies.add(self.entity)
        self.game.game_objects.camera.set_camera('Deer_encounter')
        self.game.game_objects.player.currentstate.enter_state('Walk_main')#should only enter these states once
        self.stage = 0

    def update(self):#write how you want things to act
        super().update()
        self.timer+=self.game.dt
        if self.stage == 0:

            if self.timer < 50:
                self.game.game_objects.player.velocity[0]=4

            elif self.timer>50:
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.game.game_objects.player.acceleration[0] = 0
                self.stage  = 1
                self.entity.dir[0] *= -1

        elif self.stage ==1:
            if self.timer > 100:
                self.entity.velocity[0] = 5

        if self.timer>200:
            self.exit_state()

    def exit_state(self):
        self.game.game_objects.camera.exit_state()
        self.entity.kill()
        super().exit_state()

class Boss_deer_encounter(Cutscene_engine):#boss fight cutscene
    def __init__(self,objects):
        super().__init__(objects)
        pos = (self.game.game_objects.camera.scroll[0] + 900,self.game.game_objects.camera.scroll[1] + 100)
        self.entity = Entities.Reindeer(pos, self.game.game_objects)#make the boss
        self.game.game_objects.enemies.add(self.entity)
        self.entity.dir[0]=-1
        self.game.game_objects.camera.set_camera('Deer_encounter')
        self.entity.AI.deactivate()
        self.stage = 0
        self.game.game_objects.player.currentstate.enter_state('Walk_main')
        self.game.game_objects.player.currentstate.walk()#to force tha walk animation

    def update(self):#write how you want the player/group to act
        super().update()
        self.timer += self.game.dt
        if self.stage == 0:
            self.game.game_objects.player.velocity[0]  = 4

            if self.timer >120:
                self.stage=1
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.game.game_objects.player.acceleration[0] = 0

        elif self.stage==1:
            if self.timer>200:
                self.entity.currentstate.enter_state('Transform')
                self.game.game_objects.player.velocity[0] = -20
                self.game.game_objects.camera.camera_shake(amp=3,duration=100)#amplitude, duration
                self.stage=2

        elif self.stage==2:
            if self.timer > 400:
                self.game.game_objects.camera.exit_state()#exsiting deer encounter camera
                self.entity.AI.activate()
                self.exit_state()

class Defeated_boss(Cutscene_engine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)
        self.step1 = False
        self.const = [0.5,0.5]#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once

    def update(self):
        super().update()
        self.timer+=self.game.dt
        if self.timer < 75:
            self.game.game_objects.player.velocity[1] = -2
        elif self.timer > 75:
            self.game.game_objects.player.velocity[1] = -1#compensates for gravity, levitates
            self.step1 = True

        if self.timer > 250:
            self.game.game_objects.player.velocity[1] = 2#go down again
            if self.game.game_objects.player.collision_types['bottom']:
                self.exit_state()

    def render(self):
        super().render()
        if self.step1:
            particle = getattr(particles, 'Spark')(self.game.game_objects.player.rect.center, self.game.game_objects, distance = 400, lifetime = 60, vel = {'linear':[7,13]}, dir = 'isotropic', scale = 1, colour = [255,255,255,255])
            self.game.game_objects.cosmetics.add(particle)

            self.game.game_objects.cosmetics.draw(self.game.game_objects.game.screen)
            self.game.game_objects.players.draw(self.game.game_objects.game.screen)

class Death(Cutscene_engine):#when aila dies
    def __init__(self,game):
        super().__init__(game)
        self.stage = 0

    def update(self):
        super().update()
        if self.game.state_stack[-1] != self: return
        self.timer += self.game.dt
        if self.stage == 0:

            if self.timer > 120:
                self.state1()

        elif self.stage == 1:
                #spawn effect
                pos = (0,0)#
                offset = 100#depends on the effect animation
                self.spawneffect = Entities.Spawneffect(pos,self.game.game_objects)
                self.spawneffect.rect.midbottom=self.game.game_objects.player.rect.midbottom
                self.spawneffect.rect.bottom += offset
                self.game.game_objects.cosmetics.add(self.spawneffect)
                self.stage = 2

        elif self.stage == 2:
            if self.spawneffect.finish:#when the cosmetic effetc finishes
                self.game.game_objects.player.currentstate.enter_state('Spawn_main')
                self.exit_state()

    def state1(self):
        if self.game.game_objects.player.spawn_point.get('bone', False):#respawn by bone
            map = self.game.game_objects.player.spawn_point['bone']['map']
            point = self.game.game_objects.player.spawn_point['bone']['point']
            del self.game.game_objects.player.spawn_point['bone']
        else:#normal resawn
            map = self.game.game_objects.player.spawn_point['map']
            point =  self.game.game_objects.player.spawn_point['point']
        self.game.game_objects.load_map(self, map, point)
        self.stage = 1

    def handle_events(self,input):
        pass

    def cinematic(self):
        pass

class Cultist_encounter(Cutscene_engine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.player.death_state.handle_input('cultist_encounter')
        self.game.game_objects.quests_events.initiate_quest('cultist_encounter', kill = 2)
        quest = self.game.game_objects.quests_events.active_quests['cultist_encounter']

        #should entity stuff be in quest insted?
        spawn_pos1 = (self.game.game_objects.camera.scroll[0] - 300, self.game.game_objects.camera.scroll[1] + 100)
        spawn_pos2 = (self.game.game_objects.camera.scroll[0] + 50, self.game.game_objects.camera.scroll[1] + 100)
        self.entity1 = Entities.Cultist_warrior(spawn_pos1, self.game.game_objects, quest)#added to group in cutscene
        self.entity1.dir[0] *= -1
        self.entity1.AI.deactivate()
        self.game.game_objects.enemies.add(self.entity1)
        self.entity2 = Entities.Cultist_rogue(spawn_pos2, self.game.game_objects, quest)#added to group in cutscene
        ##

        self.stage = 0
        self.game.game_objects.camera.set_camera('Cultist_encounter')
        self.game.game_objects.player.currentstate.enter_state('Walk_main')#should only enter these states once
        self.game.game_objects.player.currentstate.walk()#to force tha walk animation

    def update(self):
        super().update()
        self.timer+=self.game.dt
        if self.stage==0:#encounter Cultist_warrior
            if self.timer<50:
                self.game.game_objects.player.velocity[0]=-4
                self.game.game_objects.player.acceleration[0]=1

            elif self.timer > 50:
                self.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                #self.game.game_objects.player.velocity[0]=0
                self.game.game_objects.player.acceleration[0]=0

                self.stage = 1

        elif self.stage == 1:
            if self.timer > 200:#sapawn cultist_rogue
                spawn_pos = self.game.game_objects.player.rect.topright
                self.entity2.AI.deactivate()
                self.entity2.dir[0] = -1
                self.entity2.currentstate.enter_state('Ambush_pre')
                self.game.game_objects.enemies.add(self.entity2)

                self.stage=2
                self.timer=0

        elif self.stage==2:
            if self.timer>100:
                self.exit_state()

    def exit_state(self):
        self.entity1.AI.activate()
        self.entity2.AI.activate()
        self.game.game_objects.camera.exit_state()
        super().exit_state()

class Rhoutta_encounter(Gameplay):#called from trigger before first rhoutta: shuold spawn lightning and a gap spawns, or something -> TODO make a cutsene
    def __init__(self, game):
        super().__init__(game)
        spawn_pos = (1520-40,416-336)#topleft position in tiled - 40 to spawn it behind aila
        lightning = Entities.Lighitning(spawn_pos,self.game.game_objects, parallax = [1,1], size = [64,336])
        effect = Entities.Spawneffect(spawn_pos,self.game.game_objects)
        effect.rect.midbottom = lightning.rect.midbottom
        self.game.game_objects.interactables.add(lightning)
        self.game.game_objects.cosmetics.add(effect)
        self.game.game_objects.weather.flash()

class Butterfly_encounter(Cutscene_engine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.stage = 0
        self.cocoon = self.game.game_objects.map.references['cocoon_boss']
        self.const[1] = 0.9

    def update(self):
        super().update()
        self.timer+=self.game.dt
        if self.stage ==0:#approch
            if self.timer<50:
                self.game.game_objects.player.velocity[0]=-4
                self.game.game_objects.player.acceleration[0] = 1

            elif self.timer > 50:#stay
                self.game.game_objects.player.currentstate.enter_state('Idle_main')
                self.game.game_objects.player.acceleration[0]=0
                self.stage = 1

        elif self.stage == 1:#aggro

            if self.timer > 200:
                self.game.game_objects.camera.camera_shake(duration = 200)
                self.stage = 2

        elif self.stage == 2:#spawn
            self.cocoon.particle_release()
            if self.timer > 400:
                self.game_objects.quests_events.initiate_quest('butterfly_encounter')
                self.exit_state()
