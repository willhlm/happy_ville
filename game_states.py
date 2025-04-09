import pygame, sys
import read_files
import entities_UI
import cutscene
import constants as C
import animation

class Game_State():
    def __init__(self,game):
        self.game = game

    def update(self):
        pass

    def render(self):
        pass

    def handle_events(self, input):
        input.processed()

    def on_exit(self):
        pass

    def on_resume(self):
        pass

    def release_texture(self):#in the final version, this should not be needed sinec we wil not dynamically make layers
        pass

class Title_menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.title = self.game.game_objects.font.render(text = 'HAPPY VILLE')
        self.sounds = read_files.load_sounds_dict('audio/music/load_screen/')
        self.play_music()

        self.sprites = {'idle': read_files.load_sprites_list('Sprites/UI/load_screen/start_screen',game.game_objects)}
        self.image = self.sprites['idle'][0]
        self.animation = animation.Animation(self)

        #create buttons
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()
        #self.arrow = entities_UI.Menu_Arrow(self.buttons[self.current_button].rect.topleft, game.game_objects)
        offset = [-10, -2]
        self.arrow = entities_UI.Menu_Arrow(self.buttons[self.current_button].rect.midleft, game.game_objects, offset = [-8, -1], animate = True)
        self.arrow_2 = entities_UI.Menu_Arrow(self.buttons[self.current_button].rect.midright, game.game_objects, offset = [-8, -1], mirrored = True, animate = True)

    def initiate_buttons(self):
        buttons = ['New game','Load game','Option','Quit']
        self.buttons = []
        y_pos = 200
        x_pos = 320
        for b in buttons:
            text = (self.game.game_objects.font.render(text = b))
            self.buttons.append(entities_UI.Button(self.game.game_objects, image = text, position = [x_pos, y_pos], center = True))
            y_pos += self.game.game_objects.font.get_height() + 3

    def define_BG(self):
        size = (90,100)
        bg = pygame.Surface(size, pygame.SRCALPHA,32).convert_alpha()
        pygame.draw.rect(bg,[200,200,200,150],(0,0,size[0],size[1]),border_radius=10)
        self.bg = self.game.display.surface_to_texture(bg)

    def reset_timer(self):
        pass

    def update(self):#update menu arrow position
        self.animation.update()
        self.arrow.animate()
        self.arrow_2.animate()

    def fade_update(self):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.update()

    def render(self):
        self.buttons[self.current_button].hoover()
        self.game.display.render(self.image, self.game.screen)#shader render

        #blit title
        self.game.display.render(self.title, self.game.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5,50))
        #self.game.display.render(self.bg, self.game.screen, position = (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.display.render(b.image, self.game.screen, position = b.rect.topleft)

        #blit arrow
        self.game.display.render(self.arrow.image, self.game.screen, position = self.arrow.rect.topleft)
        self.game.display.render(self.arrow_2.image, self.game.screen, position = self.arrow_2.rect.topleft, flip = True)

    def update_arrow(self):
        ref_pos = self.buttons[self.current_button].rect.midleft
        ref_pos2 = self.buttons[self.current_button].rect.midright
        self.arrow.update_pos((ref_pos[0], ref_pos[1]))
        self.arrow_2.update_pos((ref_pos2[0], ref_pos2[1]))
        self.arrow.play_SFX()

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] in ('return', 'a'):
                self.buttons[self.current_button].pressed()#if we want to make it e.g. glow or something
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def play_music(self):#called from e.g. exiting ganeplay state
        self.channel = self.game.game_objects.sound.play_priority_sound(self.sounds['main'][0], index = 0, loop = -1, fade = 700, vol = 0.3)
        self.channel = self.game.game_objects.sound.play_priority_sound(self.sounds['whisper'][0], index = 1, loop = -1, fade = 700, vol = 0.1)

    def change_state(self):
        if self.current_button == 0:#new game
            self.arrow.pressed('new')#if we want to make it e.g. glow or something
            self.game.state_manager.enter_state('Gameplay')

            #load new game level
            #self.game.game_objects.load_map(self,'village_ola2_1','1')
            #self.game.game_objects.load_map(self,'golden_fields_1','1')
            #self.game.game_objects.load_map(self,'crystal_mines_1','1')
            self.game.game_objects.load_map(self,'nordveden_1','1')
            #self.game.game_objects.load_map(self,'dark_forest_1','5')
            #self.game.game_objects.load_map(self,'light_forest_cave_6','1')
            #self.game.game_objects.load_map(self,'hlifblom_40','1')
            #self.game.game_objects.load_map(self,'rhoutta_encounter_1','1')
            #self.game.game_objects.load_map(self,'collision_map_4','1')

        elif self.current_button == 1:
            self.arrow.pressed()
            self.game.state_manager.enter_state('Load_menu')

        elif self.current_button == 2:
            self.arrow.pressed()
            self.game.state_manager.enter_state('Option_menu')

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Load_menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.title = self.game.game_objects.font.render(text = 'LOAD GAME') #temporary
        self.sprites = {'idle': read_files.load_sprites_list('Sprites/UI/load_screen/new_game',game.game_objects)}
        self.image = self.sprites['idle'][0]
        self.animation = animation.Animation(self)

        #create buttons
        self.buttons = ['SLOT 1','SLOT 2','SLOT 3','SLOT 4']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()
        self.arrow = entities_UI.Menu_Arrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

    def define_BG(self):
        size = (90,100)
        bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(bg,[200,200,200,100],(0,0,size[0],size[1]),border_radius=10)
        self.bg = self.game.display.surface_to_texture(bg)

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

    def reset_timer(self):
        pass

    def update(self):
        self.animation.update()

    def update_arrow(self):
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update_pos((ref_pos[0] - 10, ref_pos[1]))
        self.arrow.play_SFX()

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
        self.game.display.render(self.arrow.image, self.game.screen, position = self.arrow.rect.topleft)


    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.arrow.pressed()
                self.game.game_objects.load_game()#load saved game data
                self.game.state_manager.enter_state('Gameplay')

                map = self.game.game_objects.player.backpak.map.spawn_point['map']
                point=self.game.game_objects.player.backpak.map.spawn_point['point']
                self.game.game_objects.load_map(self, map, point)

