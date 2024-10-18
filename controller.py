import pygame, json, math
from os.path import join

class Controller():
    def __init__(self, controller_type = False):
        self.controller_type = ['keyboard']
        if controller_type: self.controller_type.append(controller_type)
        self.keydown = False
        self.keyup = False
        self.value = {'l_stick':[0,0],'r_stick':[0,0],'d_pad':[0,0]}#movement (left analog, arrow keys), right analog, d_pad
        self.key = False
        self.outputs = [self.keydown, self.keyup, self.value, self.key]
        self.map_keyboard()
        self.methods = [self.keybord]#joystick may be appended
        self.input_buffer = set()

        pygame.joystick.init()#initialise joystick module
        self.joysticks = []

    def add_controller(self):
        self.initiate_controls()#initialise joysticks and add to list
        self.get_controllertype()
        self.buttonmapping()#read in controler configuration file

    def initiate_controls(self):
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]#save and initialise the controlers.

    def rumble(self, duration = 1000):
        for joystick in self.joysticks:
            joystick.rumble(0, 0.7, duration)#low fre, high fre, duration

    def buttonmapping(self):
        if len(self.controller_type) == 1: return#if no controller
        file = 'keys_' + self.controller_type[-1] + '.json'
        with open(join(file),'r+') as file:
            mapping = json.load(file)
            self.buttons = mapping['buttons']
            self.analogs = mapping['analogs']

    def get_controllertype(self):#called when a device is adde
        for joy in self.joysticks:
            if 'xbox' in joy.get_name().lower():
                self.controller_type.append('xbox')
            elif 'playstation' in joy.get_name().lower():
                self.controller_type.append('ps4')
            elif 'nintendo' in joy.get_name().lower():
                self.controller_type.append('nintendo')

    def map_keyboard(self):
        self.keyboard_map = {pygame.K_ESCAPE: 'start',
                                pygame.K_RIGHT: 'right',
                                pygame.K_LEFT: 'left',
                                pygame.K_UP: 'up',
                                pygame.K_DOWN: 'down',
                                pygame.K_TAB: 'rb',
                                pygame.K_SPACE: 'a',     #jump, should be X on PS4
                                pygame.K_t: 'y',
                                pygame.K_e: 'b',
                                pygame.K_f: 'x',
                                pygame.K_g: 'y',
                                pygame.K_i: 'select',
                                pygame.K_LSHIFT: 'lb',
                                pygame.K_RETURN: 'return',
                                pygame.K_k: 'rt'
                                }

    def map_inputs(self,event):
        self.keyup = False
        self.keydown = False
        self.key = None
        for method in self.methods:#check for keyboard and controller
            method(event)#self.methods[-1](event)

    def keybord(self,event):
        if event.type == pygame.KEYDOWN:
            self.keydown = True
            self.key = self.keyboard_map.get(event.key, '')

            if self.key=='right':
                self.value['l_stick'][0] = 1
            elif self.key=='left':
                self.value['l_stick'][0] = -1
            elif self.key=='up':
                self.value['l_stick'][1] = -1
            elif self.key=='down':
                self.value['l_stick'][1] = 1

            self.insert_buffer()

        elif event.type == pygame.KEYUP:#lift bottom
            self.keyup = True
            self.key = self.keyboard_map.get(event.key, '')

            if self.key == 'right':
                keys_pressed=pygame.key.get_pressed()
                if keys_pressed[pygame.K_LEFT]:
                    self.value['l_stick'][0]=-1
                else:
                    self.value['l_stick'][0]=0
            elif self.key=='left':
                keys_pressed=pygame.key.get_pressed()
                if keys_pressed[pygame.K_RIGHT]:
                    self.value['l_stick'][0]=1
                else:
                    self.value['l_stick'][0]=0

            elif self.key=='up' or self.key=='down':
                self.value['l_stick'][1] = 0

            self.insert_buffer()

        if event.type==pygame.JOYDEVICEADDED:#if a controller is added while playing
            self.add_controller()
            self.methods.append(self.joystick)

    def joystick(self,event):
        if event.type == pygame.JOYDEVICEREMOVED:#if a controller is removed wile playing
            self.initiate_controls()
            self.methods.pop()
            self.controller_type.pop()

        if event.type == pygame.JOYBUTTONDOWN:#press a button
            self.keydown = True
            self.key = self.buttons[str(event.button)]
            self.insert_buffer()

        elif event.type == pygame.JOYBUTTONUP:#release a button
            self.keyup = True
            self.key = self.buttons[str(event.button)]
            self.insert_buffer()

        if event.type == pygame.JOYAXISMOTION:#analog stick
            if event.axis == self.analogs['lh']:#left horizontal
                self.value['l_stick'][0] = event.value
                if abs(event.value) < 0.1:
                    self.value['l_stick'][0] = 0

            if event.axis == self.analogs['lv']:#left vertical
                self.value['l_stick'][1] = event.value
                if abs(event.value) < 0.1:
                    self.value['l_stick'][1] = 0

            self.controller_angle('l_stick')

            if event.axis == self.analogs['rh']:#right horizontal
                self.value['r_stick'][0] = event.value
                if abs(event.value) < 0.1:
                    self.value['r_stick'][0] = 0

            if event.axis == self.analogs['rv']:#right vertical
                self.value['r_stick'][1] = event.value
                if abs(event.value) < 0.1:
                    self.value['r_stick'][1] = 0

            #self.controller_angle('r_stick')
            self.insert_buffer()

        if event.type == pygame.JOYHATMOTION:
            self.keydown = True
            self.value['d_pad'] = [event.value[0], event.value[1]]
            self.insert_buffer()

    def continious_input_checks(self):#called in update loop of gameplay: used for aila movement
        keys = pygame.key.get_pressed()#check for continious presses    
        value = {'l_stick': [0, 0]}#value = {'l_stick':[0,0],'r_stick':[0,0],'d_pad':[0,0]}
        if keys[pygame.K_RIGHT]:#right
            value['l_stick'][0] = 1
        if keys[pygame.K_LEFT]:#left
            value['l_stick'][0] = -1           
        if keys[pygame.K_UP]:#left
            value['l_stick'][1] = -1        
        if keys[pygame.K_DOWN]:#left
            value['l_stick'][1] = 1    
        
        for joystick in self.joysticks:#Controller input handling            
            axis_x = joystick.get_axis(0)  # Left stick X axis
            axis_y = joystick.get_axis(1)  # Left stick Y axis

            if abs(axis_x) > 0.1:
                value['l_stick'][0] = axis_x
            if abs(axis_y) > 0.1:
                value['l_stick'][1] = axis_y
                if abs(axis_y) > 0.98:#if poiting up or down, set x to 0
                    value['l_stick'][0] = 0                      
        return value

    def insert_buffer(self):
        self.input_buffer.add(Inputs(self, self.key, self.keydown, self.keyup, self.value))

    def output(self):
        return [self.keydown, self.keyup, self.value, self.key]

    def controller_angle(self,stick):#limit the inputs depending on the angle
        x, y = self.value[stick]
        if abs(y) > 0.98:#if poiting up or down, set x to 0
            self.value[stick][0] = 0

class Inputs():#different inputs such as keys and buttons
    def __init__(self, controller, key, keydown, keyup, value, lifetime = 50):
        self.controller = controller
        self.lifetime = lifetime
        self.key = key
        self.keydown = keydown
        self.keyup = keyup
        self.value = value

    def output(self):
        return [self.keydown, self.keyup, self.value, self.key]

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime < 0:
            self.remove_input()

    def remove_input(self):
        self.controller.input_buffer.discard(self)

    def processed(self):
        self.remove_input()
