import pygame, sys
import UI_loader
import entities_UI, Entities

class Facility_states():
    def __init__(self, game_state):
        self.game_state = game_state
        self.game_objects = game_state.game.game_objects

    def enter_state(self,newstate):
         self.game_state.state = getattr(sys.modules[__name__], newstate)(self.game_state)#make a class based on the name of the newstate: need to import sys

    def update(self):
        pass

    def render(self):
        pass

    def handle_events(self,input):
        pass

    def exit_state(self):
        self.release_texture()
        self.game_state.exit_state()

    def release_texture(self):
        pass    

#ability upgrade
class Spirit_upgrade_menu(Facility_states):
    def __init__(self, game_state):
        super().__init__(game_state)
        self.define_UI()
        self.index = [0,0]
        self.letter_frame = 0
        self.define_abilities()
        self.define_pointer()
        self.blit_titles()
        self.next_page = 'Movement_upgrades_menu'

    def define_UI(self):
        self.abillity_UI = UI_loader.UI_loader(self.game_objects,'ability_spirit_upgrade')
        self.abilities = self.game_objects.player.abilities.spirit_abilities

    def define_abilities(self):
        rows = self.abillity_UI.rows
        for ability in self.abilities.keys():
            self.abillity_UI.abilities[rows[ability]][0].activate(1)#set the first column of abilities aila has to one level 1

            for level in range(1,len(self.abillity_UI.abilities[rows[ability]][0].description)):#the levels already aquired
                if level < self.abilities[ability].level:
                    self.abillity_UI.abilities[rows[ability]][level].activate(level+1)
                else:
                    self.abillity_UI.abilities[rows[ability]][level].deactivate(level+1)

    def define_pointer(self,size = [32,32]):#called everytime we move from one area to another
        self.pointer = pygame.Surface(size,pygame.SRCALPHA,32).convert_alpha()#the length should be fixed determined, putting 500 for now
        pygame.draw.rect(self.pointer,[200,50,50,255],(0,0,size[0],size[1]),width=1,border_radius=5)

    def update(self):
        self.letter_frame += self.game_objects.game.dt

    def render(self):
        self.blit_BG()
        self.blit_symbols()
        self.blit_pointer()
        self.blit_description()
        self.blit_titles()

    def blit_titles(self):
        title = self.game_objects.font.render(text = 'absorbed abillities')
        title.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.screen.blit(title,[250,50])

    def blit_pointer(self):
        self.game_objects.game.screen.blit(self.pointer,self.abillity_UI.abilities[self.index[0]][self.index[1]].rect.center)#pointer

    def blit_symbols(self):
        for abilities in self.abillity_UI.abilities:
            for ability in abilities:
                ability.animation.update()
                self.game_objects.game.screen.blit(ability.image,ability.rect.center)

    def blit_BG(self):
        self.abillity_UI.BG.set_alpha(230)
        self.game_objects.game.screen.blit(self.abillity_UI.BG,(0,0))#pointer

    def blit_description(self):
        ability = self.abillity_UI.abilities[self.index[0]][0]#the row we are on
        level = self.index[1]#the columns we are on
        conv = ability.description[level]
        text = self.game_objects.font.render((152,80), conv, int(self.letter_frame//2))
        text.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.screen.blit(text,(380,120))

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()
            elif input[-1] == 'rb' or input[-1] == 'lb':#nezt page
                self.enter_state(self.next_page)
            elif input[-1]=='a' or input[-1]=='return':
                self.choose_ability()

            elif input[-1] =='right':
                self.index[1] += 1
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)
                self.letter_frame = 0

            elif input[-1] =='left':
                self.index[1] -= 1
                self.index[1] = max(0,self.index[1])
                self.letter_frame = 0

            elif input[-1] =='down':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.abillity_UI.abilities)-1)
                self.letter_frame = 0
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)

            elif input[-1] =='up':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])
                self.letter_frame = 0
                self.index[1] = min(self.index[1],len(self.abillity_UI.abilities[self.index[0]])-1)

    def choose_ability(self):
        ability = self.abillity_UI.abilities[self.index[0]][0]#the row we are on
        level = self.index[1]#the columns we are on
        if self.abilities[type(ability).__name__].level == level:
            self.abilities[type(ability).__name__].upgrade_ability()
            self.abillity_UI.abilities[self.index[0]][level].activate(level+1)

    def exit_state(self):
        super().exit_state()
        self.game_objects.player.currentstate.handle_input('Pray_spe_post')