class Option_menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Options', color = (0,0,0)) #temporary

        #create buttons
        self.buttons = ['Display','Sounds']
        if self.game.DEBUG_MODE:
            self.buttons += ['Render FPS', 'Render Hitboxes']
        self.current_button = 0
        self.initiate_buttons()
        self.arrow = entities_UI.Menu_Arrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b, color = (0,0,0)))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update_arrow(self):#update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update_pos((ref_pos[0] - 10, ref_pos[1]))
        self.arrow.play_SFX()

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

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.arrow.pressed()
                self.update_options()

    def update_options(self):
        if self.current_button == 0:#resolution
            self.game.state_manager.enter_state('Option_menu_display')
        elif self.current_button == 1:#sounds
            self.game.state_manager.enter_state('Option_menu_sounds')
        if self.current_button == 2:
            self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
        elif self.current_button == 3:
            self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

class Option_menu_sounds(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['overall', 'SFX','music']
        self.current_button = 0
        self.initiate_buttons()
        self.arrow = entities_UI.Menu_Arrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update_arrow(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update_pos((ref_pos[0] - 10, ref_pos[1]))
        self.arrow.play_SFX()

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

    def on_exit(self):
        super().on_exit()
        self.game_settings['sounds'] = self.game.game_objects.sound.volume
        read_files.write_json(self.game_settings, 'game_settings.json')#overwrite

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options(1)
            elif event[-1] in ('b'):
                self.update_options(-1)

    def update_options(self, int):
        if self.current_button == 0:#overall
            self.game.game_objects.sound.change_volume('overall', int)
        if self.current_button == 1:#SFX
            self.game.game_objects.sound.change_volume('SFX', int)
        elif self.current_button == 2:#music
            self.game.game_objects.sound.change_volume('music', int)

class Option_menu_display(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['vsync', 'fullscreen','resolution']
        self.current_button = 0
        self.initiate_buttons()
        self.arrow = entities_UI.Menu_Arrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].width/2 ,y_pos),self.button_surfaces[b].size)
            y_pos += 20

    def update_arrow(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update_pos((ref_pos[0] - 10, ref_pos[1]))
        self.arrow.play_SFX()

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

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.update_options(1)
            elif event[-1] in ('b'):
                self.update_options(-1)

    def on_exit(self):
        super().on_exit()
        read_files.write_json(self.game_settings, 'game_settings.json')#overwrite

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
        self.handle_movement()
        self.game.game_objects.time_manager.update()
        self.game.game_objects.update()
        self.game.game_objects.collide_all()
        self.game.game_objects.UI.hud.update()

    def fade_update(self):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.game.game_objects.update()
        self.game.game_objects.platform_collision()
        self.game.game_objects.UI.hud.update()

    def render(self):
        self.game.game_objects.render_state.render()#handles normal and special rendering (e.g. portal rendering)
        self.game.game_objects.UI.hud.render()
        if self.game.RENDER_FPS_FLAG:
            self.blit_fps()

    def blit_fps(self):
        fps_string = str(int(self.game.clock.get_fps()))
        image = self.game.game_objects.font.render((50,12),'fps ' + fps_string)
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game.display.render(image, self.game.screen, position = (self.game.window_size[0]-50,20),shader = self.game.game_objects.shaders['colour'])#shader render
        image.release()

    def handle_movement(self):#every frame
        #value = self.game.game_objects.controller.continuous_input_checks()
        value = self.game.game_objects.controller.value
        self.game.game_objects.player.currentstate.handle_movement(value)#move around
        self.game.game_objects.camera_manager.handle_movement(value)

    def handle_events(self, input):
        event = input.output()
        if event[0]:#press
            if event[-1]=='start':#escape button
                input.processed()
                self.game.state_manager.enter_state('Pause_menu')

            elif event[-1]=='rb':
                input.processed()
                self.game.state_manager.enter_state('Ability_menu')

            elif event[-1] == 'y':
                input.processed()
                self.game.game_objects.collisions.check_interaction_collision()

            elif event[-1] == 'select':
                input.processed()
                self.game.state_manager.enter_state('UIs', page = 'backpack')

            elif event[-1] == 'down':
                input.processed()#should it be processed here or when passed through?
                self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

            elif sum(event[2]['d_pad']) != 0:#d_pad was pressed
                input.processed()
                self.game.game_objects.player.abilities.handle_input(event[2]['d_pad'])#to change movement ability with d pad

            else:
                self.game.game_objects.player.currentstate.handle_press_input(input)
                #self.game.game_objects.player.omamoris.handle_press_input(input)
        elif event[1]:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)

        elif event[2]['l_stick'][1] > 0.85:
            input.processed()#should it be processed here or when passed through?
            self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

