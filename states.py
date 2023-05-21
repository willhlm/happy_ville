import pygame, sys, random
import Read_files
import entities_UI
import cutscene
import constants as C
import animation
import UI_select_menu, UI_facilities

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
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
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
            text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.button_surfaces[b] = text
            self.button_rects[b] = pygame.Rect((100,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20


    def change_state(self):
        if self.current_button == 0:#new game
            new_state = Gameplay(self.game)
            new_state.enter_state()

            #when starting a new game, should be a cutscene
            #new_state = Cutscenes(self.game,'New_game')
            #new_state.enter_state()

            #load new game level
            self.game.game_objects.load_map('village_2','1')

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
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
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
                self.game.game_objects.load_map(map,point)

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
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))
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
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,50))

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
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
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
        self.game.screen.blit(self.game.game_objects.font.render((30,12),'fps ' + fps_string),(self.game.WINDOW_SIZE[0]-40,20))

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
                self.game.game_objects.collisions.pass_through()

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
        self.game.screen.blit(self.bg, (self.game.WINDOW_SIZE[0]/2 - self.bg.get_width()/2,100))

        #blit title
        self.game.screen.blit(self.title, (self.game.WINDOW_SIZE[0]/2 - self.title.get_width()/2,110))

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
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
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
        #self.shader = shader_entities.Shader_entities(self)

    def update(self):
        self.game.game_objects.cosmetics.update([0,0])
        self.duration -= self.game.dt
        self.amp = int(0.8*self.amp)
        if self.duration < 0:
            self.exit_state()

    def render(self):
        #super().render()
        self.game.game_objects.cosmetics.draw(self.game.screen)
        self.game.screen.blit(self.temp_surface, (random.randint(-self.amp,self.amp),random.randint(-self.amp,self.amp)))

class Cultist_encounter_gameplay(Gameplay):#if player dies, the plater is not respawned but transffered to cultist hideout
    def __init__(self,game):
        super().__init__(game)

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input == 'exit':
            self.exit_state()
        elif input == 'death':
            self.game.game_objects.player.reset_movement()
            self.game.game_objects.load_map('cultist_hideout_1','2')

class Slow_motion_gameplay(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.slow_rate = 0.5#determines the rate of slow motion, between 0 and 1
        self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].init(self.slow_rate)
        self.duration = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].duration

        self.bar = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites.sprite_dict['bar'][0].copy()
        self.meter = self.game.game_objects.player.abilities.spirit_abilities['Slow_motion'].sprites.sprite_dict['meter'][0].copy()
        self.width = self.meter.get_width()

        self.pos = [self.game.WINDOW_SIZE[0]*0.5 - self.width*0.5,3]
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

class Fading(Gameplay):#fades out and then in
    def __init__(self,game):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_out,self.render_in]
        self.fade_surface = pygame.Surface(self.game.WINDOW_SIZE, pygame.SRCALPHA, 32)
        self.fade_surface.fill((0,0,0))
        self.init_out()

    def init_in(self):
        self.count = 0
        self.fade_length = 20
        self.fade_surface.set_alpha(255)

    def init_out(self):
        self.count = 0
        self.fade_length = 60
        self.fade_surface.set_alpha(int(255/self.fade_length))

    def update(self):
        super().update()
        self.count += min(self.game.dt,2)#the framerate jump when loading map. This class is called when loading a map. Need to set maximum dt
        if self.count > self.fade_length:
            self.page += 1
            self.init_in()
            if self.page == 2:
                self.exit()

    def exit(self):
        self.game.game_objects.load_bg_music()
        self.exit_state()

    def render(self):
        self.render_fade[self.page]()
        self.game.screen.blit(self.fade_surface, (0,0))

    def render_in(self):
        super().render()
        self.fade_surface.set_alpha(int((self.fade_length - self.count)*(255/self.fade_length)))

    def render_out(self):
        self.fade_surface.set_alpha(int(self.count*(255/self.fade_length)))

    def handle_events(self, input):
        pass

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_WINDOW_SIZE = (352, 96)
        self.blit_pos = [int((self.game.WINDOW_SIZE[0]-self.text_WINDOW_SIZE[0])*0.5),60]
        self.clean_slate()

        self.conv = self.npc.dialogue.get_conversation()

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.game.game_objects.font.fill_text_bg(self.text_WINDOW_SIZE)
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
        if scene != 'Death':
            self.game.game_objects.world_state.cutscenes_complete.append(scene)#scenes will not run if the scnene is in this list

    def update(self):
        super().update()
        self.current_scene.update()

    def render(self):
        super().render()#want the BG to keep rendering for engine. It is not needed for file cut scnene
        self.current_scene.render()#to plot the abilities. Maybe better with another state?

    def handle_events(self, input):
        self.current_scene.handle_events(input)

class New_ability(Gameplay):#when player obtaines a new ability
    def __init__(self, game,ability):
        super().__init__(game)
        self.page = 0
        self.render_fade=[self.render_in,self.render_out]

        self.img = self.game.game_objects.player.sprites.sprite_dict[ability][0].copy()
        self.game.game_objects.player.reset_movement()

        self.surface = pygame.Surface((int(self.game.WINDOW_SIZE[0]), int(self.game.WINDOW_SIZE[1])), pygame.SRCALPHA, 32).convert_alpha()
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
