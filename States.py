import pygame, sys
import Read_files
import Engine
import Entities

class Game_State():
    def __init__(self,game):
        self.font = Read_files.Alphabet("Sprites/UI/Alphabet/Alphabet.png")#intitilise the alphabet class, scale of alphabet
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
        self.arrow = Entities.Menu_Arrow()
        self.title = self.font.render(text = 'HAPPY VILLE') #temporary

        #create buttons
        self.buttons = ['NEW GAME','LOAD GAME','OPTIONS','QUIT']
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
            elif event[-1] in ('return', 'a'):
                self.change_state()
            elif event[-1] == 'start':
                pygame.quit()
                sys.exit()

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def change_state(self):
        if self.current_button == 0:
            new_state = Gameplay(self.game)
            new_state.enter_state()
            #load new game level
            self.game.game_objects.load_map('village1')

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
        self.arrow = Entities.Menu_Arrow()
        self.title = self.font.render(text = 'LOAD GAME') #temporary

        #create buttons
        self.buttons = ['SLOT 1','SLOT 2','SLOT 3','SLOT 4']
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

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = Entities.Menu_Arrow()
        self.title = self.font.render(text = 'OPTIONS') #temporary

        #create buttons
        self.buttons = ['Option 1','Option 2','Option 3','Option 4','Option 5']
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

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Pause_Menu(Game_State):

    def __init__(self,game):
        super().__init__(game)
        self.arrow = Entities.Menu_Arrow()
        self.title = self.font.render(text = 'PAUSE') #temporary

        #create buttons
        self.buttons = ['RESUME','OPTIONS','QUIT TO MAIN MENU','QUIT GAME']
        self.current_button = 0
        self.initiate_buttons()

    def update(self):
        #update menu arrow position
        ref_pos = self.button_rects[self.buttons[self.current_button]].topleft
        self.arrow.update((ref_pos[0] - 10, ref_pos[1]))

    def render(self):
        #fill game.screen
        self.game.screen.fill((255,255,255,128))

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
            elif event[-1] in ('return', 'a'):
                self.change_state()
            elif event[-1] == 'start':
                self.exit_state()

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.font.render(text = b))
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