class Pause_menu(Gameplay):#when pressing ESC duing gameplay
    def __init__(self, game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Pause menu') #TODO

        #create buttons
        self.buttons = ['Resume','Options','Quit to main menu','Quit game']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()
        self.arrow = entities_UI.Menu_Arrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

        self.screen_copy = self.game.display.make_layer(self.game.window_size)

    def define_BG(self):
        size = (100,120)
        bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()
        pygame.draw.rect(bg,[200,200,200,220],(0,0,size[0],size[1]),border_radius=10)
        self.bg = self.game.display.surface_to_texture(bg)
        self.background = self.game.display.make_layer(self.game.window_size)

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

    def update_arrow(self):
        pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update_pos(pos)
        self.arrow.play_SFX()

    def update(self):
        pass

    def render(self):
        super().render()
        self.background.clear(50,50,50,30)
        self.game.game_objects.shaders['blur']['blurRadius'] = 0.1
        self.game.display.render(self.game.screen.texture, self.screen_copy, shader = self.game.game_objects.shaders['blur'])#blur screen
        self.game.display.render(self.bg, self.background, position = (self.game.window_size[0]*0.5 - self.bg.width*0.5,100))#shader render

        #blit title
        self.game.display.render(self.title, self.background, position = (self.game.window_size[0]*0.5 - self.title.width*0.5,110))#shader render

        #blit buttons
        for b in self.buttons:
            self.game.display.render(self.button_surfaces[b], self.background, position = self.button_rects[b].topleft)#shader render

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.background, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])

        self.game.display.render(self.screen_copy.texture, self.game.screen)#shader render
        self.game.display.render(self.background.texture, self.game.screen)#shader render

    def release_texture(self):
        self.title.release()
        self.bg.release()
        self.background.release()
        self.screen_copy.release()
        for key in self.button_surfaces.keys():
            self.button_surfaces[key].release()

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if not input.key:#if it is a directinal input
            if event[2]['l_stick'][1] < 0:#up
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.buttons) - 1
                self.update_arrow()
            elif event[2]['l_stick'][1] > 0:#down
                self.current_button += 1
                if self.current_button >= len(self.buttons):
                    self.current_button = 0
                self.update_arrow()
        if event[0]:
            if event[-1] in ['a', 'return']:
                self.arrow.pressed()
                self.change_state()
            elif event[-1] == 'start':
                self.game.state_manager.exit_state()

    def on_exit(self):
        self.release_texture()

    def change_state(self):
        if self.current_button == 0:
            self.game.state_manager.exit_state()

        elif self.current_button == 1:
            self.game.state_manager.enter_state('Option_menu')

        elif self.current_button == 2:#exit to main menu
            for state in self.game.state_manager.state_stack[1:]:#except the first one
                state.release_texture()
            self.game.state_manager.state_stack = [self.game.state_manager.state_stack[0]]
            self.game.state_manager.state_stack[-1].play_music()

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Ability_menu(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.abilities = list(self.game.game_objects.player.abilities.spirit_abilities.keys())
        self.index = self.abilities.index(self.game.game_objects.player.abilities.equip)

        self.sprites = read_files.load_sprites_list('Sprites/UI/ability_HUD/', game.game_objects)#TODO
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]
        self.surface = self.game.display.make_layer(self.game.window_size)#TODO

    def update(self):
        self.game.dt *= 0.5#slow motion
        super().update()

    def render(self):
        super().render()
        self.surface.clear(20,20,20,100)
        self.game.display.render(self.surface.texture, self.game.screen)

        hud=self.sprites[self.index]
        for index, ability in enumerate(self.abilities):
            pos = [self.coordinates[index][0] + 250, self.coordinates[index][1] + 100]
            self.game.display.render(self.game.game_objects.player.abilities.spirit_abilities[ability].sprites['active_1'][0], self.game.screen,position =pos)

        self.game.display.render(hud, self.game.screen,position = (250,100))

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] > 0:#dwpn
            self.index += 1
            if self.index > len(self.abilities)-1:
                self.index = 0
        elif event[2]['l_stick'][1] < 0:#up
            self.index-=1
            if self.index<0:
                self.index=len(self.abilities)-1
        elif event [1]:#release
            if event[-1]=='rb':
                self.game.game_objects.player.abilities.equip=self.abilities[self.index]
                self.game.state_manager.exit_state()

