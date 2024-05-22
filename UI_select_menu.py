import pygame, sys
import UI_loader
import Entities#to load the inventory -> entities_UI?
import states_inventory

class Select_menu():
    def __init__(self, game_state, **kwarg):
        self.game_state = game_state
        self.game_objects = game_state.game.game_objects
        self.game_state.screen_alpha = kwarg.get('screen_alpha', 0)

    def enter_state(self, newstate, **kwarg):
        self.game_state.state.append(getattr(sys.modules[__name__], newstate)(self.game_state, **kwarg))

    def update(self):
        self.letter_frame += self.game_objects.game.dt
        self.game_state.screen_alpha += self.game_objects.game.dt*4
        self.game_state.screen_alpha = min(self.game_state.screen_alpha,230)

    def render(self):
        pass

    def handle_events(self,input):
        pass

    def exit_state(self):                
        self.game_state.screen.release()
        self.game_state.exit_state()

    def previous_state(self):
        self.game_state.state.pop()

    def blit_screen(self):#blits everything first to self.game_state.screen. Then blit it to the game screen at the end
        self.game_state.shader['alpha'] = self.game_state.screen_alpha
        self.game_objects.game.display.render(self.game_state.screen.texture, self.game_objects.game.screen, shader = self.game_state.shader)

class Inventory(Select_menu):
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg)
        self.iventory_UI = UI_loader.UI_loader(self.game_objects,'inventory')
        self.letter_frame = 0#for description
        self.state = states_inventory.Items(self)
        self.item_index = [0,0]

        self.define_blit_positions()
        self.define_pointer()
        self.define_botton_texts()

    def define_botton_texts(self):
        convs = ['select','exit','Map','Omamori']
        self.texts = []
        for conv in convs:
            self.texts.append(self.game_objects.font.render((32,32), conv, len(conv)))
            #self.texts[-1].fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)

    def define_blit_positions(self):#set positions
        items = self.iventory_UI.items.copy()#a list of empty items
        key_items = self.iventory_UI.key_items#a dict of empty key items
        index = 0
        for key in self.game_objects.player.inventory.keys():#crease the object in inventory and sepeerate between useable items and key items
            item = getattr(sys.modules[Entities.__name__], key)([0,0],self.game_objects)#make the object based on the string
            if hasattr(item, 'use_item'):
                item.rect.topleft = items[index].rect.topleft
                item.number = self.game_objects.player.inventory[key]#number of items euirepped
                items[index] = item
                index += 1
            else:
                item.rect.topleft = key_items[key].rect.topleft
                item.number = self.game_objects.player.inventory[key]#number of items euirepped
                key_items[key] = item

        stones = self.iventory_UI.stones#a dict of emppty stones
        for key in self.game_objects.player.sword.stones.keys():
            self.game_objects.player.sword.stones[key].rect.topleft = stones[key].rect.topleft
            stones[key] = self.game_objects.player.sword.stones[key]

        self.items = {'sword':list(stones.values()),'key_items':list(key_items.values()),'items':items}#organised items: used to select the item

    def define_pointer(self,size = [16,16]):#called everytime we move from one area to another
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        self.pointer = self.game_objects.game.display.surface_to_texture(self.pointer)

    def render(self):
        self.blit_inventory_BG()
        self.blit_inventory()
        self.blit_sword()
        self.blit_pointer()
        self.blit_description()
        self.blit_bottons()
        self.blit_screen()

    def blit_inventory_BG(self):
        self.game_objects.game.display.render(self.iventory_UI.BG, self.game_state.screen)#shader render

    def blit_inventory(self):
        for index, item in enumerate(self.items['items'] + self.items['key_items']):#items we can use
            item.animation.update()
            self.game_objects.game.display.render(item.image, self.game_state.screen, position = item.rect.topleft)#shader render
            number = self.game_objects.font.render(text = str(item.number))
            self.game_objects.game.display.render(number, self.game_state.screen, position = item.rect.center)#shader render
            number.release()

    def blit_sword(self):
        self.iventory_UI.sword.animation.update()
        self.game_objects.game.display.render(self.iventory_UI.sword.image, self.game_state.screen, position = self.iventory_UI.sword.rect.topleft)#shader render
        for stone in self.items['sword']:
            stone.animation.update()
            self.game_objects.game.display.render(stone.image, self.game_state.screen, position = stone.rect.topleft)#shader render

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer, self.game_state.screen, position = self.items[self.state.state_name][self.item_index[0]].rect.topleft)#shader render

    def blit_description(self):
        self.conv = self.items[self.state.state_name][self.item_index[0]].description
        text = self.game_objects.font.render((140,80), self.conv, int(self.letter_frame//2))
        #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(text, self.game_state.screen, position = (420,150),shader = self.game_objects.shaders['colour'])#shader render
        text.release()

    def blit_bottons(self):
        for index, button in enumerate(self.iventory_UI.buttons.keys()):
            self.iventory_UI.buttons[button].update()
            self.game_objects.game.display.render(self.iventory_UI.buttons[button].image, self.game_state.screen, position = self.iventory_UI.buttons[button].rect.topleft)#shader render
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(self.texts[index], self.game_state.screen, position = self.iventory_UI.buttons[button].rect.center,shader = self.game_objects.shaders['colour'])#shader render

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                self.iventory_UI.buttons['rb'].currentstate.handle_input('press')
                self.enter_state('Omamori', screen_alpha = 230)
            elif input[-1] == 'lb':#previouse page
                self.iventory_UI.buttons['lb'].currentstate.handle_input('press')
                self.enter_state('Map', screen_alpha = 230)
            elif input[-1]=='a' or input[-1]=='return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('press')
                self.use_item()
            self.state.handle_input(input)
            self.letter_frame = 0
        elif input[1]:#release
            if input[-1]=='a' or input[-1]=='return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('release')

    def use_item(self):
        if not hasattr(self.items[self.state.state_name][self.item_index[0]], 'use_item'): return#if it is a item
        if self.items[self.state.state_name][self.item_index[0]].number <= 0: return#if we have more than 0 item
        self.items[self.state.state_name][self.item_index[0]].use_item()
        self.items[self.state.state_name][self.item_index[0]].number -= 1

class Omamori(Select_menu):
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg)
        self.omamori_UI = UI_loader.UI_loader(self.game_objects,'omamori')
        self.letter_frame = 0#for description
        self.define_blit_positions()
        self.define_pointer()
        self.omamori_index = kwarg.get('omamori_index', 0)
        self.omamori_UI.necklace.set_level(self.game_objects.player.omamoris.level)

    def define_blit_positions(self):
        for key in self.game_objects.player.omamoris.equipped.keys():
            for index, omamori in enumerate(self.game_objects.player.omamoris.equipped[key]):
                pos = omamori.rect.topleft
                self.game_objects.player.omamoris.equipped[key][index].set_pos(pos)

        omamori_dict = self.omamori_UI.inventory#copy all empty ones and then overwrite with the rellavant ones in inventory
        for index, key in enumerate(self.game_objects.player.omamoris.inventory):#the ones in inventory
            pos = self.omamori_UI.inventory[key].rect.topleft
            self.game_objects.player.omamoris.inventory[key].set_pos(pos)
            omamori_dict[key] = self.game_objects.player.omamoris.inventory[key]
        self.omamori_list = list(omamori_dict.values())
        self.omamori_list.sort(key=lambda x: (x.rect.topleft[1], x.rect.topleft[0]))

    def define_pointer(self,size = [32,32]):#called everytime we move from one area to another
        self.pointer = pygame.Surface(size, pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        self.pointer = self.game_objects.game.display.surface_to_texture(self.pointer)

    def render(self):
        self.blit_omamori_BG()
        self.blit_necklace()
        self.blit_omamori_menu()
        self.blit_pointer()
        self.blit_description()
        self.blit_screen()

    def blit_omamori_BG(self):
        #self.omamori_UI.BG.set_alpha(230)
        self.game_objects.game.display.render(self.omamori_UI.BG, self.game_state.screen)

    def blit_omamori_menu(self):
        flattened_list = [item for sublist in list(self.game_objects.player.omamoris.equipped.values()) for item in sublist]

        for omamori in flattened_list + self.omamori_list:
            omamori.animation.update()#update the image
            omamori.render_UI(self.game_state.screen)
            self.game_objects.game.display.render(omamori.image, self.game_state.screen, position = omamori.rect.topleft)

    def blit_description(self):
        self.conv = self.omamori_list[self.omamori_index].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(text, self.game_state.screen, position = (100,250), shader = self.game_objects.shaders['colour'])
        text.release()

    def blit_necklace(self):
        self.omamori_UI.necklace.animation.update()
        self.game_objects.game.display.render(self.omamori_UI.necklace.image,self.game_state.screen, position = self.omamori_UI.necklace.rect.topleft)

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer, self.game_state.screen, position = self.omamori_list[self.omamori_index].rect.topleft)

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                if self.game_objects.world_state.statistics['kill']:#if we have killed something
                    self.enter_state('Journal', screen_alpha = 230)
            elif input[-1] == 'lb':#previouse page
                self.previous_state()
            elif input[-1]=='a' or input[-1]=='return':
                self.choose_omamori()

            elif input[-1] =='right':
                self.letter_frame = 0
                self.omamori_index += 1
                self.omamori_index = min(self.omamori_index, len(self.omamori_list)-1)

            elif input[-1] =='left':
                self.letter_frame = 0
                self.omamori_index -= 1
                self.omamori_index = max(0,self.omamori_index)

            elif input[-1] =='down':
                self.letter_frame = 0
                self.omamori_index += 4
                self.omamori_index = min(self.omamori_index, len(self.omamori_list)-1)

            elif input[-1] =='up':
                self.letter_frame = 0
                self.omamori_index -= 4
                self.omamori_index = max(0,self.omamori_index)

    def choose_omamori(self):
        name = type(self.omamori_list[self.omamori_index]).__name__#name of omamori
        if name == 'Omamori': return#if it is an empty omamori. return
        response = self.game_objects.player.omamoris.equip_omamori(name, self.omamori_UI.equipped)
        if not response[0]:#if couldn't eqiup
            self.enter_state('Omamori_2', response = response[1], screen_alpha = 230, omamori_index = self.omamori_index)

class Omamori_2(Omamori):#blit potential response from action
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg) 
        self.response = kwarg.get('response', 'No')  
        self.text_window_size = (200,100) 
        self.text_window = self.game_objects.font.fill_text_bg(self.text_window_size)
        self.layer = self.game_objects.game.display.make_layer(self.game_objects.game.window_size)#TODO
    
    def render(self):
        self.blit_omamori_BG()
        self.blit_necklace()
        self.blit_omamori_menu()
        self.blit_description()
        self.blit_screen()
        self.tint_screen()
        self.blit_message()

    def tint_screen(self):#blits everything first to self.game_state.screen. Then blit it to the game screen at the end
        self.layer.clear(0, 0, 0, 100)
        self.game_objects.game.display.render(self.layer.texture, self.game_objects.game.screen)

    def blit_message(self):
        text = self.game_objects.font.render(self.text_window_size, self.response, int(self.letter_frame//2))
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(self.text_window, self.game_objects.game.screen, position = (280,120))#shader render            
        self.game_objects.game.display.render(text, self.game_objects.game.screen, position = (300,170), shader = self.game_objects.shaders['colour'])
        text.release()        

    def handle_events(self,input):
        if input[0]:#press 
            if input[-1]=='a' or input[-1]=='return':
               self.previous_state()

class Journal(Select_menu):
    def __init__(self, game_sate, **kwarg):
        super().__init__(game_sate, **kwarg)
        self.journal_UI = UI_loader.UI_loader(self.game_objects,'journal')
        self.letter_frame = 0
        self.journal_index = [0,0]
        self.enemies = []
        self.enemy_index = self.journal_index.copy()
        self.number = 8 #number of enemies per page

        for enemy in self.game_objects.world_state.statistics['kill']:
            self.enemies.append(getattr(sys.modules[Entities.__name__], enemy.capitalize())([0,0],self.game_objects))#make the object based on the string

        self.select_enemies()
        self.define_pointer()

    def select_enemies(self):
        self.selected_enemies = self.enemies[self.enemy_index[0]:self.enemy_index[0]+self.number:1]

    def define_pointer(self):#called everytime we move from one area to another
        size = [48,16]
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        self.pointer = self.game_objects.game.display.surface_to_texture(self.pointer)

    def render(self):
        self.blit_journal_BG()
        self.blit_names()
        self.blit_pointer()
        self.blit_enemy()
        self.blit_description()
        self.blit_screen()

    def blit_journal_BG(self):
        #self.journal_UI.BG.set_alpha(230)
        self.game_objects.game.display.render(self.journal_UI.BG, self.game_state.screen)

    def blit_names(self):
        for index, enemy in enumerate(self.selected_enemies):
            name = enemy.__class__.__name__
            text = self.game_objects.font.render((152,80), name, 100)
            #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game_objects.game.display.render(text, self.game_state.screen, position = self.journal_UI.name_pos[index])
            text.release()

    def blit_pointer(self):
        pos = [self.journal_UI.name_pos[self.journal_index[0]][0],self.journal_UI.name_pos[self.journal_index[0]][1]-5]#add a offset
        self.game_objects.game.display.render(self.pointer, self.game_state.screen, position = pos)

    def blit_enemy(self):
        enemy = self.selected_enemies[self.journal_index[0]]
        enemy.rect.midbottom = self.journal_UI.image_pos#allign based on bottom
        enemy.animation.update()
        self.game_objects.game.display.render(enemy.image, self.game_state.screen, position = [enemy.rect.center[0]-enemy.rect.width*0.5,enemy.rect.center[1]-enemy.rect.height*0.5])

    def blit_description(self):
        self.conv = self.selected_enemies[self.journal_index[0]].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.display.render(text, self.game_state.screen, position = (380,120))
        text.release()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                pass
            elif input[-1] == 'lb':#previouse page
                self.previous_state()
            elif input[-1] =='down':
                self.letter_frame = 0
                self.journal_index[0] += 1
                if self.journal_index[0] == self.number:
                    self.enemy_index[0] += 1
                    self.enemy_index[0] = min(self.enemy_index[0],len(self.enemies)-self.number)
                    self.select_enemies()
                self.journal_index[0] = min(self.journal_index[0],len(self.selected_enemies)-1)

            elif input[-1] =='up':
                self.letter_frame = 0
                self.journal_index[0] -= 1
                if self.journal_index[0] == -1:
                    self.enemy_index[0] -= 1
                    self.enemy_index[0] = max(0,self.enemy_index[0])
                    self.select_enemies()
                self.journal_index[0] = max(0,self.journal_index[0])

class Map(Select_menu):
    def __init__(self, game, **kwarg):
        super().__init__(game, **kwarg)
        self.map_UI = UI_loader.UI_loader(self.game_objects,'map')

        self.scroll = [0,0]
        self.index = 0
        self.pos = [-0.5*(self.map_UI.BG.width - self.game_objects.game.window_size[0]),-0.5*(self.map_UI.BG.height - self.game_objects.game.window_size[1])]#start offset position

        for object in self.map_UI.objects:
            object.update(self.pos)

    def update(self):
        self.update_pos(self.scroll)
        self.limit_pos()
        for object in self.map_UI.objects:
            object.update(self.scroll)

    def update_pos(self,scroll):
        self.pos = [self.pos[0]+scroll[0],self.pos[1]+scroll[1]]

    def limit_pos(self):
        #self.pos[0] = min(0,self.pos[0])
        #self.pos[0] = max(self.game.window_size[0] - self.map_UI.BG.get_width(),self.pos[0])
        #self.pos[1] = min(0,self.pos[1])
        #self.pos[1] = max(self.game.window_size[1] - self.map_UI.BG.get_height(),self.pos[1])
        if self.pos[0] > 0:
            self.pos[0] = 0
            self.scroll[0] = 0
        elif self.pos[0] < self.game_objects.game.window_size[0] - self.map_UI.BG.width:
            self.pos[0] = self.game_objects.game.window_size[0] - self.map_UI.BG.width
            self.scroll[0] = 0
        if self.pos[1] > 0:
            self.pos[1] = 0
            self.scroll[1] = 0
        elif self.pos[1] < self.game_objects.game.window_size[1] - self.map_UI.BG.height:
            self.pos[1] = self.game_objects.game.window_size[1] - self.map_UI.BG.height
            self.scroll[1] = 0

    def render(self):
        self.game_objects.game.display.render(self.map_UI.BG, self.game_state.screen, position = self.pos)
        for object in self.map_UI.objects:
            self.game_objects.game.display.render(object.image, self.game_state.screen, position = object.rect.topleft)
        self.blit_screen()

    def calculate_position(self):
        scroll = [-self.map_UI.objects[self.index].rect.center[0]+self.game_objects.game.window_size[0]*0.5,-self.map_UI.objects[self.index].rect.center[1]+self.game_objects.game.window_size[1]*0.5]
        for object in self.map_UI.objects:
            object.update(scroll)
        self.update_pos(scroll)

    def handle_events(self,input):
        self.scroll = [-2*input[2]['r_stick'][0],-2*input[2]['r_stick'][1]]#right analog stick

        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb':#nezt page
                self.previous_state()
            elif input[-1] == 'right':#should it be left analogue stick?
                self.map_UI.objects[self.index].currentstate.set_animation_name('idle')
                self.index += 1
                self.index = min(self.index,len(self.map_UI.objects)-1)
                self.map_UI.objects[self.index].currentstate.set_animation_name('equip')
                self.calculate_position()
            elif input[-1] == 'left':#should it be left analogue stick?
                self.map_UI.objects[self.index].currentstate.set_animation_name('idle')
                self.index -= 1
                self.index = max(0,self.index)
                self.map_UI.objects[self.index].currentstate.set_animation_name('equip')
                self.calculate_position()
            elif input[-1] == 'a':#when pressing a
                self.map_UI.objects[self.index].activate()#open the local map. I guess it should be a new state

    def exit_state(self):
        super().exit_state()
        for object in self.map_UI.objects:
            object.revert()