class Movement_upgrades_menu(Spirit_upgrade_menu):#when double clicking the save point, open ability upgrade screen, spirit abilities
    def __init__(self, game_state):
        super().__init__(game_state)
        self.next_page = 'Spirit_upgrade_menu'

    def define_UI(self):
        self.abillity_UI = UI_loader.UI_loader(self.game_objects,'ability_movement_upgrade')
        self.abilities = self.game_objects.player.abilities.movement_dict

    def blit_titles(self):
        title = self.game_objects.font.render(text = 'absorbed abillities')
        title.fill(color=(255,255,255),special_flags=pygame.BLEND_ADD)
        self.game_objects.game.screen.blit(title,[250,50])

#fast travel, smith, bank, souls essence, vendor
class Fast_travel_unlock(Facility_states):
    def __init__(self, game_state,fast_travel):
        super().__init__(game_state)
        self.fast_travel = fast_travel
        self.index = [0,0]
        self.letter_frame = 0
        self.actions = ['yes','no']
        self.conv = 'Would you like to offer ' + str(self.fast_travel.cost) + ' ambers to this statue?'
        self.bg_size = [152,48]
        self.bg = self.game_objects.font.fill_text_bg(self.bg_size)
        self.define_pos()
        self.pointer = entities_UI.Menu_Box(self.game_objects)

    def define_pos(self):
        self.pos = []
        for i in range(0,len(self.actions)):
            self.pos.append([255+i*30,110])

    def blit_BG(self):
        pos = [self.game_objects.game.window_size[0]*0.5-self.bg_size[0]*0.5,self.game_objects.game.window_size[1]*0.25]
        self.game_objects.game.display.render(self.bg, self.game_objects.game.screen, position = pos)#shader render

    def blit_actions(self):
        for index, action in enumerate(self.actions):
            response = self.game_objects.font.render(text = action)
            self.game_objects.game.display.render(response, self.game_objects.game.screen, position = self.pos[index])#shader render

    def blit_text(self):
        text = self.game_objects.font.render((130,90), self.conv, int(self.letter_frame//2))
        self.game_objects.game.display.render(text, self.game_objects.game.screen, position =(220,90))#shader render        

    def blit_pointer(self):
        pos = self.pos[self.index[0]]
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, position =pos)#shader render        
        
    def update(self):
        self.letter_frame += self.game_objects.game.dt

    def render(self):
        self.blit_BG()
        self.blit_actions()
        self.blit_text()
        self.blit_pointer()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()

            elif input[-1] =='right':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.pos)-1)

            elif input[-1] =='left':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif input[-1] == 'a' or 'return':
                if self.index[0] == 1:#no
                    self.exit_state()
                elif self.index[0] == 0:#yes
                    if self.fast_travel.unlock():#enough money: unlocked
                        self.exit_state()
                    else:#not enout money
                        pass

class Fast_travel_menu(Facility_states):
    def __init__(self, game_state):
        super().__init__(game_state)
        self.travel_UI = UI_loader.UI_loader(self.game_objects,'fast_travel')
        self.index = [0,0]
        self.define_destination()
        self.pointer = entities_UI.Menu_Box(self.game_objects)

    def define_destination(self):
        self.destinations = []
        for level in self.game_objects.world_state.travel_points.keys():
            self.destinations.append(level)

    def blit_BG(self):        
        self.game_objects.game.display.render(self.travel_UI.BG, self.game_objects.game.screen)#shader render                

    def blit_destinations(self):
        for index, name in enumerate(self.game_objects.world_state.travel_points.keys()):
            text = self.game_objects.font.render((152,80), name, 100)
            self.game_objects.game.display.render(text, self.game_objects.game.screen, position =self.travel_UI.name_pos[index])#shader render                

    def blit_pointer(self):
        pos = self.travel_UI.name_pos[self.index[0]]
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, position =pos)#shader render                

    def render(self):
        self.blit_BG()
        self.blit_destinations()
        self.blit_pointer()

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] == 'select':
                self.exit_state()

            elif input[-1] =='down':
                self.index[0] += 1
                self.index[0] = min(self.index[0],len(self.destinations)-1)

            elif input[-1] =='up':
                self.index[0] -= 1
                self.index[0] = max(0,self.index[0])

            elif input[-1] == 'a':
                self.exit_state()
                level = self.destinations[self.index[0]]
                cord = self.game_objects.world_state.travel_points[level]
                self.game_objects.load_map(self,level,cord)