class Fadein(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.count = 0
        self.fade_length = 25
        self.init()
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)

    def init(self):
        self.aila_state = 'Idle_main'#for respawn after death
        for state in self.game.state_manager.state_stack:
            if 'Death' == type(state).__name__:
                self.aila_state = 'Invisible_main'
                self.game.game_objects.player.currentstate.enter_state('Invisible_main')
                break

    def update(self):
        self.fade_update()#so that it doesn't collide with collision path
        self.count += self.game.dt
        if self.count > self.fade_length*2:
            self.exit()

    def exit(self):
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.currentstate.enter_state(self.aila_state)
        self.fade_surface.release()
        self.game.state_manager.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

class Fadeout(Fadein):
    def __init__(self,game, previous_state, map_name, spawn, fade):
        super().__init__(game)
        self.previous_state = previous_state
        self.fade_length = 25
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))
        self.map_name = map_name
        self.spawn = spawn
        self.fade = fade

    def init(self):
        pass

    def update(self):
        self.previous_state.fade_update()#so that it don't consider player input
        self.count += self.game.dt
        if self.count > self.fade_length:
            self.exit()

    def exit(self):
        self.fade_surface.release()
        self.game.state_manager.exit_state()#has to be before loadmap
        self.game.game_objects.load_map2(self.map_name, self.spawn, self.fade)

    def render(self):
        self.previous_state.render()
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

class Safe_spawn_1(Gameplay):#basically fade. Uses it when collising a hole
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
            self.game.state_manager.exit_state()
            self.game.state_manager.enter_state('Safe_spawn_2')

    def render(self):
        super().render()#gameplay render
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

