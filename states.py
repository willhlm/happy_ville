import pygame, sys
import Read_files
import Engine
import Entities
import cutscene
import constants as C
import random

class Game_State():
    def __init__(self,game):
        self.font = Read_files.Alphabet()#intitilise the alphabet class, scale of alphabet
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
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def change_state(self):
        if self.current_button == 0:#new game
            new_state = Gameplay(self.game)
            new_state.enter_state()

            #when starting a new game, should be a cutscene
            #new_state = Cutscenes(self.game,'New_game')
            #new_state.enter_state()

            #load new game level
            self.game.game_objects.load_map('village_1','1')


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
            elif event[-1] in ('return', 'a'):
                self.game.game_objects.load_game()#load saved game data

                new_state = Gameplay(self.game)
                new_state.enter_state()
                map=self.game.game_objects.player.spawn_point['map']
                point=self.game.game_objects.player.spawn_point['point']
                self.game.game_objects.load_map(map,point)

    def initiate_buttons(self):
        y_pos = 90
        self.button_surfaces = {}
        self.button_rects = {}
        for b in self.buttons:
            self.button_surfaces[b] = (self.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

class Start_Option_Menu(Game_State):
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

class Option_Menu(Game_State):
    def __init__(self,game):
        super().__init__(game)
        self.arrow = Entities.Menu_Arrow()
        self.title = self.font.render(text = 'OPTIONS') #temporary

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
            self.button_surfaces[b] = (self.font.render(text = b))
            self.button_rects[b] = pygame.Rect((self.game.WINDOW_SIZE[0]/2 - self.button_surfaces[b].get_width()/2 ,y_pos),self.button_surfaces[b].get_size())
            y_pos += 20

    def update_options(self):
        if self.game.DEBUG_MODE:
            if self.current_button == 0:
                self.game.RENDER_FPS_FLAG = not self.game.RENDER_FPS_FLAG
            elif self.current_button == 1:
                self.game.RENDER_HITBOX_FLAG = not self.game.RENDER_HITBOX_FLAG

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
        self.light_effects = []#can append diffeet light effects: dark (caves) or light glow around aila

    def update(self):
        self.game.game_objects.update()
        self.game.game_objects.collide_all()

    def render(self):
        self.game.screen.fill((17,22,22))
        self.game.game_objects.draw()
        self.blit_screen_info()
        self.render_effect()

    def render_effect(self):
        for effect in self.light_effects:
            effect()

    def blit_screen_info(self):
        self.blit_health()
        self.blit_spirit()
        if self.game.RENDER_FPS_FLAG:
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
        self.game.game_objects.player.currentstate.handle_movement(input)

        if input[0]:#press
            if input[-1]=='start':#escape button
                new_state = Pause_Menu(self.game)
                new_state.enter_state()

            elif input[-1]=='rb':
                new_state = Ability_Menu(self.game)
                new_state.enter_state()

            elif input[-1] == 'y':
                self.game.game_objects.collisions.check_interaction_collision()

            elif input[-1] == 'select':
                new_state = Select_Menu(self.game)
                new_state.enter_state()

            elif input[-1] == 'down':
                self.game.game_objects.collisions.pass_through()

            else:
                self.game.game_objects.player.currentstate.handle_press_input(input)
                self.game.game_objects.player.omamoris.handle_input(input)
        elif input[1]:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input =='dark':#dark around aila
            self.light_effects.append(self.blit_dark_effect)
            self.make_glow(6)
        elif input =='light':#light around aila
            self.light_effects.append(self.blit_glow_effect)
            self.make_glow(1)
        elif input == 'death':#normal death
            self.game.game_objects.player.death()
        elif input == 'exit':#remove any effects
            self.light_effects = []

    def blit_glow_effect(self):
        pos=[self.game.game_objects.player.rect.centerx-self.radius,self.game.game_objects.player.rect.centery-self.radius]
        self.game.screen.blit(self.glow,pos,special_flags=pygame.BLEND_RGBA_ADD)

    def blit_dark_effect(self):
        self.dark.fill((80,80,80))#dark background
        pos=[self.game.game_objects.player.rect.centerx-self.radius,self.game.game_objects.player.rect.centery-self.radius]
        self.dark.blit(self.glow,pos,special_flags = pygame.BLEND_RGBA_ADD)
        self.game.screen.blit(self.dark,(0,0),special_flags = pygame.BLEND_RGBA_MULT)

    def make_glow(self,const=1):#init
        self.dark = pygame.Surface((int(self.game.WINDOW_SIZE[0]), int(self.game.WINDOW_SIZE[1]))).convert_alpha()#ONLY USED FOR DARK MODE
        self.radius = 200
        self.glow = pygame.Surface((self.radius * 2, self.radius * 2),pygame.SRCALPHA,32).convert_alpha()
        layers = 40

        for i in range(layers):
            k = i*const
            k = min(k,255)
            pygame.draw.circle(self.glow,(k,k,k),self.glow.get_rect().center,self.radius-i*5)

class Pause_gameplay(Gameplay):#a pause screen with shake. = when aila takes dmg
    def __init__(self,game, duration=10, amplitude = 20):
        super().__init__(game)
        self.duration = duration
        self.amp = amplitude
        self.game.state_stack[-1].render()#make sure that everything is plotted before making a screen copy
        self.temp_surface = self.game.screen.copy()

    def update(self):
        self.game.game_objects.cosmetics.update([0,0])
        self.duration -= 1
        self.amp = int(0.8*self.amp)
        if self.duration < 0:
            self.exit_state()

    def render(self):
        self.game.screen.blit(self.temp_surface, (random.randint(-self.amp,self.amp),random.randint(-self.amp,self.amp)))

class Cultist_encounter_gameplay(Gameplay):#if player dies, the plater is not respawned but transffered to cultist hideout
    def __init__(self,game):
        super().__init__(game)
        self.game.game_objects.player.health = max(30,self.game.game_objects.player.health)#the player should have atleast some lives if it get hit in cutsene.

    def handle_input(self,input):
        if input == 'dmg':
            new_game_state = Pause_gameplay(self.game,duration=11)
            new_game_state.enter_state()
        elif input == 'exit':
            self.exit_state()
        elif input == 'death':
            self.game.game_objects.player.reset_movement()
            self.game.game_objects.load_map('cultist_hideout1','2')

class Ability_Menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.abilities=list(self.game.game_objects.player.abilities.keys())
        self.index=self.abilities.index(self.game.game_objects.player.equip)

        symbol1=pygame.image.load("Sprites/Attack/Darksaber/symbol/darksaber.png").convert_alpha()
        symbol2=pygame.image.load("Sprites/Attack/Heal/symbol/heal.png").convert_alpha()
        symbol3=pygame.image.load("Sprites/Attack/Force/symbol/force.png").convert_alpha()
        symbol4=pygame.image.load("Sprites/Attack/thunder/symbol/hammer.png").convert_alpha()
        symbol5=pygame.image.load("Sprites/Attack/Arrow/symbol/arrow.png").convert_alpha()

        hud2=pygame.image.load("Sprites/Attack/HUD/abilityHUD2.png").convert_alpha()
        hud3=pygame.image.load("Sprites/Attack/HUD/abilityHUD3.png").convert_alpha()
        hud4=pygame.image.load("Sprites/Attack/HUD/abilityHUD4.png").convert_alpha()
        hud5=pygame.image.load("Sprites/Attack/HUD/abilityHUD5.png").convert_alpha()
        hud6=pygame.image.load("Sprites/Attack/HUD/abilityHUD6.png").convert_alpha()

        self.symbols={'Darksaber':symbol1,'Heal':symbol2,'Force':symbol3,'Thunder':symbol4,'Arrow':symbol5}
        self.hud=[hud2,hud3,hud4,hud5,hud6]
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]

    def update(self):
        super().update()
        pygame.time.wait(100)#slow motion

    def render(self):
        super().render()
        self.game.screen.fill((20,20,20),special_flags=pygame.BLEND_RGB_ADD)

        hud=self.hud[self.index]
        for index,ability in enumerate(self.abilities):
            hud.blit(self.symbols[ability],self.coordinates[index])

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
                self.exit_state()

