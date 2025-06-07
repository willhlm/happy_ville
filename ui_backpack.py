import pygame, sys
import UI_loader
import entities#used for enemies in journal
from entities_UI import InventoryPointer

class BaseUI():
    def __init__(self, game_objects, **kwarg):
        self.game_objects = game_objects

    def update(self):
        self.letter_frame += self.game_objects.game.dt
        self.screen_alpha += self.game_objects.game.dt*4
        self.screen_alpha = min(self.screen_alpha, 230)

    def render(self):
        pass

    def handle_events(self,input):
        input.processed()

    def on_exit(self, **kwarg):
        pass

    def on_enter(self, **kwarg):
        self.screen_alpha = kwarg.get('screen_alpha', 0)
        self.letter_frame = 0#for descriptions

    def blit_screen(self):#blits everything first to self.game_state.screen. Then blit it to the game screen at the end
        self.game_objects.shaders['alpha']['alpha'] = self.screen_alpha
        self.game_objects.game.display.render(self.game_objects.UI.screen.texture, self.game_objects.game.screen, shader = self.game_objects.shaders['alpha'])

class InventoryUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.iventory_UI = getattr(UI_loader, 'Inventory')(game_objects)
        self.selected_container = self.iventory_UI.containers[0]#initial default container

        self.pointer = InventoryPointer([0,0], game_objects)
        self.define_botton_texts(game_objects)

    def define_botton_texts(self, game_objects):
        convs = ['select','exit','Map','Omamori']
        self.texts = []
        for conv in convs:
            self.texts.append(game_objects.font.render((32,32), conv, len(conv)))

    def render(self):
        self.game_objects.UI.screen.clear(0, 0, 0, 0)#clear the screen
        self.blit_inventory_BG()
        self.blit_inventory()
        self.blit_sword()
        self.blit_pointer()
        self.blit_description()
        self.blit_bottons()
        self.blit_screen()

    def blit_inventory_BG(self):
        self.game_objects.game.display.render(self.iventory_UI.BG, self.game_objects.UI.screen)#shader render

    def blit_inventory(self):
        for container in self.iventory_UI.containers:#blit all containers
            self.game_objects.game.display.render(container.image, self.game_objects.UI.screen, position = container.rect.topleft)#shader render

        for key in self.game_objects.player.backpack.inventory.items.keys():#blit the items there is in inventory
            item = self.game_objects.player.backpack.inventory.get_item(key)    
            item.animation.update()
            self.game_objects.game.display.render(item.image, self.game_objects.UI.screen, position = self.iventory_UI.items[key])#shader render
            
            quantity = self.game_objects.player.backpack.inventory.get_quantity(key)
            number = self.game_objects.font.render(text = '' + str(quantity))
            topleft = self.iventory_UI.items[key]
            self.game_objects.game.display.render(number, self.game_objects.UI.screen, position = [topleft[0] + item.rect[2], topleft[1] + item.rect[3]])#shader render
            number.release()

    def blit_sword(self):
        self.iventory_UI.items['sword'].animation.update()
        self.game_objects.game.display.render(self.iventory_UI.items['sword'].image, self.game_objects.UI.screen, position = self.iventory_UI.items['sword'].rect.topleft)#shader render
  
    def blit_pointer(self):
        pos = self.selected_container.rect.topleft#should change this index
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.UI.screen, position = pos)#shader render

    def blit_description(self):
        item_name = self.selected_container.get_item()
        item = self.game_objects.player.backpack.inventory.get_item(item_name)
        if item:#if the item is in the inventory
            self.conv = item.description
            text = self.game_objects.font.render((140,80), self.conv, int(self.letter_frame//2))
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(text, self.game_objects.UI.screen, position = (420,150),shader = self.game_objects.shaders['colour'])#shader render
            text.release()

    def blit_bottons(self):
        for index, button in enumerate(self.iventory_UI.buttons.keys()):
            self.iventory_UI.buttons[button].update()
            self.game_objects.game.display.render(self.iventory_UI.buttons[button].image, self.game_objects.UI.screen, position = self.iventory_UI.buttons[button].rect.topleft)#shader render
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(self.texts[index], self.game_objects.UI.screen, position = self.iventory_UI.buttons[button].rect.center,shader = self.game_objects.shaders['colour'])#shader render

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'select':
                self.game_objects.game.state_manager.exit_state()
            elif event[-1] == 'rb':#nezt page
                self.iventory_UI.buttons['rb'].currentstate.handle_input('press')
                self.game_objects.UI.set_ui('radna', screen_alpha = 230)
            elif event[-1] == 'lb':#previouse
                self.iventory_UI.buttons['lb'].currentstate.handle_input('press')
                self.game_objects.UI.set_ui('map', screen_alpha = 230)
            elif event[-1]=='a' or event[-1]=='return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('press')
                self.use_item()
            self.letter_frame = 0
        elif event[1]:#release
            if event[-1]=='a' or event[-1]=='return':
                self.iventory_UI.buttons['a'].currentstate.handle_input('release')

        if event[2]['l_stick'][1] < 0:  # up
            next_container = self.find_closest_position('up')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0
        elif event[2]['l_stick'][1] > 0:  # down
            next_container = self.find_closest_position('down')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0
        elif event[2]['l_stick'][0] < 0:  # left
            next_container = self.find_closest_position('left')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0
        elif event[2]['l_stick'][0] > 0:  # right
            next_container = self.find_closest_position('right')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0

    def find_closest_position(self, direction):
        current = self.selected_container.rect
        best = None
        best_score = float('inf')

        for container in self.iventory_UI.containers:
            if container == self.selected_container:
                continue
            target = container.rect

            dx = target.centerx - current.centerx
            dy = target.centery - current.centery

            # Check direction and filter candidates
            if direction == 'up' and dy >= 0: continue
            if direction == 'down' and dy <= 0: continue
            if direction == 'left' and dx >= 0: continue
            if direction == 'right' and dx <= 0: continue

            # Prioritize closest in direction
            distance = dx**2 + dy**2
            angle_priority = abs(dx if direction in ('up', 'down') else dy)

            score = distance + angle_priority * 0.5  # fine-tune weighting
            if score < best_score:
                best_score = score
                best = container

        return best

    def use_item(self):
        item_name = self.selected_container.get_item()
        item = self.iventory_UI.items.get('item_name', False)

        if not hasattr(item, 'use_item'): return#if it is a item that cannot be used
        if self.game_objects.player.backpack.inventory.get_quantity(item_name) <= 0: return#if we have more than 0 item
        item.use_item()
        self.game_objects.player.backpack.inventory.remove_item(item_name, 1)#remove one item from the inventory

class RadnaUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.radna_UI = getattr(UI_loader, 'Radna')(game_objects)
        self.pointer = InventoryPointer([0,0], game_objects)
        self.selected_container = self.radna_UI.containers[0]#initial default container

    def render(self):
        self.game_objects.UI.screen.clear(0, 0, 0, 0)#clear the screen
        self.blit_BG()
        self.blit_hand()
        self.blit_containers()
        self.blit_radnas()
        self.blit_rings()        
        self.blit_pointer()
        self.blit_description()
        self.blit_screen()

    def blit_BG(self):
        self.game_objects.game.display.render(self.radna_UI.BG, self.game_objects.UI.screen)#shader render

    def blit_containers(self):
        for container in self.radna_UI.containers:#blit all containers
            self.game_objects.game.display.render(container.image, self.game_objects.UI.screen, position = container.rect.topleft)#shader render

        for container in self.radna_UI.equipped_containers.values():#blit all containers
            self.game_objects.game.display.render(container.image, self.game_objects.UI.screen, position = container.rect.topleft)#shader render

    def blit_radnas(self):
        for key in self.game_objects.player.backpack.necklace.inventory.keys():#blit the radnas there is in inventory
            item = self.game_objects.player.backpack.necklace.get_radna(key)           
            self.game_objects.shaders['colour']['colour'] = (0,0,0,255)#item.shader toggle sbetween colour and None                   
            self.game_objects.game.display.render(item.image, self.game_objects.UI.screen, position = self.radna_UI.items[key], shader = item.shader)#shader render        

        for finger in self.game_objects.player.backpack.necklace.equipped.keys():#blit the equipped radnas
            ring = self.game_objects.player.backpack.necklace.rings[finger]            
            self.game_objects.game.display.render(ring.radna.image, self.game_objects.UI.screen, position = self.radna_UI.equipped_containers[finger].rect.topleft)#shader render        

    def blit_rings(self): 
        for key in self.game_objects.player.backpack.necklace.rings.keys():#blit the rings there is in inventory
            ring = self.game_objects.player.backpack.necklace.get_ring(key)
            ring.animation.update()            
            self.game_objects.game.display.render(ring.image, self.game_objects.UI.screen, position = self.radna_UI.rings[key])#shader render        

    def blit_pointer(self):
        pos = self.selected_container.rect.topleft
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.UI.screen, position = pos)#shader render        

    def blit_hand(self):
        self.radna_UI.items['hand'].animation.update()
        self.game_objects.shaders['colour']['colour'] = (0,0,0,255)
        self.game_objects.game.display.render(self.radna_UI.items['hand'].image, self.game_objects.UI.screen, position = self.radna_UI.items['hand'].rect.topleft,shader = self.game_objects.shaders['colour'])#shader render

    def blit_description(self):
        item_name = self.selected_container.get_item()
        item = self.game_objects.player.backpack.necklace.get_radna(item_name)
        if item:#if the item is in the inventory
            self.dark(item)#blit a dark radna at the equippable position
            self.conv = item.description
            text = self.game_objects.font.render((140,80), self.conv, int(self.letter_frame//2))
            self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
            self.game_objects.game.display.render(text, self.game_objects.UI.screen, position = (320,220),shader = self.game_objects.shaders['colour'])#shader render
            text.release()

    def dark(self, item):        
        if item.entity: return#if it is equpped
        slot = self.game_objects.player.backpack.necklace.check_position(item)#blit a dark radna at this potsion
        if not slot: return
        self.game_objects.shaders['colour']['colour'] = (0,0,0,255)
        self.game_objects.game.display.render(item.image, self.game_objects.UI.screen, position =self.radna_UI.equipped_containers[slot].rect.topleft,shader = self.game_objects.shaders['colour'])#shader render           

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'select':
                self.game_objects.game.state_manager.exit_state()
            elif event[-1] == 'rb':#nezt page
                #self.radna_UI.buttons['rb'].currentstate.handle_input('press')
                self.game_objects.UI.set_ui('journal', screen_alpha = 230)
            elif event[-1] == 'lb':#previouse
                #self.radna_UI.buttons['lb'].currentstate.handle_input('press')
                self.game_objects.UI.set_ui('inventory', screen_alpha = 230)
            elif event[-1]=='a' or event[-1]=='return':
                #self.radna_UI.buttons['a'].currentstate.handle_input('press')
                self.use_item()
            self.letter_frame = 0
        elif event[1]:#release
            if event[-1]=='a' or event[-1]=='return':
                pass
                #self.radna_UI.buttons['a'].currentstate.handle_input('release')

        if event[2]['l_stick'][1] < 0:  # up
            next_container = self.find_closest_position('up')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0
        elif event[2]['l_stick'][1] > 0:  # down
            next_container = self.find_closest_position('down')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0
        elif event[2]['l_stick'][0] < 0:  # left
            next_container = self.find_closest_position('left')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0
        elif event[2]['l_stick'][0] > 0:  # right
            next_container = self.find_closest_position('right')
            if next_container:
                self.selected_container = next_container
                self.letter_frame = 0

    def find_closest_position(self, direction):
        current = self.selected_container.rect
        best = None
        best_score = float('inf')

        for container in self.radna_UI.containers:
            if container == self.selected_container:
                continue
            target = container.rect

            dx = target.centerx - current.centerx
            dy = target.centery - current.centery

            # Check direction and filter candidates
            if direction == 'up' and dy >= 0: continue
            if direction == 'down' and dy <= 0: continue
            if direction == 'left' and dx >= 0: continue
            if direction == 'right' and dx <= 0: continue

            # Prioritize closest in direction
            distance = dx**2 + dy**2
            angle_priority = abs(dx if direction in ('up', 'down') else dy)

            score = distance + angle_priority * 0.5  # fine-tune weighting
            if score < best_score:
                best_score = score
                best = container

        return best

    def use_item(self):
        item_name = self.selected_container.get_item()
        new_radna = self.game_objects.player.backpack.necklace.get_radna(item_name)       
        if not new_radna: return#if there is not in inventory
        if not new_radna.entity:#if it has an owner, i.e. equipped           
            self.game_objects.player.backpack.necklace.equip_item(new_radna)
        else:
            self.game_objects.player.backpack.necklace.remove_item(new_radna)

class JournalUI(BaseUI):
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.journal_UI = getattr(UI_loader, 'Journal')(game_objects)
        self.define_pointer(game_objects)
        self.journal_index = [0,0]
        self.enemies = []
        self.enemy_index = self.journal_index.copy()
        self.number = 8 #number of enemies per page

        self.define_enemies()
        self.select_enemies()

    def on_enter(self):
        self.define_enemies()
        self.select_enemies()

    def define_enemies(self):
        for enemy in self.game_objects.world_state.statistics['kill']:
            self.enemies.append(getattr(sys.modules[entities.__name__], enemy.capitalize())([0,0],self.game_objects))#make the object based on the string

    def select_enemies(self):
        self.selected_enemies = self.enemies[self.enemy_index[0]:self.enemy_index[0]+self.number:1]

    def define_pointer(self, game_objects):#called everytime we move from one area to another
        size = [48,16]
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)
        self.pointer = game_objects.game.display.surface_to_texture(self.pointer)

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

class MapUI(BaseUI):#local maps
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.map_UIs = {'nordveden': getattr(UI_loader, 'NordvedenMap')(game_objects),'dark_forest': getattr(UI_loader, 'DarkforestMap')(game_objects)}        

    def on_enter(self, **kwarg):
        super().on_enter(**kwarg)
        self.map_UI = self.map_UIs[kwarg.get('map', self.game_objects.map.biome_name)]#load the map the player is in
        self.selected_container = self.map_UI.objects[0]#initial default container

    def update(self):
        self.selected_container.update()#make it move

    def render(self):        
        self.game_objects.UI.screen.clear(0, 0, 0, 0)#clear the screen
        self.game_objects.game.display.render(self.map_UI.BG, self.game_objects.UI.screen, position = [0,0])
        for object in self.map_UI.objects:
            object.draw(self.game_objects.UI.screen)#draw the object. If it is selected, draw it with a different colour
        self.blit_screen()

    def handle_events(self,input):
        event = input.output()
        input.processed()        

        if event[0]:#press
            if event[-1] == 'select':
                self.exit_state()
            elif event[-1] == 'rb':#nezt page
                self.game_objects.UI.set_ui('inventory', screen_alpha = 230)

            elif event[-1] == 'a':#nezt page
                map_name = self.selected_container.activate()#open the local map. I guess it should be a new state
                self.game_objects.UI.set_ui('map', screen_alpha = 230, map = map_name)  

            elif event[-1] == 'x':#when pressing a
                self.game_objects.UI.set_ui('worldmap', screen_alpha = 230)#world map

        if event[2]['l_stick'][1] < 0:  # up
            next_container = self.find_closest_position('up')
            if next_container:
                self.selected_container.reset()#reset the position of the container
                self.selected_container = next_container
        elif event[2]['l_stick'][1] > 0:  # down
            next_container = self.find_closest_position('down')
            if next_container:
                self.selected_container.reset()#reset the position of the container
                self.selected_container = next_container
        elif event[2]['l_stick'][0] < 0:  # left
            next_container = self.find_closest_position('left')
            if next_container:
                self.selected_container.reset()#reset the position of the container
                self.selected_container = next_container
        elif event[2]['l_stick'][0] > 0:  # right
            next_container = self.find_closest_position('right')
            if next_container:
                self.selected_container.reset()#reset the position of the container
                self.selected_container = next_container

    def find_closest_position(self, direction):
        current = self.selected_container.rect
        best = None
        best_score = float('inf')

        for container in self.map_UI.objects:
            if container == self.selected_container:
                continue
            target = container.rect

            dx = target.centerx - current.centerx
            dy = target.centery - current.centery

            # Check direction and filter candidates
            if direction == 'up' and dy >= 0: continue
            if direction == 'down' and dy <= 0: continue
            if direction == 'left' and dx >= 0: continue
            if direction == 'right' and dx <= 0: continue

            # Prioritize closest in direction
            distance = dx**2 + dy**2
            angle_priority = abs(dx if direction in ('up', 'down') else dy)

            score = distance + angle_priority * 0.5  # fine-tune weighting
            if score < best_score:
                best_score = score
                best = container

        return best          

    def exit_state(self):
        self.game_objects.game.state_manager.exit_state()       

class MapUI_2(BaseUI):#world map
    def __init__(self, game_objects, **kwarg):
        super().__init__(game_objects, **kwarg)
        self.map_UI = getattr(UI_loader, 'WorldMap')(game_objects),
        self.selected_container = self.map_UI.objects[0]#initial default container

        self.scroll = [0,0]
        self.pos = [-0.5*(self.map_UI.BG.width - self.game_objects.game.window_size[0]),-0.5*(self.map_UI.BG.height - self.game_objects.game.window_size[1])]#start offset position

        for object in self.map_UI.objects:
            object.update_scroll(self.pos)
        
    def update(self):
        self.selected_container.update()#make it move
        self.continious_input()
        self.update_pos(self.scroll)
        self.limit_pos()
        for object in self.map_UI.objects:
            object.update_scroll(self.scroll)

    def continious_input(self):        
        self.scroll = [-2*self.game_objects.controller.value['r_stick'][0], -2*self.game_objects.controller.value['r_stick'][1]]#right analog stick

    def update_pos(self,scroll):
        self.pos = [self.pos[0]+scroll[0],self.pos[1]+scroll[1]]

    def limit_pos(self):
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
        self.game_objects.UI.backpack.screen.clear(0, 0, 0, 0)#clear the screen
        self.game_objects.game.display.render(self.map_UI.BG, self.game_objects.UI.backpack.screen, position = self.pos)
        for object in self.map_UI.objects:
            self.game_objects.game.display.render(object.image, self.game_objects.UI.backpack.screen, position = object.rect.topleft)
        self.blit_screen()

    def calculate_position(self):
        scroll = [-self.selected_container.rect.center[0]+self.game_objects.game.window_size[0]*0.5,-self.selected_container.rect.center[1]+self.game_objects.game.window_size[1]*0.5]
        for object in self.map_UI.objects:
            object.update_scroll(scroll)
        self.update_pos(scroll)

    def handle_events(self,input):
        event = input.output()
        input.processed()        

        if event[0]:#press
            if event[-1] == 'select':
                self.exit_state()
            elif event[-1] == 'rb':#nezt page
                new_ui = InventoryUI(self.game_objects, screen_alpha = 230)
                self.game_objects.UI.backpack.enter_page(new_ui)
            elif event[-1] == 'x':#when pressing a
                map_name = self.selected_container.activate()#open the local map. I guess it should be a new state
                self.game_objects.UI.set_ui('map', map = map_name, screen_alpha = 230)#world map

        if event[2]['l_stick'][1] < 0:  # up
            next_container = self.find_closest_position('up')
            if next_container:
                self.selected_container = next_container
                self.calculate_position()
        elif event[2]['l_stick'][1] > 0:  # down
            next_container = self.find_closest_position('down')
            if next_container:
                self.selected_container = next_container
                self.calculate_position()
        elif event[2]['l_stick'][0] < 0:  # left
            next_container = self.find_closest_position('left')
            if next_container:
                self.selected_container = next_container
                self.calculate_position()
        elif event[2]['l_stick'][0] > 0:  # right
            next_container = self.find_closest_position('right')
            if next_container:
                self.selected_container = next_container
                self.calculate_position()

    def exit_state(self):
        self.game_objects.game.state_manager.exit_state()

    def find_closest_position(self, direction):
        current = self.selected_container.rect
        best = None
        best_score = float('inf')

        for container in self.map_UI.objects:
            if container == self.selected_container:
                continue
            target = container.rect

            dx = target.centerx - current.centerx
            dy = target.centery - current.centery

            # Check direction and filter candidates
            if direction == 'up' and dy >= 0: continue
            if direction == 'down' and dy <= 0: continue
            if direction == 'left' and dx >= 0: continue
            if direction == 'right' and dx <= 0: continue

            # Prioritize closest in direction
            distance = dx**2 + dy**2
            angle_priority = abs(dx if direction in ('up', 'down') else dy)

            score = distance + angle_priority * 0.5  # fine-tune weighting
            if score < best_score:
                best_score = score
                best = container

        return best   