class Safe_spawn_2(Gameplay):#fade
    def __init__(self, game):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.count = 0
        self.fade_length = 20
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)
        self.game.game_objects.player.set_pos(self.game.game_objects.player.backpack.map.spawn_point['safe_spawn'])
        self.game.game_objects.player.currentstate.enter_state('Stand_up_main')

    def update(self):
        super().update()
        self.count += self.game.dt
        if self.count > self.fade_length*2:
            self.game.state_manager.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.display.render(self.fade_surface.texture, self.game.screen)#shader render

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.velocity = [0,0]
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_window_size = (528, 160)
        self.blit_pos = [int((self.game.window_size[0]-self.text_window_size[0])*0.5),50]
        self.background = self.game.display.make_layer(self.text_window_size)#TODO
        self.conv_screen = self.game.display.make_layer(self.game.window_size)#TODO

        self.clean_slate()
        self.conv = self.npc.dialogue.get_conversation()
        self.alpha = 10#alpha of the conversation screen
        self.sign = 1#fade in and back

    def clean_slate(self):
        self.letter_frame = 0
        #self.text_window = self.game.game_objects.font.fill_text_bg(self.text_window_size)
        self.text_window = pygame.image.load('Sprites/utils/text_box3.png').convert_alpha()
        self.text_window = self.game.display.surface_to_texture(self.text_window)
        self.text_win_size = self.text_window.size
        print(self.text_win_size)
        self.game.display.render(self.text_window, self.background)#shader render

    def update(self):
        super().update()
        self.letter_frame += self.print_frame_rate*self.game.dt
        self.alpha += self.sign * self.game.dt*5
        self.alpha = min(self.alpha,230)
        if self.alpha < 10:
            self.game.state_manager.exit_state()

    def render(self):
        super().render()
        self.conv_screen.clear(10,10,10,100)#needed to make the self.background semi trasnaprant
        self.background.clear(10,10,10,0)#needed to make the self.background semi trasnaprant

        self.game.display.render(self.text_window, self.background)#shader render

        text = self.game.game_objects.font.render((272,80), self.conv, int(self.letter_frame))
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game.display.render(self.background.texture, self.conv_screen, position = self.blit_pos)#shader render
        self.game.display.render(text, self.background, position = (144,self.blit_pos[1] + 20), shader = self.game.game_objects.shaders['colour'])#shader render
        self.npc.render_potrait(self.background)#some conversation target may not have potraits
        text.release()
        self.game.game_objects.shaders['alpha']['alpha'] = self.alpha
        self.game.display.render(self.background.texture,self.conv_screen,position = [(640 - self.text_win_size[0])/2, 50],shader = self.game.game_objects.shaders['alpha'])
        self.game.display.render(self.conv_screen.texture,self.game.screen)#shader render

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[0]:
            if event[-1] == 'start':
                self.fade_back()

            elif event[-1] == 'y':
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

    def on_exit(self):
        self.conv_screen.release()
        self.background.release()
        self.npc.buisness()

class UIs(Gameplay):#pressing i: map, inventory, omamori, journal
    def __init__(self, game, page, **kwarg):
        super().__init__(game)
        self.game.game_objects.UI.set_ui(page, **kwarg)

    def update(self):
        super().update()
        self.game.game_objects.UI.update()

    def render(self):
        super().render()
        self.game.game_objects.UI.render()

    def handle_events(self,input):
        self.game.game_objects.UI.handle_events(input)

class Blit_image_text(Gameplay):#when player obtaines a new ability, pick up inetractable item etc. It blits an image and text
    def __init__(self, game, image, text = '', callback = None):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]

        self.image = game.display.make_layer(image.size)#TODO
        self.game.display.render(image, self.image)#make a copy of the image
        self.text = self.game.game_objects.font.render((140,80), text)

        self.game.game_objects.player.reset_movement()

        self.surface = game.display.make_layer(game.window_size)#TODO
        self.fade = [0,0]
        self.callback = callback#a function to call when exiting

    def handle_movement(self):#every frame
        pass

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
        self.fade[0] = max(self.fade[0], 0)
        self.fade[1] = max(self.fade[1], 0)

        if self.fade[0] == 0:
            if self.callback: self.callback()
            self.game.state_manager.exit_state()

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.page = 1
            elif event[-1] == 'a':
                self.page = 1