class Smith(Facility_states):#called from mr smith
    def __init__(self, game_state, npc):
        super().__init__(game_state)
        self.npc = npc
        self.pointer = entities_UI.Menu_Arrow(self.game_objects)
        self.init()#depends on frame
        self.pointer_index = [0,0]#position of box
        self.set_response('')

    def init(self):
        self.actions = ['upgrade','enhance','cancel']
        self.init_canvas([64,22*len(self.actions)])#specific for each facility

    def init_canvas(self,size=[64,64]):
        self.surf=[]
        self.bg = self.game_objects.font.fill_text_bg(size)
        for string in self.actions:
            self.surf.append(self.game_objects.font.render(text = string))

    def set_response(self,text):
        self.respond = self.game_objects.font.render(text = text)

    def render(self):
        self.game_objects.shaders['colour']['colour'] = [255,255,255,255]
        self.blit_text()
        self.blit_pointer()
        self.blit_response()

    def blit_text(self):
        self.game_objects.game.display.render(self.bg, self.game_objects.game.screen, position =(280,120))#shader render                
        for index, surf in enumerate(self.surf):
            self.game_objects.game.display.render(surf, self.game_objects.game.screen, position =(310,135+index*10),shader = self.game_objects.shaders['colour'])#shader render                

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, position =(300,135+10*self.pointer_index[1]),shader = self.game_objects.shaders['colour'])#shader render                        

    def blit_response(self): 
        self.game_objects.game.display.render(self.respond, self.game_objects.game.screen, position = (300,195),shader = self.game_objects.shaders['colour'])#shader render

    def handle_events(self,input):
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

    def select(self):
        if self.pointer_index[1] == 0:#if we select upgrade
            self.upgrade()
        elif self.pointer_index[1] == 1:#selct enhace
            self.game_state.state.append(Smith_2(self.game_state,self.npc))#go to next frame
        else:#select cancel
            self.exit_state()

    def upgrade(self):
        if self.game_objects.player.inventory['Tungsten'] >= self.game_objects.player.sword.tungsten_cost:
            self.game_objects.player.sword.level_up()
            self.set_response('Now it is better')
        else:#not enough tungsten
            self.set_response('You do not have enough heavy rocks')

class Smith_2(Smith):#the enhance screen
    def __init__(self, game_state, npc):
        super().__init__(game_state,npc)

    def init(self):
        self.actions=[]
        for index, stones in enumerate(self.game_objects.player.sword.stones):
            self.actions.append(stones)
        self.actions.append('cancel')
        self.init_canvas([64,17*len(self.actions)])
        self.set_response('Lets enhance')

    def select(self):
        if self.pointer_index[1] < len(self.actions)-1:#if we selec
            stone_str = self.actions[self.pointer_index[1]]
            self.game_objects.player.sword.set_stone(stone_str)
            self.set_response('Now it is ' + stone_str)
        else:#select cancel
            self.game_state.state.pop()

