import pygame, sys, random
import Read_files
import entities_UI
import cutscene
import constants as C
import animation
import UI_select_menu, UI_facilities
import Entities

class Game_State():
    def __init__(self,game):
        self.game = game

    def update(self):
        pass

    def render(self,display):
        pass

    def handle_events(self,event):
        pass

    def enter_state(self):
        self.game.state_stack.append(self)

    def exit_state(self):
        self.game.state_stack.pop()

class Title_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'HAPPY VILLE') #temporary
        self.sprites = Read_files.load_sprites('Sprites/UI/load_screen/new_game')
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

        #create buttons
        self.buttons = ['NEW GAME','LOAD GAME','OPTIONS','QUIT']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (90,100)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def reset_timer(self):
        pass

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        self.game.screen.fill((255,255,255))
        self.game.screen.blit(self.image, (0,0))

        #blit title
        self.game.screen.blit(self.title, (self.game.window_size[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.bg, (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

    def handle_events(self, event):
        #print(event)
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
                pygame.quit()
                sys.exit()

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color = (255,255,255), special_flags = pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def change_state(self):
        if self.current_button == 0:#new game
            new_state = Gameplay(self.game)
            new_state.enter_state()

            #load new game level
            self.game.game_objects.load_map(self,'rhoutta_encounter_1','1')

        elif self.current_button == 1:
            new_state = Load_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 2:
            new_state = Start_Option_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Load_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'LOAD GAME') #temporary
        self.sprites = Read_files.load_sprites('Sprites/UI/load_screen/new_game')
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

        #create buttons
        self.buttons = ['SLOT 1','SLOT 2','SLOT 3','SLOT 4']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (90,100)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def reset_timer(self):
        pass

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255))
        self.game.screen.blit(self.image, (0,0))

        #blit title
        self.game.screen.blit(self.title, (self.game.window_size[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.bg, (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

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
                map=self.game.game_objects.player.spawn_point['map']
                point=self.game.game_objects.player.spawn_point['point']
                self.game.game_objects.load_map(self,map,point)

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Start_Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.game_objects = game.game_objects
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'OPTIONS') #temporary
        self.sprites = Read_files.load_sprites('Sprites/UI/load_screen/new_game')
        self.image = self.sprites[0]
        self.animation = animation.Simple_animation(self)

        #create buttons
        self.buttons = ['Option 1','Option 2','Option 3','Option 4','Option 5']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def reset_timer(self):
        pass

    def define_BG(self):
        size = (90,130)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def update(self):
        #update menu arrow position
        self.animation.update()
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255))
        self.game.screen.blit(self.image, (0,0))

        #blit title
        self.game.screen.blit(self.title, (self.game.window_size[0]/2 - self.title.get_width()/2,50))
        self.game.screen.blit(self.bg, (70,180))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

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

    def initiate_buttons(self):
        y_pos = 200
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'OPTIONS') #temporary

        #create buttons
        self.buttons = ['Option 1','Option 2','Option 3','Option 4','Option 5']
        if self.game.DEBUG_MODE:
            self.buttons = ['Render FPS', 'Render Hitboxes']
        self.current_button = 0
        self.initiate_buttons()

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255))

        #blit title
        self.game.screen.blit(self.title, (self.game.window_size[0]/2 - self.title.get_width()/2,50))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

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

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.game.game_objects.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def update_options(self):
        if self.game.DEBUG_MODE:
            if self.current_button == 0:
                self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
            elif self.current_button == 1:
                self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