class Select_Menu(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.inventory_BG=Read_files.Sprites().load_all_sprites("Sprites/UI/Menu/select/")['']
        self.box = Entities.Menu_Box()

        self.page=1
        self.pages=[self.map_menu,self.inventory_menu,self.omamori_menu]#what to render

        #invenotory stuff
        self.use_items=[]
        self.key_items=[]
        self.key_number=[]
        self.use_number=[]
        for key in self.game.game_objects.player.inventory.keys():
            item=getattr(sys.modules[Entities.__name__], key)([0,0],self.game.game_objects)#make the object based on the string
            if hasattr(item, 'use_item'):
                self.use_items.append(item)
                self.use_number.append(self.game.game_objects.player.inventory[key])

            else:
                self.key_items.append(item)
                self.key_number.append(self.game.game_objects.player.inventory[key])

        self.stone_pos = [[135,3],[168,27],[168,90],[103,27],[103,90]]#infinity stone blit positions

        self.item_index=[0,0]
        self.item_positions=(270,150)
        self.keyitem_positions=(320,50)

        #omamori stuff
        self.omamori_index=[0,0]
        self.positions=(255,120)
        self.equip_positions=(260,25)

    def blit_inventory_BG(self):
        width=self.inventory_BG[self.page].get_width()
        self.game.screen.blit(self.inventory_BG[self.page],((self.game.WINDOW_SIZE[0]-width)/2,20))

    def render(self):
        super().render()
        self.blit_inventory_BG()
        self.pages[self.page]()

    def map_menu(self):
        pass

    def inventory_menu(self):
        for index, item in enumerate(self.use_items):#items we can use
            item.animation.update()
            pos=[self.item_positions[0]+20*index,self.item_positions[1]]
            self.game.screen.blit(pygame.transform.scale(item.image,(16,16)),pos)
            number = self.font.render(text = str(self.use_number[index]))
            self.game.screen.blit(number,pos)

        for index, item in enumerate(self.key_items):
            item.animation.update()
            pos=[self.keyitem_positions[0]+20*index,self.keyitem_positions[1]]
            self.game.screen.blit(pygame.transform.scale(item.image,(16,16)),pos)
            number = self.font.render(text = str(self.key_number[index]))
            self.game.screen.blit(number,pos)

        self.game.screen.blit(self.box.img,(self.item_positions[0]-16+20*self.item_index[0],135+20*self.item_index[1]))#pointer
        self.blit_sword()

    def blit_sword(self):
        self.game.game_objects.player.sword.potrait_animation()
        self.game.screen.blit(self.game.game_objects.player.sword.potrait_image,(105,0))#player position

        for index, stone in enumerate(self.game.game_objects.player.sword.stones):
            self.game.game_objects.player.sword.stones[stone].animation.update()
            self.game.screen.blit(self.game.game_objects.player.sword.stones[stone].image,self.stone_pos[index])#player position

    def omamori_menu(self):
        for index, omamori in enumerate(self.game.game_objects.player.omamoris.equipped_omamoris):#equipped ones
            pos=[self.equip_positions[0]+50*index,self.equip_positions[1]]
            self.game.screen.blit(omamori.image,pos)

        for index, omamori in enumerate(self.game.game_objects.player.omamoris.omamori_list):#the ones in inventory
            omamori.animation.update()
            pos=[self.positions[0]+20*index,self.positions[1]]
            self.game.screen.blit(omamori.image,pos)

        self.game.screen.blit(self.box.img,(self.positions[0]+20*self.omamori_index[0],135+20*self.omamori_index[1]))#pointer

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':
                self.page+=1
                self.page=min(self.page,2)
            elif input[-1] == 'lb':
                self.page-=1
                self.page=max(self.page,0)

            if self.page==0:#map stuff
                pass


            elif self.page==1:#inventory stuff
                if input[-1] =='right':
                    self.item_index[0]+=1
                    self.item_index[0]=min(self.item_index[0],5)
                elif input[-1] =='left':
                    self.item_index[0]-=1
                    self.item_index[0]=max(self.item_index[0],0)
                elif input[-1] =='down':
                    self.item_index[1]+=1
                    self.item_index[1]=min(self.item_index[1],1)
                elif input[-1] =='up':
                    self.item_index[1]-=1
                    self.item_index[1]=max(self.item_index[1],0)
                elif input[-1]=='a' or input[-1]=='return':
                    self.use_item()

            elif self.page==2:#omamori stuff
                if input[-1] =='right':
                    self.omamori_index[0]+=1
                    self.omamori_index[0]=min(self.omamori_index[0],5)
                elif input[-1] =='left':
                    self.omamori_index[0]-=1
                    self.omamori_index[0]=max(self.omamori_index[0],0)
                elif input[-1] =='down':
                    self.omamori_index[1]+=1
                    self.omamori_index[1]=min(self.omamori_index[1],1)
                elif input[-1] =='up':
                    self.omamori_index[1]-=1
                    self.omamori_index[1]=max(self.omamori_index[1],0)
                elif input[-1]=='a':
                    self.choose_omamori()

    def choose_omamori(self):
        omamori_index=self.omamori_index[0]
        if self.omamori_index[1]==1:#if on the bottom row
            omamori_index+=5
        if omamori_index<len(self.game.game_objects.player.omamoris.omamori_list):
            self.game.game_objects.player.omamoris.equip_omamori(omamori_index)

    def use_item(self):
        item_index=self.item_index[0]
        if self.item_index[1]==1:#if on the bottom row
            item_index+=5
        if item_index<len(self.use_items):
            self.use_items[item_index].use_item()
            self.exit_state()

class Fading(Gameplay):#fades out and then in
    def __init__(self,game):
        super().__init__(game)
        self.page = 0
        self.render_fade=[self.render_out,self.render_in]
        self.game.game_objects.player.reset_movement()
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
        self.count += 1
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
        self.game.state_stack[-2].render_effect()#render light or dark effects, if exist

    def render_out(self):
        self.fade_surface.set_alpha(int(self.count*(255/self.fade_length)))

    def handle_events(self, input):
        pass

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.npc = npc
        self.print_frame_rate = 3
        self.text_WINDOW_SIZE = (352, 96)
        self.blit_x = int((self.game.WINDOW_SIZE[0]-self.text_WINDOW_SIZE[0])/2)
        self.clean_slate()

        self.conv = self.npc.get_conversation()

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
                if self.letter_frame//self.print_frame_rate < len(self.npc.get_conversation()):
                    self.letter_frame = 10000
                else:
                    self.clean_slate()
                    self.npc.increase_conv_index()
                    self.conv = self.npc.get_conversation()
                    if not self.conv:
                        self.exit_state()

    def exit_state(self):
        super().exit_state()
        self.npc.buisness()

class Facilities(Gameplay):
    def __init__(self, game, npc = None):
        super().__init__(game)
        self.npc = npc
        self.pointer_index = [0,0]#position of box
        self.pointer = Entities.Menu_Arrow()
        self.set_response('welcome')
        self.render_list=[self.blit_frame1]
        self.handle_list=[self.handle_frame1]
        self.select_list=[self.select_frame1]
        self.pointer_list = [self.pointer_frame1]
        self.frame = 1

    def init_canvas(self,size=[64,64]):
        self.surf=[]
        self.bg = self.font.fill_text_bg(size)
        for string in self.actions:
            self.surf.append(self.font.render(text = string))

    def blit_frame1(self):
        for index, surf in enumerate(self.surf):
            self.bg.blit(surf,(30,10+index*10))#
        self.game.screen.blit(self.bg,(280,120))#box position

    def render(self):
        super().render()
        self.render_list[-1]()
        self.pointer_list[-1]()
        self.blit_response()

    def handle_events(self,input):
        self.handle_list[-1](input)

    def set_response(self,text):
        self.respond = self.font.render(text = text)

    def blit_response(self):
        self.game.screen.blit(self.respond,(190,150))

    def pointer_frame1(self):
        self.game.screen.blit(self.pointer.img,(300,130+10*self.pointer_index[1]))#pointer

    def select(self):
        self.select_list[-1]()

    def select_frame1(self):
        pass

    def next_frame(self):#instead of hardcoding it, maybe it can iterate through the number somehow
        self.frame+=1
        self.render_list.append(getattr(self,'blit_frame'+str(self.frame)))
        self.select_list.append(getattr(self,'select_frame'+str(self.frame)))
        self.handle_list.append(getattr(self,'handle_frame'+str(self.frame)))
        self.pointer_list.append(getattr(self,'pointer_frame'+str(self.frame)))

    def previouse_frame(self):
        self.render_list.pop()
        self.select_list.pop()
        self.handle_list.pop()
        self.pointer_list.pop()
        self.frame-=1

    def handle_frame1(self,input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()
            elif input[-1] =='down':
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],len(self.actions)-1)
            elif input[-1] =='up':
                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Smith(Facilities):
    def __init__(self, game, npc):
        super().__init__(game,npc)
        self.actions=['upgrade','enhance','cancel']
        self.init_canvas([64,22*len(self.actions)])#specific for each facility

    def select_frame2(self):
        if self.pointer_index[1] < len(self.actions)-1:#if we select upgrade
            stone_str=self.actions[self.pointer_index[1]]
            self.game.game_objects.player.sword.set_stone(stone_str)
            self.set_response('Now it is ' + self.game.game_objects.player.sword.equip)
        else:#select cancel
            self.previouse_frame()

    def pointer_frame2(self):
        self.pointer_frame1()

    def handle_frame2(self,input):
        self.handle_frame1(input)

    def blit_frame2(self):
        self.blit_frame1()

    def previouse_frame(self):
        super().previouse_frame()
        self.actions=['upgrade','enhance','cancel']
        self.init_canvas([64,22*len(self.actions)])#specific for each facility

    def next_frame(self):
        super().next_frame()
        self.actions=[]
        for index, stones in enumerate(self.game.game_objects.player.sword.stones):
            self.actions.append(stones)
        self.actions.append('cancel')
        self.init_canvas([64,22*len(self.actions)])

    def select_frame1(self):
        if self.pointer_index[1] == 0:#if we select upgrade
            self.upgrade()
        elif self.pointer_index[1] == 1:
            self.next_frame()
        else:#select cancel
            self.exit_state()

    def upgrade(self):
        if self.game.game_objects.player.inventory['Tungsten']>=1:
            self.game.game_objects.player.inventory['Tungsten'] -= 1
            self.game.game_objects.player.sword.dmg+=5
            self.set_response('Now it is better')
        else:#not enough tungsten
            self.set_response('You do not have enought heavy rocks')