class Bank(Facility_states):#caled from mr banks
    def __init__(self, game_state, npc):
        super().__init__(game_state)
        self.npc = npc
        self.pointer = entities_UI.Menu_Arrow(self.game_objects)
        self.init()#depends on frame

    def init(self):
        self.pointer_index = [0,0]#position of box
        self.actions = ['withdraw','deposit','cancel']
        self.init_canvas()#specific for each facility
        self.set_response('Welcome')

    def init_canvas(self,size=[120,64]):
        self.surf=[]
        self.bg = self.game_objects.font.fill_text_bg(size)
        for string in self.actions:
            self.surf.append(self.game_objects.font.render(text = string))

    def render(self):
        self.blit_text()
        self.blit_pointer()

    def blit_text(self):
        self.game_objects.game.display.render(self.bg, self.game_objects.game.screen, position = (190,150))#shader render        
        for index, surf in enumerate(self.surf):
            self.game_objects.game.display.render(surf, self.game_objects.game.screen, position = (300,160+index*10))#shader render

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, position =(300,130+10*self.pointer_index[1]))#shader render              

    def handle_events(self,input):
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

    def select(self):#exchane of money
        if self.pointer_index[1]==2:#cancel
            self.exit_state()
        else:#widthdraw or deposit
            if self.pointer_index[1]==0:#widthdraw
                self.game_state.state.append(Bank_withdraw(self.game_state,self.npc))#go to next frame
            else:#deposite
                self.game_state.state.append(Bank_deposite(self.game_state,self.npc))#go to next frame

class Bank_withdraw(Bank):#caled from mr banks
    def __init__(self, game_state, npc):
        super().__init__(game_state, npc)
        self.ammount = 0

    def select(self):
        self.game_objects.player.inventory['Amber_Droplet']+=self.ammount
        self.npc.ammount-=self.ammount
        self.game_state.state.pop()

    def blit_text(self):
        self.game_objects.game.display.render(self.bg, self.game_objects.game.screen, position = (280,120))#shader render         
        self.amount_surf = self.game_objects.font.render(text = str(self.ammount))
        self.game_objects.game.display.render(self.amount_surf, self.game_objects.game.screen, position = (310,130))#shader render         

    def blit_pointer(self):
        pass

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] =='down':
                self.ammount -= 1
                self.ammount = max(self.ammount,0)
            elif input[-1] =='up':
                self.ammount += 1
                self.ammount = min(self.ammount,self.npc.ammount)
            elif input[-1] =='right':
                self.ammount += 100
                self.ammount = min(self.ammount,self.npc.ammount)
            elif input[-1] == 'left':
                self.ammount -= 100
                self.ammount = max(self.ammount,0)
            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Bank_deposite(Bank):#caled from mr banks
    def __init__(self, game_state, npc):
        super().__init__(game_state, npc)
        self.ammount = 0

    def select(self):
        self.game_objects.player.inventory['Amber_Droplet']-=self.ammount
        self.npc.ammount+=self.ammount
        self.game_state.state.pop()

    def blit_text(self):
        self.game_objects.game.display.render(self.bg, self.game_objects.game.screen, position = (280,120))#shader render         
        self.amount_surf = self.game_objects.font.render(text = str(self.ammount))
        self.game_objects.game.display.render(self.amount_surf, self.game_objects.game.screen, position = (310,130))#shader render         

    def blit_pointer(self):
        pass

    def handle_events(self,input):
        if input[0]:#press
            if input[-1] =='down':
                self.ammount -= 1
                self.ammount = max(self.ammount,0)
            elif input[-1] =='up':
                self.ammount += 1
                self.ammount = min(self.ammount,self.game_objects.player.inventory['Amber_Droplet'])
            elif input[-1] =='right':
                self.ammount += 100
                self.ammount = min(self.ammount,self.game_objects.player.inventory['Amber_Droplet'])
            elif input[-1] == 'left':
                self.ammount -= 100
                self.ammount = max(self.ammount,0)
            elif input[-1]=='a' or input[-1]=='return':
                self.select()

