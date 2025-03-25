import pygame, sys
import UI_loader
import entities#to load the inventory -> entities_UI?
from states import states_inventory

class BackpackUI():#initialised in UI.py
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.screen = self.game_objects.game.display.make_layer(self.game_objects.game.window_size)
        self.current_page =  InventoryUI(game_objects)

    def update(self):
        self.current_page.update()

    def render(self):
        self.current_page.render()

    def handle_events(self,input):
        self.current_page.handle_events(input)

    def enter_page(self, page):
        self.current_page.on_exit()
        self.current_page = page

class BaseUI():
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects
        self.screen_alpha = kwarg.get('screen_alpha', 0)
        self.letter_frame = 0#for descriptions

    def update(self):
        self.letter_frame += self.game_objects.game.dt
        self.screen_alpha += self.game_objects.game.dt*4
        self.screen_alpha = min(self.screen_alpha,230)

    def render(self):
        pass

    def handle_events(self,input):
        input.processed()        

    def on_exit(self, **kwarg):
        pass        

    def blit_screen(self):#blits everything first to self.game_state.screen. Then blit it to the game screen at the end
        self.game_objects.shaders['alpha']['alpha'] = self.screen_alpha
        self.game_objects.game.display.render(self.game_objects.UI.backpack.screen.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['alpha'])

