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
        self.outputs = [self.keydown,self.keyup,self.value,self.key]
        self.map_keyboard()
        self.methods = [self.keybord]#joystick may be appended

        pygame.joystick.init()#initialise joystick module
        self.initiate_controls()#initialise joysticks and add to list
        self.buttonmapping()#read in controler configuration file

    def initiate_controls(self):
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]#save and initialise the controlers.

    def rumble(self):#doesn't rumble...
        for joystick in self.joysticks:
            joystick.rumble(0,0.7,1000)#low fre, high fre, duration

    def buttonmapping(self):
        if len(self.controller_type) == 1: return#if no controller
        #self.methods.append(self.joystick)
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
            method(event)
        #self.methods[-1](event)

    def keybord(self,event):
        if event.type == pygame.KEYDOWN:
            self.keydown = True
            self.key = self.keyboard_map.get(event.key, '')

            if self.key=='right':
                self.value['l_stick'][0]=1
            elif self.key=='left':
                self.value['l_stick'][0]=-1
            elif self.key=='up':
                self.value['l_stick'][1]=-1
            elif self.key=='down':
                self.value['l_stick'][1]=1

        elif event.type == pygame.KEYUP:#lift bottom
            self.keyup = True
            self.key = self.keyboard_map.get(event.key, '')

            if self.key=='right':
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
                self.value['l_stick'][1]=0

        if event.type==pygame.JOYDEVICEADDED:#if a controller is added while playing
            self.initiate_controls()
            self.methods.append(self.joystick)
            self.get_controllertype()
            self.buttonmapping()#read in controler configuration file

    def joystick(self,event):
        if event.type == pygame.JOYDEVICEREMOVED:#if a controller is removed wile playing
            self.initiate_controls()
            self.methods.pop()
            self.controller_type.pop()

        if event.type==pygame.JOYBUTTONDOWN:#press a button
            self.keydown=True
            self.key=self.buttons[str(event.button)]

        elif event.type==pygame.JOYBUTTONUP:#release a button
            self.keyup=True
            self.key=self.buttons[str(event.button)]

        if event.type==pygame.JOYAXISMOTION:#analog stick
            if event.axis==self.analogs['lh']:#left horizontal
                self.value['l_stick'][0] = event.value
                if abs(event.value) < 0.2:
                    self.value['l_stick'][0] = 0

            if event.axis==self.analogs['lv']:#left vertical
                self.value['l_stick'][1] = event.value
                if abs(event.value) < 0.1:
                    self.value['l_stick'][1] = 0

            #self.controller_angle('l_stick')

            if event.axis==self.analogs['rh']:#right horizontal
                self.value['r_stick'][0] = event.value
                if abs(event.value) < 0.1:
                    self.value['r_stick'][0] = 0

            if event.axis==self.analogs['rv']:#right vertical
                self.value['r_stick'][1] = event.value
                if abs(event.value) < 0.1:
                    self.value['r_stick'][1] = 0

            #self.controller_angle('r_stick')

        if event.type == pygame.JOYHATMOTION:
            self.keydown = True
            self.value['d_pad'] = [event.value[0],event.value[1]]

    def output(self):
        return [self.keydown, self.keyup, self.value, self.key]

    def controller_angle(self,stick):#limit the inputs depending on the angle
        x, y = self.value[stick]
        if abs(x) > 1:
            x = math.copysign(1, x)
        if abs(y) > 1:
            y = math.copysign(1, y)

        if x == 0:
            return
        else:
            angle = 180 * math.atan(abs(y)/abs(x))/3.141592
            #print(angle)
            if angle < 45:
                self.value[stick][1] = 0