class Soul_essence(Facility_states):#called from inorinoki
    def __init__(self, game_state):
        super().__init__(game_state)
        self.actions=['health','spirit','cancel']
        self.pointer = entities_UI.Menu_Box(self.game_objects)
        self.cost = 4
        self.pointer_index = [0,0]
        self.init_canvas()
        self.bg_pos = [280,120]

    def init_canvas(self,size=[64,64]):
        self.surf=[]
        self.bg = self.game_objects.font.fill_text_bg(size)
        for string in self.actions:
            self.surf.append(self.game_objects.font.render(text = string))

    def render(self):
        self.blit_BG()
        self.blit_pointer()

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, position =  (self.bg_pos[0] + 30,self.bg_pos[1] + 10+self.pointer_index[1]*10))#shader render 

    def blit_BG(self):
        self.game_objects.game.display.render(self.bg, self.game_objects.game.screen, position = self.bg_pos)#shader render        
        for index, surf in enumerate(self.surf):
            self.game_objects.game.display.render(surf, self.game_objects.game.screen, position = (self.bg_pos[0] + 30,self.bg_pos[1] + 10+index*10))#shader render        

    def handle_events(self,input):
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

    def select(self):
        if self.pointer_index[1] == 0:#if we select health
            if self.game_objects.player.inventory['Soul_essence'] >= self.cost:
                pos = [self.game_objects.player.rect[0],-100]
                heart = Entities.Heart_container(pos,self.game_objects)
                self.game_objects.loot.add(heart)
                self.game_objects.player.inventory['Soul_essence']-=self.cost
        elif self.pointer_index[1] == 1:#if we select spirit
            if self.game_objects.player.inventory['Soul_essence'] >= self.cost:
                pos = [self.game_objects.player.rect[0],-100]
                spirit = Entities.Spirit_container(pos,self.game_objects)
                self.game_objects.loot.add(spirit)
                self.game_objects.player.inventory['Soul_essence']-=self.cost
        else:#select cancel
            self.exit_state()