class Gameplay(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.health_sprites = Read_files.Sprites().generic_sheet_reader("Sprites/UI/health/hearts_black.png",9,8,2,3)
        self.spirit_sprites = Read_files.Sprites().generic_sheet_reader("Sprites/UI/Spirit/spirit_orbs.png",9,9,1,3)

    def update(self):
        self.game.game_objects.scrolling()
        self.game.game_objects.group_distance()
        self.game.game_objects.trigger_event()
        self.game.game_objects.check_camera_border()
        self.game.game_objects.collide_all()

    def render(self):
        self.game.screen.fill((207,238,250))
        self.game.game_objects.draw()
        self.blit_screen_info()

    def blit_screen_info(self):
        self.blit_health()
        self.blit_spirit()
        self.blit_fps()

    def blit_health(self):
        #this code is specific to using heart.png sprites
        sprite_dim = [9,8] #width, height specific to sprites used
        blit_surface = pygame.Surface((int(self.game.game_objects.player.max_health/20)*(sprite_dim[0] + 1),sprite_dim[1]),pygame.SRCALPHA,32)
        health = self.game.game_objects.player.health

        for i in range(int(self.game.game_objects.player.max_health/20)):
            health -= 20
            if health >= 0:
                blit_surface.blit(self.health_sprites[0],(i*(sprite_dim[0] + 1),0))
            elif health > -20:
                blit_surface.blit(self.health_sprites[-(health//4)],(i*(sprite_dim[0] + 1),0))
            else:
                blit_surface.blit(self.health_sprites[5],(i*(sprite_dim[0] + 1),0))

        self.game.screen.blit(blit_surface,(20, 20))

    def blit_spirit(self):

        sprite_dim = [9,9] #width, height specific to sprites used
        blit_surface = pygame.Surface((int(self.game.game_objects.player.max_spirit/20)*(sprite_dim[0] + 1),sprite_dim[1]),pygame.SRCALPHA,32)
        spirit = self.game.game_objects.player.spirit

        for i in range(int(self.game.game_objects.player.max_spirit/20)):
            spirit -= 20
            if spirit > -10:
                blit_surface.blit(self.spirit_sprites[0],(i*(sprite_dim[0] + 1),0))
            elif spirit > -20:
                blit_surface.blit(self.spirit_sprites[1],(i*(sprite_dim[0] + 1),0))
            else:
                blit_surface.blit(self.spirit_sprites[2],(i*(sprite_dim[0] + 1),0))

        self.game.screen.blit(blit_surface,(20, 34))

    def blit_fps(self):
        fps_string = str(int(self.game.clock.get_fps()))
        self.game.screen.blit(self.font.render((30,12),'fps ' + fps_string),(self.game.WINDOW_SIZE[0]-40,20))

    def handle_events(self, input):
        if input[0]:
            if input[-1]=='start':#escape button
                new_state = Pause_Menu(self.game)
                new_state.enter_state()
            elif input[-1]=='rb':
                new_state = Ability_Menu(self.game)
                new_state.enter_state()
            elif input[-1] == 'y':
                npc = self.game.game_objects.conversation_collision()
                if npc:
                    new_state = Conversation(self.game, npc)
                    new_state.enter_state()
                else:
                    self.game.game_objects.interactions()
            elif input[-1] == 'select':
                new_state = Start_Menu(self.game)
                new_state.enter_state()
            else:
                self.game.game_objects.player.currentstate.handle_input(input)

        elif input [1]:
            self.game.game_objects.player.currentstate.handle_input(input)



class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.npc = npc
        self.print_frame_rate = 3
        self.text_WINDOW_SIZE = (352, 96)
        self.blit_x = int((self.game.WINDOW_SIZE[0]-self.text_WINDOW_SIZE[0])/2)
        self.clean_slate()

        self.conv = self.npc.get_conversation('state_1')

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.font.fill_text_bg(self.text_WINDOW_SIZE)
        self.text_window.blit(self.npc.portrait,(0,10))

    def update(self):
        super().update()

        self.letter_frame += 1

    def render(self):
        super().render()
        text = self.font.render((272,80), self.conv, int(self.letter_frame//self.print_frame_rate))
        self.text_window.blit(text,(64,8))
        self.game.screen.blit(self.text_window,(self.blit_x,60))

    def handle_events(self, input):

        if input[0]:
            if input[-1] == 'start':
                self.exit_state()

            elif input[-1] == 'y':
                if self.letter_frame//self.print_frame_rate < len(self.npc.get_conversation('state_1')):
                    self.letter_frame = 10000
                else:
                    self.clean_slate()
                    self.npc.increase_conv_index()
                    self.conv = self.npc.get_conversation('state_1')
                    if not self.conv:
                        self.exit_state()

class Ability_Menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.abilities=list(self.game.game_objects.player.abilities.keys())
        self.index=self.abilities.index(self.game.game_objects.player.equip)

        symbol1=pygame.image.load("Sprites/Attack/Darksaber/symbol/darksaber.png").convert_alpha()
        symbol2=pygame.image.load("Sprites/Attack/Heal/symbol/heal.png").convert_alpha()
        symbol3=pygame.image.load("Sprites/Attack/Force/symbol/force.png").convert_alpha()
        symbol4=pygame.image.load("Sprites/Attack/Hammer/symbol/hammer.png").convert_alpha()
        symbol5=pygame.image.load("Sprites/Attack/Arrow/symbol/arrow.png").convert_alpha()

        hud2=pygame.image.load("Sprites/Attack/HUD/abilityHUD2.png").convert_alpha()
        hud3=pygame.image.load("Sprites/Attack/HUD/abilityHUD3.png").convert_alpha()
        hud4=pygame.image.load("Sprites/Attack/HUD/abilityHUD4.png").convert_alpha()
        hud5=pygame.image.load("Sprites/Attack/HUD/abilityHUD5.png").convert_alpha()
        hud6=pygame.image.load("Sprites/Attack/HUD/abilityHUD6.png").convert_alpha()

        self.symbols={'Darksaber':symbol1,'Heal':symbol2,'Force':symbol3,'Hammer':symbol4,'Arrow':symbol5}
        self.hud=[hud2,hud3,hud4,hud5,hud6]
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]

    def update(self):
        super().update()
        pygame.time.wait(100)#slow motion

    def render(self):
        super().render()

        hud=self.hud[self.index]

        #positions=[]#placeholder
        for index,ability in enumerate(self.abilities):
            #coordinate=[100+50*index,200]
            #self.game.screen.blit(self.font.render((50,50),ability),(coordinate))
            #self.game.screen.blit(self.symbols[ability],(coordinate))
            hud.blit(self.symbols[ability],self.coordinates[index])

            #positions.append(coordinate)#coordinates of all blits

        #self.game.screen.fill((20,20,20),special_flags=pygame.BLEND_RGB_ADD)#change the overall colour while changing equip
        #self.game.screen.blit(self.font.render((20,20),'o'),(positions[self.index][0],positions[self.index][1]-20))#the pointer

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
                self.game.game_objects.player.equip=self.abilities[self.index]
                self.game.game_objects.player.ability=self.game.game_objects.player.abilities[self.game.game_objects.player.equip]
                #self.game.game_objects.player.equip=self.game.game_objects.player.abilities[self.ab_index]#select ability
                self.exit_state()

class Start_Menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.inventory_BG=pygame.image.load("Sprites/UI/Inventory/inventory.png").convert_alpha()

        self.inventory=[]#make all objects and save in list
        for item in self.game.game_objects.player.inventory.keys():
            self.inventory.append(getattr(sys.modules[Entities.__name__], item)(self.game.game_objects.player))#make the object based on the string

    def update(self):
        super().update()

    def render(self):
        super().render()

        self.game.screen.blit(self.inventory_BG,(0,0))

        width=self.game.game_objects.player.image.get_width()
        height=self.game.game_objects.player.image.get_height()
        scale=2
        self.game.screen.blit(pygame.transform.scale(self.game.game_objects.player.image,(scale*width,scale*height)),(180,120))#player position

        for index, loot in enumerate(self.inventory):
            loot.update_animation()
            self.game.screen.blit(pygame.transform.scale(loot.image,(int(width/scale),int(height/scale))),(0+50*index,0))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
