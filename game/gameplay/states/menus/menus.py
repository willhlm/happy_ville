import pygame, sys
from gameplay.ui import ui_loader
from engine.utils import read_files
from gameplay.ui.elements import MenuArrow
from gameplay.states.base.game_state import GameState

class BaseUI(GameState):
    def __init__(self, game, **kwarg):
        super().__init__(game)
 
class Title_menu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = getattr(ui_loader, 'TitleMenu')(game.game_objects)
        self.play_music()
        self.image = self.menu_ui.sprites['idle'][0]
        self.current_button = 0
        self.update_arrow()

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def fade_update(self, dt):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.update_render(dt)

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.menu_ui.buttons[self.current_button].hoover()
        self.game.display.render(self.image, self.game.screen_manager.screen)#shader render

        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        #blit arrow
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)        

        self.game.render_display(self.game.screen_manager.screen.texture)

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0 or (event[-1] == 'dpad_up' and event[0]):#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0 or (event[-1] == 'dpad_down' and event[0]):#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] in ('return', 'a'):
                self.menu_ui.buttons[self.current_button].pressed()#if we want to make it e.g. glow or something
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def play_music(self):
        self.channel = self.game.game_objects.sound.play_priority_sound(self.menu_ui.sounds['main'][0], index = 0, loop = -1, fade = 700, vol = 0.3)
        self.channel = self.game.game_objects.sound.play_priority_sound(self.menu_ui.sounds['whisper'][0], index = 1, loop = -1, fade = 700, vol = 0.1)

    def change_state(self):
        if self.current_button == 0:#new game
            self.menu_ui.arrows[0].pressed('new')#if we want to make it e.g. glow or something
            self.game.state_manager.enter_state('Gameplay')

            #load new game level
            #self.game.game_objects.load_map(self,'village_ola2_1','1')
            #self.game.game_objects.load_map(self,'wakeup_forest_1','1')
            #self.game.game_objects.load_map(self,'crystal_mines_1','1')
            self.game.game_objects.load_map(self,'nordveden_1','1')
            #self.game.game_objects.load_map(self,'dark_forest_1','5')
            #self.game.game_objects.load_map(self,'tall_trees_2','1')
            #self.game.game_objects.load_map(self,'hlifblom_1','1')
            #self.game.game_objects.load_map(self,'rhoutta_encounter_1','1')
            #self.game.game_objects.load_map(self,'golden_fields_2','1')
            #self.game.game_objects.load_map(self,'collision_map_4','1')

        elif self.current_button == 1:
            self.menu_ui.arrows[0].pressed()
            self.game.state_manager.enter_state('Load_menu', category = 'menu')

        elif self.current_button == 2:
            self.menu_ui.arrows[0].pressed()
            self.game.state_manager.enter_state('Option_menu', category = 'menu')

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Load_menu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = getattr(ui_loader, 'LoadMenu')(game.game_objects)
        self.image = self.menu_ui.sprites['idle'][0]
        self.current_button = 0
        self.update_arrow()

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.game.display.render(self.image, self.game.screen_manager.screen)

        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)   

        #blit arrow
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.arrow.pressed()
                map, point = self.game.game_objects.load_game()#load saved game data
                self.game.state_manager.enter_state('Gameplay')
                self.game.game_objects.load_map(self, map, point)

class Option_menu(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.menu_ui = Option_menu.menu_ui
        self.image = self.menu_ui.sprites['idle'][0]
        self.current_button = 0
        self.update_arrow()

    def pool(game_objects):
        Option_menu.menu_ui = getattr(ui_loader, 'OptionMenu')(game_objects)

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def render(self):
        self.game.screen_manager.screen.clear(0,0,0,0)
        self.game.display.render(self.image, self.game.screen_manager.screen)

        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip)   

        #blit arrow
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] < 0:#up
            self.current_button -= 1
            if self.current_button < 0:
                self.current_button = len(self.menu_ui.buttons) - 1
            self.update_arrow()
        elif event[2]['l_stick'][1] > 0:#down
            self.current_button += 1
            if self.current_button >= len(self.menu_ui.buttons):
                self.current_button = 0
            self.update_arrow()
        elif event[0]:
            if event[-1] == 'start':
                self.game.state_manager.exit_state()
            elif event[-1] in ('return', 'a'):
                self.menu_ui.arrows[0].pressed()
                self.update_options()

    def update_options(self):
        if self.current_button == 0:#resolution
            self.game.state_manager.enter_state('Option_menu_display', category = 'menu')
        elif self.current_button == 1:#sounds
            self.game.state_manager.enter_state('Option_menu_sounds', category = 'menu')
        if self.current_button == 2:
            self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
        elif self.current_button == 3:
            self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