class Bank(Facilities):
    def __init__(self, game, npc):
        super().__init__(game,npc)
        self.actions=['withdraw','deposit','cancel']
        self.ammount = 0
        self.init_canvas()

    def blit_frame2(self):
        self.game.screen.blit(self.bg,(280,120))#box position
        self.amount_surf = self.font.render(text = str(self.ammount))
        self.game.screen.blit(self.amount_surf,(310,130))#box position

    def select_frame1(self):#exchane of money
        if self.pointer_index[1]==2:#cancel
            self.exit_state()
        else:#widthdraw or deposit
            self.bg = self.font.fill_text_bg([64,64])
            self.next_frame()

    def select_frame2(self):
        if self.pointer_index[1]==0:#widthdraw
            self.game.game_objects.player.inventory['Amber_Droplet']+=self.ammount
            self.npc.ammount-=self.ammount
        elif self.pointer_index[1]==1:#deposit
            self.game.game_objects.player.inventory['Amber_Droplet']-=self.ammount
            self.npc.ammount+=self.ammount
        self.previouse_frame()

    def pointer_frame2(self):
        pass

    def handle_frame2(self,input):
        if input[0]:#press
            if input[-1] =='down':
                self.ammount -= 1
                self.ammount = max(self.ammount,0)
            elif input[-1] =='up':
                self.ammount += 1
                if self.pointer_index[1]==0:#widthdraw
                    self.ammount = min(self.ammount,self.npc.ammount)
                else:
                    self.ammount = min(self.ammount,self.game.game_objects.player.inventory['Amber_Droplet'])

            elif input[-1] =='right':
                self.ammount += 100
                if self.pointer_index[1]==0:#widthdraw
                    self.ammount = min(self.ammount,self.npc.ammount)
                else:
                    self.ammount = min(self.ammount,self.game.game_objects.player.inventory['Amber_Droplet'])
            elif input[-1] == 'left':
                self.ammount -= 100
                self.ammount = max(self.ammount,0)

            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Soul_essence(Facilities):
    def __init__(self, game):
        super().__init__(game)
        self.actions=['health','spirit','cancel']
        self.cost = 4
        self.init_canvas()

    def select_frame1(self):
        if self.pointer_index[1] == 0:#if we select health
            if self.game.game_objects.player.inventory['Soul_essence'] >= self.cost:
                pos = [self.game.game_objects.player.rect[0],-100]
                heart=Entities.Heart_container(pos,self.game.game_objects)
                self.game.game_objects.loot.add(heart)
                self.game.game_objects.player.inventory['Soul_essence']-=self.cost
        elif self.pointer_index[1] == 1:#if we select spirit
            if self.game.game_objects.player.inventory['Soul_essence'] >= self.cost:
                pos = [self.game.game_objects.player.rect[0],-100]
                spirit=Entities.Spirit_container(pos,self.game.game_objects)
                self.game.game_objects.loot.add(spirit)
                self.game.game_objects.player.inventory['Soul_essence']-=self.cost
        else:#select cancel
            self.exit_state()