class InventoryUI(BaseUI):
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg)
        self.state = states_inventory.Items(self)
        self.item_index = [0,0]
        self.iventory_UI = InventoryUI.iventory_UI
        self.texts = InventoryUI.texts
        self.define_blit_positions()

    def pool(game_objects):
        InventoryUI.iventory_UI = getattr(UI_loader, 'Inventory')(game_objects)
        InventoryUI.define_pointer(game_objects)
        InventoryUI.define_botton_texts(game_objects)

    @classmethod
    def define_botton_texts(cls, game_objects):
        convs = ['select','exit','Map','Omamori']
        InventoryUI.texts = []
        for conv in convs:
            InventoryUI.texts.append(game_objects.font.render((32,32), conv, len(conv)))
            #self.texts[-1].fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)

    def define_blit_positions(self):#set positions
        items = self.iventory_UI.items.copy()#a list of empty items
        key_items = self.iventory_UI.key_items#a dict of empty key items
        index = 0
        for key in self.game_objects.player.backpack.inventory.items.keys():#crease the object in inventory and sepeerate between useable items and key items
            item = self.game_objects.player.backpack.inventory.items[key]['item']
            if hasattr(item, 'use_item'):#usable items
                item.rect.topleft = items[index].rect.topleft
                item.number = self.game_objects.player.backpack.inventory.get_quantity(key)#number of items euirepped
                items[index] = item
                index += 1
            else:#key items
                item.rect.topleft = key_items[key.capitalize()].rect.topleft
                item.number = self.game_objects.player.backpack.inventory.get_quantity(key)#number of items euirepped
                key_items[key.capitalize()] = item

        stones = self.iventory_UI.stones#a dict of emppty stones
        for key in self.game_objects.player.sword.stones.keys():#stones player has
            self.game_objects.player.sword.stones[key].rect.topleft = stones[key].rect.topleft
            stones[key] = self.game_objects.player.sword.stones[key]

        self.items = {'sword':list(stones.values()),'key_items':list(key_items.values()),'items':items}#organised items: used to select the item

    @classmethod
    def define_pointer(cls, game_objects):#called everytime we move from one area to another
        size = [16,16]
        cls.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()
        pygame.draw.rect(cls.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        cls.pointer = game_objects.game.display.surface_to_texture(cls.pointer)

    def render(self):
        self.blit_inventory_BG()
        self.blit_inventory()
        self.blit_sword()
        self.blit_pointer()
        self.blit_description()
        self.blit_bottons()
        self.blit_screen()

    def blit_inventory_BG(self):
        self.game_objects.game.display.render(self.iventory_UI.BG, self.game_objects.UI.backpack.screen)#shader render

    def blit_inventory(self):
        for index, item in enumerate(self.items['items'] + self.items['key_items']):#items we can use
            item.animation.update()
            self.game_objects.game.display.render(item.image, self.game_objects.UI.backpack.screen, position = item.rect.topleft)#shader render
            number = self.game_objects.font.render(text = '' + str(item.number))
            self.game_objects.game.display.render(number, self.game_objects.UI.backpack.screen, position = item.rect.center)#shader render
            number.release()

    def blit_sword(self):
        self.iventory_UI.sword.animation.update()
        self.game_objects.game.display.render(self.iventory_UI.sword.image, self.game_objects.UI.backpack.screen, position = self.iventory_UI.sword.rect.topleft)#shader render
        for stone in self.items['sword']:
            stone.animation.update()
            self.game_objects.game.display.render(stone.image, self.game_objects.UI.backpack.screen, position = stone.rect.topleft)#shader render

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer, self.game_objects.UI.backpack.screen, position = self.items[self.state.state_name][self.item_index[0]].rect.topleft)#shader render

    def blit_description(self):
        self.conv = self.items[self.state.state_name][self.item_index[0]].description
        text = self.game_objects.font.render((140,80), self.conv, int(self.letter_frame//2))
        #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(text, self.game_objects.UI.backpack.screen, position = (420,150),shader = self.game_objects.shaders['colour'])#shader render
        text.release()

    def blit_bottons(self):
        for index, button in enumerate(self.iventory_UI.buttons.keys()):
            self.iventory_UI.buttons[button].update()
            self.game_objects.game.display.render(self.iventory_UI.buttons[button].image, self.game_objects.UI.backpack.screen, position = self.iventory_UI.buttons[button].rect.topleft)#shader render
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(self.texts[index], self.game_objects.UI.backpack.screen, position = self.iventory_UI.buttons[button].rect.center,shader = self.game_objects.shaders['colour'])#shader render

    def handle_events(self,input):
        event = input.output()
        input.processed()        
        if event[0]:#press
            if event[-1] == 'select':
                self.game_objects.game.state_manager.exit_state()            
            elif event[-1] == 'rb':#nezt page
                self.iventory_UI.buttons['rb'].currentstate.handle_input('press')
                new_ui = NecklaseUI(self.game_objects, screen_alpha = 230)
                self.game_objects.UI.backpack.enter_page(new_ui)
            elif event[-1] == 'lb':#previouse 
                self.iventory_UI.buttons['lb'].currentstate.handle_input('press')
                new_ui = MapUI(self.game_objects, screen_alpha = 230)
                self.game_objects.UI.backpack.enter_page(new_ui)
            elif event[-1]=='a' or event[-1]=='return':                
                self.iventory_UI.buttons['a'].currentstate.handle_input('press')
                self.use_item()
            self.state.handle_input(input)
            self.letter_frame = 0
        elif event[1]:#release
            if event[-1]=='a' or event[-1]=='return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('release')

    def use_item(self):
        if not hasattr(self.items[self.state.state_name][self.item_index[0]], 'use_item'): return#if it is a item
        if self.items[self.state.state_name][self.item_index[0]].number <= 0: return#if we have more than 0 item
        self.items[self.state.state_name][self.item_index[0]].use_item()
        self.items[self.state.state_name][self.item_index[0]].number -= 1

class NecklaseUI(BaseUI):
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg)        
        self.omamori_UI = NecklaseUI.omamori_UI
        self.pointer = NecklaseUI.pointer
        self.define_blit_positions()        
        self.omamori_index = kwarg.get('omamori_index', 0)
        self.omamori_UI.necklace.set_level(self.game_objects.player.backpack.necklace.level)

    def pool(game_objects):
        NecklaseUI.omamori_UI = getattr(UI_loader, 'Omamori')(game_objects)
        NecklaseUI.define_pointer(game_objects)

    def define_blit_positions(self):
        for key in self.game_objects.player.backpack.necklace.equipped.keys():
            for index, omamori in enumerate(self.game_objects.player.backpack.necklace.equipped[key]):
                pos = omamori.rect.topleft
                self.game_objects.player.backpack.necklace.equipped[key][index].set_pos(pos)

        omamori_dict = self.omamori_UI.inventory#copy all empty ones and then overwrite with the rellavant ones in inventory
        for index, key in enumerate(self.game_objects.player.backpack.necklace.inventory):#the ones in inventory
            pos = self.omamori_UI.inventory[key].rect.topleft
            self.game_objects.player.backpack.necklace.inventory[key].set_pos(pos)
            omamori_dict[key] = self.game_objects.player.backpack.necklace.inventory[key]
        self.omamori_list = list(omamori_dict.values())
        self.omamori_list.sort(key=lambda x: (x.rect.topleft[1], x.rect.topleft[0]))

    @classmethod
    def define_pointer(cls, game_objects, size = [32,32]):#called everytime we move from one area to another
        cls.pointer = pygame.Surface(size, pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(cls.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        cls.pointer = game_objects.game.display.surface_to_texture(cls.pointer)

    def render(self):
        self.blit_omamori_BG()
        self.blit_necklace()
        self.blit_omamori_menu()
        self.blit_pointer()
        self.blit_description()
        self.blit_screen()

    def blit_omamori_BG(self):
        #self.omamori_UI.BG.set_alpha(230)
        self.game_objects.game.display.render(self.omamori_UI.BG, self.game_objects.UI.backpack.screen)

    def blit_omamori_menu(self):
        flattened_list = [item for sublist in list(self.game_objects.player.backpack.necklace.equipped.values()) for item in sublist]

        for omamori in flattened_list + self.omamori_list:
            omamori.animation.update()#update the image
            omamori.render_UI(self.game_objects.UI.backpack.screen)
            self.game_objects.game.display.render(omamori.image, self.game_objects.UI.backpack.screen, position = omamori.rect.topleft)

    def blit_description(self):
        self.conv = self.omamori_list[self.omamori_index].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game_objects.game.display.render(text, self.game_objects.UI.backpack.screen, position = (100,250), shader = self.game_objects.shaders['colour'])
        text.release()

    def blit_necklace(self):
        self.omamori_UI.necklace.animation.update()
        self.game_objects.game.display.render(self.omamori_UI.necklace.image,self.game_objects.UI.backpack.screen, position = self.omamori_UI.necklace.rect.topleft)

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer, self.game_objects.UI.backpack.screen, position = self.omamori_list[self.omamori_index].rect.topleft)

    def handle_events(self,input):
        event = input.output()
        input.processed()              
        if event[0]:#press
            if event[-1] == 'select':
                self.game_objects.game.state_manager.exit_state()  
            elif event[-1] == 'rb':#nezt page
                if self.game_objects.world_state.statistics['kill']:#if we have killed something
                    new_ui = JournalUI(self.game_objects, screen_alpha = 230)
                    self.game_objects.UI.backpack.enter_page(new_ui)                
            elif event[-1] == 'lb':#previouse page
                new_ui = InventoryUI(self.game_objects, screen_alpha = 230)
                self.game_objects.UI.backpack.enter_page(new_ui)                            
            elif event[-1]=='a' or event[-1]=='return':
                self.choose_omamori()

            elif event[-1] =='right':
                self.letter_frame = 0
                self.omamori_index += 1
                self.omamori_index = min(self.omamori_index, len(self.omamori_list)-1)

            elif event[-1] =='left':
                self.letter_frame = 0
                self.omamori_index -= 1
                self.omamori_index = max(0,self.omamori_index)

            elif event[-1] =='down':
                self.letter_frame = 0
                self.omamori_index += 4
                self.omamori_index = min(self.omamori_index, len(self.omamori_list)-1)

            elif event[-1] =='up':
                self.letter_frame = 0
                self.omamori_index -= 4
                self.omamori_index = max(0,self.omamori_index)

    def choose_omamori(self):
        name = type(self.omamori_list[self.omamori_index]).__name__#name of omamori
        if name == 'Omamori': return#if it is an empty omamori. return
        response = self.game_objects.player.backpack.necklace.equip_omamori(name, self.omamori_UI.equipped)
        if not response[0]:#if couldn't eqiup
            new_ui = NecklaseUI_2(self.game_objects, response = response[1], screen_alpha = 230, omamori_index = self.omamori_index)
            self.game_objects.UI.backpack.enter_page(new_ui)    

class NecklaseUI_2(NecklaseUI):#blit potential response from action
    def __init__(self, game_state, **kwarg):
        super().__init__(game_state, **kwarg) 
        self.response = kwarg.get('response', 'No')  
        self.text_window_size = (200, 100) 
        self.text_window = self.game_objects.font.fill_text_bg(self.text_window_size)#TODO
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
        event = input.output()
        input.processed()             
        if event[0]:#press 
            if event[-1]=='a' or event[-1]=='return':
                new_ui = NecklaseUI(self.game_objects)
                self.game_objects.UI.backpack.enter_page(new_ui)                 

class JournalUI(BaseUI):
    def __init__(self, game_sate, **kwarg):
        super().__init__(game_sate, **kwarg)
        self.journal_UI = JournalUI.journal_UI
        self.pointer = JournalUI.pointer
        self.journal_index = [0,0]
        self.enemies = []
        self.enemy_index = self.journal_index.copy()
        self.number = 8 #number of enemies per page
            
        for enemy in self.game_objects.world_state.statistics['kill']:
            self.enemies.append(getattr(sys.modules[entities.__name__], enemy.capitalize())([0,0],self.game_objects))#make the object based on the string

        self.select_enemies()

    def pool(game_objects):
        JournalUI.journal_UI = getattr(UI_loader, 'Journal')(game_objects)
        JournalUI.define_pointer(game_objects)

    def select_enemies(self):
        self.selected_enemies = self.enemies[self.enemy_index[0]:self.enemy_index[0]+self.number:1]

    @classmethod
    def define_pointer(cls, game_objects):#called everytime we move from one area to another
        size = [48,16]
        cls.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(cls.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        cls.pointer = game_objects.game.display.surface_to_texture(cls.pointer)

    def render(self):
        self.blit_journal_BG()
        self.blit_names()
        self.blit_pointer()
        self.blit_enemy()
        self.blit_description()
        self.blit_screen()

    def blit_journal_BG(self):
        #self.journal_UI.BG.set_alpha(230)
        self.game_objects.game.display.render(self.journal_UI.BG, self.game_objects.UI.backpack.screen)

    def blit_names(self):
        for index, enemy in enumerate(self.selected_enemies):
            name = enemy.__class__.__name__
            text = self.game_objects.font.render((152,80), name, 100)
            #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
            self.game_objects.game.display.render(text, self.game_objects.UI.backpack.screen, position = self.journal_UI.name_pos[index])
            text.release()

    def blit_pointer(self):
        pos = [self.journal_UI.name_pos[self.journal_index[0]][0],self.journal_UI.name_pos[self.journal_index[0]][1]-5]#add a offset
        self.game_objects.game.display.render(self.pointer, self.game_objects.UI.backpack.screen, position = pos)

    def blit_enemy(self):
        enemy = self.selected_enemies[self.journal_index[0]]
        enemy.rect.midbottom = self.journal_UI.image_pos#allign based on bottom
        enemy.animation.update()
        self.game_objects.game.display.render(enemy.image, self.game_objects.UI.backpack.screen, position = [enemy.rect.center[0]-enemy.rect.width*0.5,enemy.rect.center[1]-enemy.rect.height*0.5])

    def blit_description(self):
        self.conv = self.selected_enemies[self.journal_index[0]].description
        text = self.game_objects.font.render((152,80), self.conv, int(self.letter_frame//2))
        #text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.display.render(text, self.game_objects.UI.backpack.screen, position = (380,120))
        text.release()

    def handle_events(self,input):
        event = input.output()
        input.processed()            
        if event[0]:#press
            if event[-1] == 'select':
                self.game_objects.game.state_manager.exit_state()        
            elif event[-1] == 'rb':#nezt page
                pass
            elif event[-1] == 'lb':#previouse page
                new_ui = NecklaseUI(self.game_objects, screen_alpha = 230)
                self.game_objects.UI.backpack.enter_page(new_ui)                 
            elif event[-1] =='down':
                self.letter_frame = 0
                self.journal_index[0] += 1
                if self.journal_index[0] == self.number:
                    self.enemy_index[0] += 1
                    self.enemy_index[0] = min(self.enemy_index[0],len(self.enemies)-self.number)
                    self.select_enemies()
                self.journal_index[0] = min(self.journal_index[0],len(self.selected_enemies)-1)

            elif event[-1] =='up':
                self.letter_frame = 0
                self.journal_index[0] -= 1
                if self.journal_index[0] == -1:
                    self.enemy_index[0] -= 1
                    self.enemy_index[0] = max(0,self.enemy_index[0])
                    self.select_enemies()
                self.journal_index[0] = max(0,self.journal_index[0])

class MapUI(BaseUI):
    def __init__(self, game, **kwarg):
        super().__init__(game, **kwarg)
        self.map_UI = MapUI.map_UI

        self.scroll = [0,0]
        self.index = 0
        self.pos = [-0.5*(self.map_UI.BG.width - self.game_objects.game.window_size[0]),-0.5*(self.map_UI.BG.height - self.game_objects.game.window_size[1])]#start offset position

        for object in self.map_UI.objects:
            object.update(self.pos)

    def pool(game_objects):
        MapUI.map_UI = getattr(UI_loader, 'Map')(game_objects)

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
        self.game_objects.game.display.render(self.map_UI.BG, self.game_objects.UI.backpack.screen, position = self.pos)
        for object in self.map_UI.objects:
            self.game_objects.game.display.render(object.image, self.game_objects.UI.backpack.screen, position = object.rect.topleft)
        self.blit_screen()

    def calculate_position(self):
        scroll = [-self.map_UI.objects[self.index].rect.center[0]+self.game_objects.game.window_size[0]*0.5,-self.map_UI.objects[self.index].rect.center[1]+self.game_objects.game.window_size[1]*0.5]
        for object in self.map_UI.objects:
            object.update(scroll)
        self.update_pos(scroll)

    def handle_events(self,input):
        event = input.output()
        input.processed()             
        self.scroll = [-2*event[2]['r_stick'][0], -2*event[2]['r_stick'][1]]#right analog stick

        if event[0]:#press
            if event[-1] == 'select':
                self.exit_state()                
            elif event[-1] == 'rb':#nezt page
                new_ui = InventoryUI(self.game_objects, screen_alpha = 230)
                self.game_objects.UI.backpack.enter_page(new_ui)               
            elif event[-1] == 'right':#should it be left analogue stick?
                self.map_UI.objects[self.index].currentstate.set_animation_name('idle')
                self.index += 1
                self.index = min(self.index,len(self.map_UI.objects)-1)
                self.map_UI.objects[self.index].currentstate.set_animation_name('equip')
                self.calculate_position()
            elif event[-1] == 'left':#should it be left analogue stick?
                self.map_UI.objects[self.index].currentstate.set_animation_name('idle')
                self.index -= 1
                self.index = max(0,self.index)
                self.map_UI.objects[self.index].currentstate.set_animation_name('equip')
                self.calculate_position()
            elif event[-1] == 'a':#when pressing a
                self.map_UI.objects[self.index].activate()#open the local map. I guess it should be a new state

    def exit_state(self):
        self.game_objects.game.state_manager.exit_state()  
        for object in self.map_UI.objects:
            object.revert()