class Option_menu_sounds(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['overall', 'SFX','music']
        self.current_button = 0
        self.initiate_buttons()
        self.arrow = MenuArrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

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
            self.game.display.render(self.button_surfaces[b], self.game.screen_manager.screen, position = self.button_rects[b].topleft)

            volume_string = self.game.game_objects.font.render((30,12), str(self.game.game_objects.sound.volume[b]))
            self.game.game_objects.shaders['colour']['colour'] = (0,0,0,255)
            self.game.display.render(volume_string, self.game.screen_manager.screen, position = [self.button_rects[b].centerx + 10,self.button_rects[b].centery] ,shader = self.game.game_objects.shaders['colour'])#shader render
            volume_string.release()

    def render(self):
        #fill game.screen
        self.game.screen_manager.screen.clear(255,255,255, 255)

        #blit title
        self.game.display.render(self.title, self.game.screen_manager.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5, 50))

        #blit buttons
        self.blit_buttons()

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.game.screen_manager.screen, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])
        self.game.render_display(self.game.screen_manager.screen.texture)
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

class Option_menu_display(BaseUI):
    def __init__(self,game):
        super().__init__(game)
        self.title = self.game.game_objects.font.render(text = 'Resolution') #temporary
        self.game_settings = read_files.read_json('game_settings.json')

        #create buttons
        self.buttons = ['vsync', 'fullscreen','resolution']
        self.current_button = 0
        self.initiate_buttons()
        self.arrow = MenuArrow(self.button_rects[self.buttons[self.current_button]].topleft, game.game_objects)

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
            self.game.display.render(self.button_surfaces[b], self.game.screen_manager.screen, position = self.button_rects[b].topleft)

            settig_string = self.game.game_objects.font.render((60,12), str(self.game_settings['display'][b]))
            self.game.game_objects.shaders['colour']['colour'] = (0,0,0,255)
            self.game.display.render(settig_string, self.game.screen_manager.screen, position = [self.button_rects[b].centerx + 50,self.button_rects[b].centery] ,shader = self.game.game_objects.shaders['colour'])#shader render
            settig_string.release()

    def render(self):
        #fill game.screen
        self.game.screen_manager.screen.clear(255,255,255, 255)

        #blit title
        self.game.display.render(self.title, self.game.screen_manager.screen, position = (self.game.window_size[0]*0.5 - self.title.width*0.5, 50))

        #blit buttons
        self.blit_buttons()

        #blit arrow
        self.game.game_objects.shaders['colour']['colour'] = [0,0,0,255]
        self.game.display.render(self.arrow.image, self.game.screen_manager.screen, position = self.arrow.rect.topleft, shader = self.game.game_objects.shaders['colour'])
        self.game.render_display(self.game.screen_manager.screen.texture)
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

class Pause_menu(BaseUI):#when pressing ESC duing gameplay
    def __init__(self, game):
        super().__init__(game)
        self.menu_ui = getattr(ui_loader, 'PauseMenu')(game.game_objects)
        self.current_button = 0
        self.update_arrow()

        self.image = self.game.display.make_layer(self.game.display_size)
        self.game.game_objects.shaders['blur']['blurRadius'] = 1
        self.game.display.render(self.game.screen_manager.composite_screen.texture, self.image, shader = self.game.game_objects.shaders['blur'])

    def update_render(self, dt):
        for arrow in self.menu_ui.arrows:
            arrow.update(dt)#make them move back and forth

    def update_arrow(self):
        button = self.menu_ui.buttons[self.current_button]
        bx, by, bw, bh = button.rect

        for arrow in self.menu_ui.arrows:
            if arrow.flip:  
                arrow.set_pos((bx + bw + 10, by))  # +10 px padding
            else:# left arrow, align to left edge of button                
                arrow.set_pos((bx - arrow.rect.width - 10, by))  # -10 px padding
        arrow.play_SFX()

    def render(self):
        #blit buttons
        for b in self.menu_ui.buttons:
            self.game.display.render(b.image, self.game.screen_manager.screen, position = b.rect.topleft)

        #blit arrow
        for arrow in self.menu_ui.arrows:
            self.game.display.render(arrow.image, self.game.screen_manager.screen, position = arrow.true_pos, flip = arrow.flip) 
    
        self.game.render_display(self.image.texture, scale = False)
        self.game.render_display(self.game.screen_manager.screen.texture)        
     
    def handle_events(self, input):
        event = input.output()
        input.processed()
        if not input.key:#if it is a directinal input
            if event[2]['l_stick'][1] < 0:#up
                self.current_button -= 1
                if self.current_button < 0:
                    self.current_button = len(self.menu_ui.buttons) - 1
                self.update_arrow()
            elif event[2]['l_stick'][1] > 0:#down
                self.current_button += 1
                if self.current_button >= len(self.menu_ui.buttons):
                    self.current_button = 0
                self.update_arrow()
        if event[0]:
            if event[-1] in ['a', 'return']:
                self.menu_ui.arrows[0].pressed()
                self.change_state()
            elif event[-1] == 'start':
                self.game.state_manager.exit_state()

    def change_state(self):
        if self.current_button == 0:
            self.game.state_manager.exit_state()

        elif self.current_button == 1:
            self.game.state_manager.enter_state('Option_menu', category = 'menu')

        elif self.current_button == 2:#exit to main menu
            for state in self.game.state_manager.state_stack[1:]:#except the first one
                state.release_texture()
            self.game.state_manager.state_stack = [self.game.state_manager.state_stack[0]]
            self.game.state_manager.state_stack[-1].play_music()

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