class Vendor(Facilities):
    def __init__(self, game, npc):
        super().__init__(game, npc)
        self.letter_frame = 0
        self.init_canvas()
        self.pointer = Entities.Menu_Box()
        self.item_index = [0,0]#pointer of item

    def init_canvas(self):
        self.bg1 = self.font.fill_text_bg([300,200])

        self.items = []
        for item in self.npc.inventory.keys():
            item=getattr(sys.modules[Entities.__name__], item)([0,0],self.game.game_objects)#make the object based on the string
            self.items.append(item)

        self.amber = getattr(sys.modules[Entities.__name__], 'Amber_Droplet')([0,0],self.game.game_objects)#make the object based on the string

        #tempporary to have many items to test scrollingl list
        for i in range(0,3):
            self.items.append(getattr(sys.modules[Entities.__name__], 'Amber_Droplet')([0,0],self.game.game_objects))
        self.items.append(getattr(sys.modules[Entities.__name__], 'Bone')([0,0],self.game.game_objects))

        self.display_number = min(3,len(self.items))#number of items to list
        self.sale_items=self.items[0:self.display_number+1]

        self.buy_sur = self.font.render(text = 'Buy')
        self.cancel_sur= self.font.render(text = 'Cancel')

    def update(self):
        super().update()
        self.letter_frame += 1

    def blit_frame1(self):
        width=self.bg1.get_width()
        self.game.screen.blit(self.bg1,((self.game.WINDOW_SIZE[0]-width)/2,20))
        self.blit_items()
        self.blit_money()
        self.blit_description()

    def blit_frame2(self):
        self.blit_frame1()
        self.bg2.blit(self.buy_sur,(30,10))#
        self.bg2.blit(self.cancel_sur,(30,20))#
        self.game.screen.blit(self.bg2,(280,120))#box position

    def blit_money(self):#blit how much gold we have in inventory
        money = self.game.game_objects.player.inventory['Amber_Droplet']
        count_text = self.font.render(text = str(money))
        self.game.screen.blit(count_text,(200,50))
        self.amber.animation.update()
        self.game.screen.blit(self.amber.image,(190,50))

    def blit_description(self):
        self.conv=self.items[self.item_index[1]].description
        text = self.font.render((272,80), self.conv, int(self.letter_frame//2))
        self.game.screen.blit(text,(190,100))

    def blit_items(self):
        for index, item in enumerate(self.sale_items):
            if index < self.display_number:
                item.animation.update()
                self.game.screen.blit(pygame.transform.scale(item.image,(10,10)),(240,80+20*index))
                #blit cost
                item_name=str(type(item).__name__)
                cost=self.npc.inventory[item_name]
                cost_text = self.font.render(text = str(cost))
                self.game.screen.blit(cost_text,(260,80+20*index))

            else:#the last index
                item.animation.update()
                item.image.set_alpha(100)
                self.game.screen.blit(pygame.transform.scale(item.image,(10,10)),(240,140))

    def pointer_frame1(self):
        self.game.screen.blit(self.pointer.img,(220+20*self.pointer_index[0],60+20*self.pointer_index[1]))#pointer

    def pointer_frame2(self):
        self.game.screen.blit(self.pointer.img,(300,130+10*self.pointer_index[1]))#pointer

    def select_frame1(self):
        self.next_frame()
        self.bg2 = self.font.fill_text_bg([64,32])
        self.item = type(self.items[self.item_index[1]]).__name__
        self.pointer = Entities.Menu_Arrow()

    def select_frame2(self):
        if self.pointer_index[1] == 0:#if we select buy
            self.buy()
        else:
            self.set_response('What do you want?')
        self.previouse_frame()
        self.pointer = Entities.Menu_Box()

    def buy(self):
        if self.game.game_objects.player.inventory['Amber_Droplet']>=self.npc.inventory[self.item]:
            self.game.game_objects.player.inventory[self.item] += 1
            self.game.game_objects.player.inventory['Amber_Droplet']-=self.npc.inventory[self.item]
            self.set_response('Thanks for buying')
        else:#not enough money
            self.set_response('Get loss you poor piece of shit')

    def handle_frame1(self, input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()

            elif input[-1] =='down':
                self.item_index[1] += 1
                self.item_index[1] = min(self.item_index[1],len(self.items)-1)

                if self.pointer_index[1]==2:
                    self.sale_items=self.items[self.item_index[1]-self.display_number+1:self.item_index[1]+self.display_number-1]
                    if self.item_index[1]==len(self.items)-1:
                        return

                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],self.display_number-1)
                self.letter_frame=0

            elif input[-1] =='up':
                self.item_index[1]-=1
                self.item_index[1] = max(self.item_index[1],0)

                if self.pointer_index[1]==0:
                    self.sale_items=self.items[self.item_index[1]:self.item_index[1]+self.display_number+1]
                    if self.item_index[1]==0:
                        return

                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
                self.letter_frame = 0

            elif input[-1]=='a' or input[-1]=='return':
                self.select()

    def handle_frame2(self,input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()

            elif input[-1] =='down':
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],1)
            elif input[-1] =='up':
                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Cutscenes(Gameplay):#basically, this class is not needed but would be nice to have the cutscene classes in a seperate file
    def __init__(self, game,scene):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
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