class Vendor(Facility_states):#called from Astrid
    def __init__(self, game_state, npc):
        super().__init__(game_state)
        self.npc = npc
        self.vendor_UI = UI_loader.UI_loader(self.game_objects,'vendor')
        self.bg_pos = (70,20)

        self.init()
        self.letter_frame = 0
        self.pointer_index = [0,0]
        self.pointer = entities_UI.Menu_Box(self.game_objects)
        self.item_index = [0,0]#pointer of item

    def init(self):
        self.init_canvas()

    def init_canvas(self):     
        self.items = []
        for item in self.npc.inventory.keys():
            item = getattr(sys.modules[entities_UI.__name__], item)([0,0],self.game_objects)#make the object based on the string
            self.items.append(item)

        self.amber = entities_UI.Amber_Droplet([0,0],self.game_objects)#the thing showing how much money you have

        self.display_number = min(len(self.vendor_UI.objects), len(self.items))#number of items to list
        self.sale_items = self.items[0:self.display_number]#gets udated when you press the up down keys

        self.buy_sur = self.game_objects.font.render(text = 'Buy')
        self.cancel_sur = self.game_objects.font.render(text = 'Cancel')

    def set_response(self,text):
        self.respond = self.game_objects.font.render(text = text)

    def blit_response(self):
        self.game.display.render(self.respond, self.game_objects.game.screen, position = (190,150))#shader render

    def update(self):
        self.letter_frame += self.game_objects.game.dt

    def render(self):
        self.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.blit_BG()
        self.blit_money()
        self.blit_description()
        self.blit_items()
        self.blit_pointer()

    def blit_BG(self):
        self.game_objects.game.display.render(self.vendor_UI.BG, self.game_objects.game.screen, position = self.bg_pos)#shader render

    def blit_money(self):#blit how much gold we have in inventory
        money = self.game_objects.player.inventory['Amber_Droplet']
        count_text = self.game_objects.font.render(text = str(money))
        position = [self.bg_pos[0] + self.vendor_UI.amber.rect.bottomright[0], self.bg_pos[1] + self.vendor_UI.amber.rect.bottomright[1]]
        self.game_objects.game.display.render(count_text, self.game_objects.game.screen, position = position, shader = self.game_objects.shaders['colour'])#shader render

        self.amber.animation.update()
        position = [self.bg_pos[0] + self.vendor_UI.amber.rect.topleft[0], self.bg_pos[1] + self.vendor_UI.amber.rect.topleft[1]]
        self.game_objects.game.display.render(self.amber.image, self.game_objects.game.screen, position = position)#shader render

    def blit_description(self):
        conv=self.items[self.item_index[1]].description        
        text = self.game_objects.font.render(self.vendor_UI.description['size'], conv, int(self.letter_frame//2))
        position = [self.bg_pos[0] + self.vendor_UI.description['position'][0], self.bg_pos[1] + self.vendor_UI.description['position'][1]]
        self.game_objects.game.display.render(text, self.game_objects.game.screen, position = position, shader = self.game_objects.shaders['colour'])#shader render

    def blit_items(self):
        for index, item in enumerate(self.sale_items):            
            item.animation.update()
            position = [self.bg_pos[0] + self.vendor_UI.objects[index].rect.topleft[0], self.bg_pos[1] + self.vendor_UI.objects[index].rect.topleft[1]]
            self.game_objects.game.display.render(item.image, self.game_objects.game.screen, position = position)#shader render

            #blit cost
            item_name=str(type(item).__name__)
            cost = self.npc.inventory[item_name]
            cost_text = self.game_objects.font.render(text = str(cost))
            position = [self.bg_pos[0] + self.vendor_UI.objects[index].rect.bottomright[0], self.bg_pos[1] + self.vendor_UI.objects[index].rect.bottomright[1]]
            self.game_objects.game.display.render(cost_text, self.game_objects.game.screen, position = position, shader = self.game_objects.shaders['colour'])#shader render                
            
    def blit_pointer(self):
        position = [self.bg_pos[0] + self.vendor_UI.objects[self.pointer_index[1]].rect.topleft[0], self.bg_pos[1] + self.vendor_UI.objects[self.pointer_index[1]].rect.topleft[1]]
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, position = position)#shader render

    def handle_events(self, input):
        if input[0]:#press
            if input[-1] == 'y':
                self.exit_state()

            elif input[-1] =='down':
                self.item_index[1] += 1
                self.item_index[1] = min(self.item_index[1],len(self.items)-1)

                if self.pointer_index[1] == self.display_number-1:#at the bottom of the list
                    self.sale_items = self.items[self.item_index[1]-self.display_number+1:self.item_index[1]+1]
                
                self.pointer_index[1] += 1
                self.pointer_index[1] = min(self.pointer_index[1],self.display_number-1)                                    
                self.letter_frame = 0                    

            elif input[-1] =='up':
                self.item_index[1]-=1
                self.item_index[1] = max(self.item_index[1],0)

                if self.pointer_index[1]==0:
                    self.sale_items = self.items[self.item_index[1]:self.item_index[1]+self.display_number]

                self.pointer_index[1] -= 1
                self.pointer_index[1] = max(self.pointer_index[1],0)
                self.letter_frame = 0

            elif input[-1]=='a' or input[-1]=='return':
                self.select()

    def select(self):
        item = type(self.items[self.item_index[1]]).__name__
        self.game_state.state.append(Vendor2(self.game_state,self.npc,item))#go to next frame

class Vendor2(Vendor):#called from vendor when selecting an item
    def __init__(self, game_state, npc, item):
        super().__init__(game_state, npc)
        self.item = item

    def init(self):
        self.bg2 = self.game_objects.font.fill_text_bg([64,32])
        self.init_canvas()

    def render(self):
        super().render()
        self.blit_BG2()
        self.blit_pointer()

    def blit_BG2(self):
        self.game_objects.game.display.render(self.buy_sur, self.game_objects.game.screen,(280+30,120+10))#shader render        
        self.game_objects.game.display.render(self.cancel_sur, self.game_objects.game.screen,(280+30,120 + 20))#shader render        
        self.game_objects.game.display.render(self.bg2, self.game_objects.game.screen,(280,120))#shader render

    def blit_pointer(self):
        self.game_objects.game.display.render(self.pointer.image, self.game_objects.game.screen, (300, 130 + 10 * self.pointer_index[1]))#shader render

    def select(self):
        if self.pointer_index[1] == 0:#if we select buy
            self.buy()
        else:
            self.set_response('What do you want?')
        self.game_state.state.pop()#go back to previous frame

    def buy(self):
        if self.game_objects.player.inventory['Amber_Droplet']>=self.npc.inventory[self.item]:
            self.game_objects.player.inventory[self.item] += 1
            self.game_objects.player.inventory['Amber_Droplet']-=self.npc.inventory[self.item]
            self.set_response('Thanks for buying')
        else:#not enough money
            self.set_response('Get loss you poor piece of shit')

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