class Gameplay(Game_State):
    def __init__(self,game):
        super().__init__(game)

    def update(self):
        self.game.game_objects.update()
        self.game.game_objects.collide_all()
        self.game.game_objects.UI['gameplay'].update()

    def render(self):
        self.game.screen.fill((17,22,22))
        self.game.game_objects.draw()
        self.game.game_objects.UI['gameplay'].render()
        if self.game.RENDER_FPS_FLAG:
            self.blit_fps()

    def blit_fps(self):
        fps_string = str(int(self.game.clock.get_fps()))
        self.game.screen.blit(self.game.game_objects.font.render((30,12),'fps ' + fps_string),(self.game.window_size[0]-40,20))

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
                self.game.game_objects.player.abilities.handle_input(input)#to change movement ability
                #self.game.game_objects.player.omamoris.handle_input(input)
        elif input[1]:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input == 'death':#normal death
            self.game.game_objects.player.death()

class Pause_Menu(Gameplay):#when pressing ESC duing gameplay
    def __init__(self,game):
        super().__init__(game)
        self.arrow = entities_UI.Menu_Arrow()
        self.title = self.game.game_objects.font.render(text = 'Pause menu') #temporary
        self.title.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        #create buttons
        self.buttons = ['RESUME','OPTIONS','QUIT TO MAIN MENU','QUIT GAME']
        self.current_button = 0
        self.initiate_buttons()
        self.define_BG()

    def define_BG(self):
        size = (100,120)
        self.bg = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.bg,[20,20,20,200],(0,0,size[0],size[1]),border_radius=10)

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        super().render()
        self.game.screen.fill((50,50,50),special_flags=pygame.BLEND_RGB_ADD)
        self.game.screen.blit(self.bg, (self.game.window_size[0]/2 - self.bg.get_width()/2,100))

        #blit title
        self.game.screen.blit(self.title, (self.game.window_size[0]/2 - self.title.get_width()/2,110))

        #blit buttons
        for b in self.buttons:
            self.game.screen.blit(self.button_surfaces[b], self.button_rects[b].topleft)

        #blit arrow
        self.arrow.draw(self.game.screen)

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

    def initiate_buttons(self):
        y_pos = 140
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            text = (self.game.game_objects.font.render(text = b))
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((self.game.window_size[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def change_state(self):
        if self.current_button == 0:
            self.exit_state()

        elif self.current_button == 1:
            new_state = Option_Menu(self.game)
            new_state.enter_state()

        elif self.current_button == 2:
            self.game.state_stack = [self.game.state_stack[0]]

        elif self.current_button == 3:
            pygame.quit()
            sys.exit()

class Pause_gameplay(Gameplay):#a pause screen with shake. = when aila takes dmg
    def __init__(self,game, duration=10, amplitude = 20):
        super().__init__(game)
        self.duration = duration
        self.amp = amplitude
        self.game.state_stack[-1].render()#make sure that everything is plotted before making a screen copy
        self.temp_surface = self.game.screen.copy()

    def update(self):
        self.game.game_objects.cosmetics.update()
        self.duration -= self.game.dt
        self.amp = int(0.8*self.amp)
        if self.duration < 0:
            self.exit_state()

    def render(self):
        #super().render()
        self.game.game_objects.cosmetics.draw(self.game.screen)
        self.game.screen.blit(self.temp_surface, (random.randint(-self.amp,self.amp),random.randint(-self.amp,self.amp)))

class Slow_motion_gameplay(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.slow_rate = 0.5#determines the rate of slow motion, between 0 and 1
        self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].init(self.slow_rate)
        self.duration = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].duration

        self.bar = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites.sprite_dict['bar'][0].copy()
        self.meter = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites.sprite_dict['meter'][0].copy()
        self.width = self.meter.get_width()

        self.pos = [self.game.window_size[0]*0.5 - self.width*0.5,3]
        self.rate =self.meter.get_width()/self.duration

    def update(self):
        self.game.dt *= self.slow_rate#slow motion
        super().update()
        self.duration -= self.game.dt
        self.exit()

    def render(self):
        super().render()
        self.game.screen.fill((20,20,20), special_flags = pygame.BLEND_RGB_ADD)
        self.width -= self.game.dt*self.rate
        self.width = max(self.width,0)
        self.game.screen.blit(pygame.transform.scale(self.meter,[self.width,self.meter.get_height()]),self.pos)
        self.game.screen.blit(self.bar, self.pos)

    def exit(self):
        if self.duration < 0:
            self.game.game_objects.player.slow_motion = 1
            self.exit_state()

class Ability_menu(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.abilities=list(self.game.game_objects.player.abilities.spirit_abilities.keys())
        self.index = self.abilities.index(self.game.game_objects.player.abilities.equip)

        hud2=pygame.image.load("Sprites/Attack/HUD/abilityHUD2.png").convert_alpha()
        hud3=pygame.image.load("Sprites/Attack/HUD/abilityHUD3.png").convert_alpha()
        hud4=pygame.image.load("Sprites/Attack/HUD/abilityHUD4.png").convert_alpha()
        hud5=pygame.image.load("Sprites/Attack/HUD/abilityHUD5.png").convert_alpha()
        hud6=pygame.image.load("Sprites/Attack/HUD/abilityHUD6.png").convert_alpha()

        self.hud=[hud2,hud3,hud4,hud5,hud6]
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]

    def update(self):
        self.game.dt *= 0.5#slow motion
        super().update()

    def render(self):
        super().render()
        self.game.screen.fill((20,20,20),special_flags=pygame.BLEND_RGB_ADD)

        hud=self.hud[self.index]
        for index,ability in enumerate(self.abilities):
            hud.blit(self.game.game_objects.player.abilities.spirit_abilities[ability].sprites.sprite_dict['active_1'][0],self.coordinates[index])

        self.game.screen.blit(hud,(250,100))

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
    def __init__(self,game):
        super().__init__(game)
        self.count = 0
        self.fade_length = 20

        self.fade_surface = pygame.Surface(self.game.window_size, pygame.SRCALPHA, 32).convert_alpha()
        self.fade_surface.set_alpha(255)
        self.fade_surface.fill((0,0,0))

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
        self.game.game_objects.player.currentstate.enter_state('Idle_main')#infstaed of idle, should make her move a little dependeing on the direction
        self.exit_state()

    def render(self):
        super().render()#gameplay render
        self.fade_surface.set_alpha(int((self.fade_length - self.count)*(255/self.fade_length)))
        self.game.screen.blit(self.fade_surface, (0,0))

    def handle_events(self, input):
        pass

class Fadeout(Fadein):
    def __init__(self,game,previous_state,map_name,spawn,fade):
        super().__init__(game)
        self.previous_state = previous_state
        self.fade_length = 60
        self.fade_surface.set_alpha(int(255/self.fade_length))
        self.map_name = map_name
        self.spawn = spawn
        self.fade = fade

    def update(self):
        self.previous_state.update()
        self.count += self.game.dt
        if self.count > self.fade_length:
            self.exit()

    def exit(self):
        self.exit_state()#has to be before loadmap
        self.game.game_objects.load_map2(self.map_name, self.spawn, self.fade)

    def render(self):
        self.previous_state.render()
        self.fade_surface.set_alpha(int(self.count*(255/self.fade_length)))
        self.game.screen.blit(self.fade_surface, (0,0))

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_window_size = (352, 96)
        self.blit_pos = [int((self.game.window_size[0]-self.text_window_size[0])*0.5),60]
        self.clean_slate()

        self.conv = self.npc.dialogue.get_conversation()

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.game.game_objects.font.fill_text_bg(self.text_window_size)
        self.text_window.blit(self.npc.portrait,(0,10))

    def update(self):
        super().update()
        self.letter_frame += self.print_frame_rate*self.game.dt

    def render(self):
        super().render()
        text = self.game.game_objects.font.render((272,80), self.conv, int(self.letter_frame))
        self.text_window.blit(text,(64,8))
        self.game.screen.blit(self.text_window,self.blit_pos)

    def handle_events(self, input):
        if input[0]:
            if input[-1] == 'start':
                self.exit_state()

            elif input[-1] == 'y':
                if self.letter_frame < len(self.conv):
                    self.letter_frame = 10000
                else:#check if we have a series of conversations or not
                    self.clean_slate()
                    self.npc.dialogue.increase_conv_index()
                    self.conv = self.npc.dialogue.get_conversation()
                    if not self.conv:
                        self.exit_state()

    def exit_state(self):
        super().exit_state()
        self.npc.buisness()

class Select_menu(Gameplay):#map, inventory, omamori, journal
    def __init__(self, game):
        super().__init__(game)
        self.state = getattr(UI_select_menu, 'Inventory')(self)#should it alway go to inventory be default?

    def update(self):
        super().update()
        self.state.update()

    def render(self):
        super().render()
        self.state.render()

    def handle_events(self,input):
        self.state.handle_events(input)

class Facilities(Gameplay):#fast_travel (menu and unlock), ability upgrade (spurit and movement), bank, soul essence, vendor, smith
    def __init__(self, game,type,*arg):#args could be npc or travel point etc
        super().__init__(game)
        self.state = getattr(UI_facilities, type)(self,*arg)#make it a list and therevy a stack?

    def update(self):
        super().update()
        self.state.update()

    def render(self):
        super().render()
        self.state.render()

    def handle_events(self,input):
        self.state.handle_events(input)

class Cutscenes(Gameplay):#basically, this class is not needed but would be nice to have the cutscene classes in a seperate file
    def __init__(self, game,scene):
        super().__init__(game)
        self.current_scene = getattr(cutscene, scene)(self)#make an object based on string

    def update(self):
        self.current_scene.update()

    def render(self):
        self.current_scene.render()

    def handle_events(self, input):
        self.current_scene.handle_events(input)

class New_ability(Gameplay):#when player obtaines a new ability
    def __init__(self, game,ability):
        super().__init__(game)
        self.page = 0
        self.render_fade=[self.render_in,self.render_out]

        self.img = self.game.game_objects.player.sprites.sprite_dict[ability][0].copy()
        self.game.game_objects.player.reset_movement()

        self.surface = pygame.Surface((int(self.game.window_size[0]), int(self.game.window_size[1])), pygame.SRCALPHA, 32).convert_alpha()
        self.surface.fill((0,0,0))

        self.fade = 0
        self.surface.set_alpha(self.fade)

    def render(self):
        super().render()
        self.surface.set_alpha(int(self.fade))
        self.render_fade[self.page]()
        self.game.screen.blit(self.surface,(0, 0))
        self.game.screen.blit(self.img,(200, 200))#blit directly on screen to avoid alpha change on this

    def render_in(self):
        self.fade += 1
        self.fade = min(self.fade,150)
        self.img.set_alpha((255-150)+int(self.fade))

    def render_out(self):
        self.fade -= 1
        self.fade = max(self.fade,0)
        self.img.set_alpha(int(self.fade))

        if self.fade == 0:
            self.exit_state()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'start':
                self.page = 1
            elif input[-1] == 'a':
                self.page = 1

#cutscenes
class Cutscene_engine(Gameplay):#cut scenens that is based on game engien
    def __init__(self,game):
        self.game = game
        self.timer = 0
        self.pos = [-self.game.window_size[1],self.game.window_size[1]]
        self.const = 0.8#value that determines where the black boxes finish: 0.8 is 20% of screen is covered

    def render(self):
        super().render()
        self.cinematic()

    def cinematic(self):#black box stuff
        self.pos[0]+=self.game.dt#the upper balck box
        rect1=(0, int(self.pos[0]), self.game.window_size[0], self.game.window_size[1])
        pygame.draw.rect(self.game.screen, (0, 0, 0), rect1)

        self.pos[1]-=self.game.dt#the lower balck box
        rect2=(0, int(self.pos[1]), self.game.window_size[0], self.game.window_size[1])
        pygame.draw.rect(self.game.screen, (0, 0, 0), rect2)

        self.pos[0]=min(-self.game.window_size[1]*self.const,self.pos[0])
        self.pos[1]=max(self.game.window_size[1]*self.const,self.pos[1])

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
        self.camera_stops = []
        for camera_stop in self.game.game_objects.camera_blocks:
            self.camera_stops.append(camera_stop)
        self.game.game_objects.camera_blocks.empty()

    def cinematic(self):
        pass

    def update(self):
        super().update()
        self.timer += self.game.dt
        if self.timer>500:
            self.exit_state()

    def exit_state(self):
        for camera_stop in self.camera_stops:
            self.game.game_objects.camera_blocks.add(camera_stop)

        self.game.game_objects.camera.exit_state()
        super().exit_state()

class Title_screen(Cutscene_engine):#screen played after waking up from boss dream
    def __init__(self,objects):
        super().__init__(objects)
        self.title_name = self.parent_class.game.game_objects.font.render(text = 'Happy Ville')
        self.text1 = self.parent_class.game.game_objects.font.render(text = 'A game by Hjortron games')
        C.acceleration = [0.3,0.51]#restrict the speed
        self.stage = 0
        self.press = False

    def update(self):
        self.timer+=self.parent_class.game.dt

    def render(self):
        if self.stage == 0:#running slowly and blit title, Hjortron games etc.
            if self.timer>400:
                self.parent_class.game.screen.blit(self.title_name,(190,150))

            if self.timer>1000:
                self.parent_class.game.screen.blit(self.text1,(190,170))

            if self.timer >1200:
                self.stage += 1
                self.init_stage1()

        elif self.stage == 1:#camera moves up and aila runs away
            if self.timer == 1300:
                self.parent_class.game.game_objects.player.acceleration[0] = 0
                self.parent_class.game.game_objects.player.enter_idle()

            if self.timer > 1500:
                self.parent_class.game.screen.blit(self.title_name,(190,150))


            if self.timer > 1550:
                if self.press:
                    self.stage += 1
                    self.parent_class.game.game_objects.camera.exit_state()
                    self.parent_class.game.game_objects.load_map('village_1')
                    self.timer = 0
                    self.pos = [-self.parent_class.game.window_size[1],self.parent_class.game.window_size[1]]

        elif self.stage == 2:#cutscenen in village
            self.cinematic()
            if self.timer == 200:#make him movev to aila
                spawn_pos=(0,130)

                self.entity = Entities.Aslat(spawn_pos, self.parent_class.game.game_objects)

                self.parent_class.game.game_objects.npcs.add(self.entity)
                self.entity.currentstate.enter_state('Walk')
            elif self.timer == 320:#make it stay still
                self.entity.currentstate.enter_state('Idle')
            elif self.timer == 400:#start conversation
                self.entity.interact()
            elif self.timer > 410:
                self.exit_state()

    def handle_events(self,input):
        super().handle_events(input)
        if self.stage == 0:
            #can only go left
            if input[2][0] > 0: return
            self.parent_class.game.game_objects.player.currentstate.handle_movement(input)

    def init_stage1(self):
        C.acceleration = [1,0.51]#reset to normal movement
        input = [0,0,[-1,0],0]
        self.parent_class.game.game_objects.player.currentstate.handle_movement(input)
        self.parent_class.game.game_objects.camera.set_camera('Title_screen')

class Deer_encounter(Cutscene_engine):#first deer encounter in light forest by waterfall
    def __init__(self,objects):
        super().__init__(objects)
        spawn_pos=(700,130)
        self.entity=Entities.Reindeer(spawn_pos, self.parent_class.game.game_objects)
        self.parent_class.game.game_objects.enemies.add(self.entity)
        self.parent_class.game.game_objects.camera.set_camera('Deer_encounter')
        self.parent_class.game.game_objects.player.currentstate.enter_state('Walk')#should only enter these states once

    def update(self):#write how you want the player/group to act
        self.timer+=self.parent_class.game.dt
        if self.timer<50:
            self.parent_class.game.game_objects.player.velocity[0]=4
        elif self.timer==50:
            self.parent_class.game.game_objects.player.currentstate.enter_state('Idle')#should only enter these states once
            self.entity.currentstate.enter_state('Walk')
        elif self.timer>50:
            self.parent_class.game.game_objects.player.velocity[0]=0
            self.entity.velocity[0]=5

        if self.timer>200:
            self.exit_state()

    def exit_state(self):
        self.parent_class.game.game_objects.camera.exit_state()
        self.entity.kill()
        super().exit_state()

class Boss_deer_encounter(Cutscene_engine):#boss fight cutscene
    def __init__(self,objects):
        super().__init__(objects)
        pos = (self.parent_class.game.game_objects.camera.scroll[0] + 900,self.parent_class.game.game_objects.camera.scroll[1] + 100)
        self.entity = Entities.Reindeer(pos, self.parent_class.game.game_objects)#make the boss
        self.parent_class.game.game_objects.enemies.add(self.entity)
        self.entity.dir[0]=-1
        self.parent_class.game.game_objects.camera.set_camera('Deer_encounter')
        self.entity.AI.deactivate()
        self.stage = 0
        self.parent_class.game.game_objects.player.currentstate.enter_state('Walk_main')
        self.parent_class.game.game_objects.player.currentstate.walk()#to force tha walk animation

    def update(self):#write how you want the player/group to act
        self.timer += self.parent_class.game.dt
        if self.stage == 0:
            self.parent_class.game.game_objects.player.velocity[0]  = 4

            if self.timer >120:
                self.stage=1
                self.parent_class.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once
                self.parent_class.game.game_objects.player.acceleration[0] = 0

        elif self.stage==1:
            if self.timer>200:
                self.entity.currentstate.enter_state('Transform')
                self.parent_class.game.game_objects.player.velocity[0] = -20
                self.parent_class.game.game_objects.camera.camera_shake(amp=3,duration=100)#amplitude, duration
                self.stage=2

        elif self.stage==2:
            if self.timer > 400:
                self.parent_class.game.game_objects.camera.exit_state()#exsiting deer encounter camera
                self.entity.AI.activate()
                self.exit_state()

class Defeated_boss(Cutscene_engine):#cut scene to play when a boss dies
    def __init__(self,objects):
        super().__init__(objects)
        self.step1 = False
        self.const = 0.5#value that determines where the black boxes finish: 0.8 is 20% of screen is covered
        self.parent_class.game.game_objects.player.currentstate.enter_state('Idle_main')#should only enter these states once

    def update(self):
        self.timer+=self.parent_class.game.dt
        if self.timer < 75:
            self.parent_class.game.game_objects.player.velocity[1] = -2
        elif self.timer > 75:
            self.parent_class.game.game_objects.player.velocity[1] = -1#compensates for gravity, levitates
            self.step1 = True

        if self.timer > 250:
            self.parent_class.game.game_objects.player.velocity[1] = 2#go down again
            if self.parent_class.game.game_objects.player.collision_types['bottom']:
                self.exit_state()

    def render(self):
        super().render()
        if self.step1:
            particle = getattr(particles, 'Spark')(self.parent_class.game.game_objects.player.rect.center,self.parent_class.game.game_objects,distance = 400, lifetime = 60, vel = {'linear':[7,13]}, dir = 'isotropic', scale = 1, colour = [255,255,255,255])
            self.parent_class.game.game_objects.cosmetics.add(particle)

            self.parent_class.game.game_objects.cosmetics.draw(self.parent_class.game.game_objects.game.screen)
            self.parent_class.game.game_objects.players.draw(self.parent_class.game.game_objects.game.screen)

class Death(Cutscene_engine):#when aila dies
    def __init__(self,objects):
        super().__init__(objects)
        self.stage = 0

    def update(self):
        self.timer += self.parent_class.game.dt
        if self.stage == 0:

            if self.timer > 120:
                self.state1()

        elif self.stage == 1:
                #spawn effect
                pos=(0,0)#
                offset=100#depends on the effect animation
                self.spawneffect = Entities.Spawneffect(pos,self.parent_class.game.game_objects)
                self.spawneffect.rect.midbottom=self.parent_class.game.game_objects.player.rect.midbottom
                self.spawneffect.rect.bottom += offset
                self.parent_class.game.game_objects.cosmetics.add(self.spawneffect)
                self.stage = 2

        elif self.stage == 2:
            if self.spawneffect.finish:#when the cosmetic effetc finishes
                self.parent_class.game.game_objects.player.currentstate.enter_state('Spawn_main')
                self.exit_state()

    def state1(self):
        self.parent_class.game.game_objects.load_map(self.parent_class.game.game_objects.player.spawn_point[-1]['map'],self.parent_class.game.game_objects.player.spawn_point[-1]['point'])
        self.parent_class.game.game_objects.player.currentstate.enter_state('Invisible_main')
        self.stage = 1
        self.timer = 0

    def handle_events(self,input):
        pass

    def cinematic(self):
        pass

#cultist encountter
class Cultist_encounter(Cutscene_engine):#intialised from cutscene trigger
    def __init__(self,game):
        super().__init__(game)
        self.gameplay = Cultist_encounter_gameplay(game)
        self.gameplay.enter_state()

        self.stage = 0
        self.gameplay.entity1.AI.deactivate()
        self.game.game_objects.enemies.add(self.gameplay.entity1)

        self.game.game_objects.interactables.add(self.gameplay.gate)

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
                #self.parent_class.game.game_objects.player.velocity[0]=0
                self.game.game_objects.player.acceleration[0]=0

                self.stage = 1

        elif self.stage == 1:
            if self.timer>200:
                spawn_pos = self.game.game_objects.player.rect.topright
                self.gameplay.entity2.AI.deactivate()
                self.gameplay.entity2.dir[0]=-1
                self.gameplay.entity2.currentstate.enter_state('Ambush_pre')

                self.game.game_objects.enemies.add(self.gameplay.entity2)

                self.stage=2
                self.timer=0

        elif self.stage==2:#sapawn cultist_rogue
            if self.timer>100:
                self.exit_state()

    def exit_state(self):
        self.gameplay.entity1.AI.activate()
        self.gameplay.entity2.AI.activate()
        self.game.game_objects.camera.exit_state()
        super().exit_state()

class Cultist_encounter_gameplay(Gameplay):#initialised in the cutscene:if player dies, the plater is not respawned but transffered to cultist hideout
    def __init__(self,game):
        super().__init__(game)
        spawn_pos = (self.game.game_objects.camera.scroll[0] - 150,self.game.game_objects.camera.scroll[1] + 100)
        self.entity1 = Entities.Cultist_warrior(spawn_pos, self.game.game_objects, self)#added to group in cutscene
        self.entity2 = Entities.Cultist_rogue(spawn_pos, self.game.game_objects, self)#added to group in cutscene
        self.gate = Entities.Gate((self.game.game_objects.camera.scroll[0] - 250,self.game.game_objects.camera.scroll[1] + 100),self.game.game_objects)#added to group in cutscene
        self.kill = 0#when the enteties have died, this will tick up

    def incrase_kill(self):#called when entity1 and 2 are killed
        self.kill += 1
        if self.kill == 2:#both cultist have died
            self.game.game_objects.world_state.cutscenes_complete.append(type(self).__name__.replace('_gameplay',''))
            self.gate.currentstate.handle_input('Transform')
            self.exit_state()#if there was a gate, we can open it

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input == 'death':#if aila dies during the fight, this is called
            self.game.game_objects.player.reset_movement()
            self.game.game_objects.load_map(self,'cultist_hideout_1','2')