class Signpost(Gameplay):
    def __init__(self, game,sign_post):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()

        self.page = 0
        self.render_fade=[self.render_in,self.render_out]

        self.sign_post = sign_post
        self.img = sign_post.sprites['bg'][0]#maybe the img should not be in signpost but somewhere more accesable
        self.dir_pos = {'left':[0,150],'up':[100,50],'right':[200,150],'down':[100,300]}

        self.surface = pygame.Surface((int(self.game.WINDOW_SIZE[0]), int(self.game.WINDOW_SIZE[1])), pygame.SRCALPHA, 32).convert_alpha()
        self.surface.fill((0,0,0))

        self.fade = 0
        self.surface.set_alpha(self.fade)

    def render(self):
        super().render()
        self.surface.set_alpha(int(self.fade))
        self.render_fade[self.page]()
        self.game.screen.blit(self.surface,(0, 0))
        self.game.screen.blit(self.img,(0, 0))#blit directly on screen to avoid alpha change on this
        for dir in self.sign_post.directions.keys():
            self.game.screen.blit(self.font.render(text = self.sign_post.directions[dir]),self.dir_pos[dir])

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

class New_ability(Gameplay):#when player obtaines a new ability
    def __init__(self, game,ability):
        super().__init__(game)
        self.page = 0
        self.render_fade=[self.render_in,self.render_out]

        self.img = self.game.game_objects.player.sprites.sprite_dict['main'][ability][0].copy()
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
