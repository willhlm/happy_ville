import pygame
import pygame._sdl2.controller
import time

class Controller():
    def __init__(self):
        self.keydown = False
        self.keyup = False
        self.key = False
        self.value = {'l_stick': [0, 0], 'r_stick': [0, 0], 'd_pad': [0, 0], 'l_trigger': 0, 'r_trigger': 0}#analogue values
        self.outputs = [self.keydown, self.keyup, self.value, self.key]

        self.map_keyboard()
        self.map_joystick()
        self.map_analogues()
        self.methods = [self.keybord]
        self.input_buffer = set()

        self.input_cooldown = 0.2  # Cooldown in seconds (e.g., 200ms)

        pygame._sdl2.controller.init()  # Initialize the SDL2 controller module
        self.controllers = []
        self.get_controller_type()

    def update_controller(self):#called when adding or removing controlelrs
        self.initiate_controls()
        self.get_controller_type()

    def initiate_controls(self):
        for controller_id in range(pygame._sdl2.controller.get_count()):
            self.controllers.append(pygame._sdl2.controller.Controller(controller_id))

    def rumble(self, duration = 1000):
        for controller in self.controllers:
            controller.rumble(0, 0.7, duration)  # Low frequency, high frequency, duration

    def get_controller_type(self):
        self.controller_type = ['keyboard']
        for controller in self.controllers:
            name = controller.name  # Get the controller's name string
            if 'xbox' in name.lower():
                self.controller_type.append('xbox')
            elif 'playstation' in name.lower():
                self.controller_type.append('ps4')
            elif 'nintendo' in name.lower():
                self.controller_type.append('nintendo')
            else:
                self.controller_type.append('unknown')

    def map_analogues(self):
        self.last_input = {
            'l_stick': {'value':[0,0],'time':0},
            'r_stick': {'value':[0,0],'time':0}, #not used
            'l_trigger': 0, #not used
            'r_trigger': 0 #not used
        }

    def map_joystick(self):
        self.joystick_map = {
            pygame.CONTROLLER_BUTTON_A: "a",
            pygame.CONTROLLER_BUTTON_B: "b",
            pygame.CONTROLLER_BUTTON_X: "x",
            pygame.CONTROLLER_BUTTON_Y: "y",
            pygame.CONTROLLER_BUTTON_START: "start",
            pygame.CONTROLLER_BUTTON_BACK: "select",
            pygame.CONTROLLER_BUTTON_LEFTSHOULDER: "lb",
            pygame.CONTROLLER_BUTTON_RIGHTSHOULDER: "rb",
            pygame.CONTROLLER_BUTTON_LEFTSTICK: "ls",  # Pressing the left stick
            pygame.CONTROLLER_BUTTON_RIGHTSTICK: "rs",  # Pressing the right stick
            pygame.CONTROLLER_BUTTON_GUIDE: "guide",  # Xbox button in the middle
            pygame.CONTROLLER_BUTTON_DPAD_UP: "dpad_up",
            pygame.CONTROLLER_BUTTON_DPAD_DOWN: "dpad_down",
            pygame.CONTROLLER_BUTTON_DPAD_LEFT: "dpad_left",
            pygame.CONTROLLER_BUTTON_DPAD_RIGHT: "dpad_right",
        }

    def map_keyboard(self):
        self.keyboard_map = {
            pygame.K_ESCAPE: "start",
            #pygame.K_RIGHT: "right",
            #pygame.K_LEFT: "left",
            #pygame.K_UP: "up",
            #pygame.K_DOWN: "down",
            pygame.K_TAB: "rb",
            pygame.K_SPACE: "a",
            pygame.K_t: "y",
            pygame.K_e: "b",
            pygame.K_f: "x",
            pygame.K_g: "y",
            pygame.K_i: "select",
            pygame.K_LSHIFT: "lb",
            pygame.K_RETURN: "return",
            pygame.K_k: "rt",
        }

    def map_inputs(self, event):
        self.keyup = False
        self.keydown = False
        self.key = None
        for method in self.methods:
            method(event)

    def keybord(self, event):
        if event.type == pygame.KEYDOWN:
            self.keydown = True
            self.key = self.keyboard_map.get(event.key, None)
            if self.key: self.insert_buffer()

        elif event.type == pygame.KEYUP:
            self.keyup = True
            self.key = self.keyboard_map.get(event.key, None)
            if self.key: self.insert_buffer()

        if event.type == pygame.CONTROLLERDEVICEADDED:
            self.update_controller()
            self.methods.append(self.joystick)

    def joystick(self, event):
        if event.type == pygame.CONTROLLERDEVICEREMOVED:
            self.update_controller()
            self.methods.pop()

        if event.type == pygame.CONTROLLERBUTTONDOWN:
            self.keydown = True
            self.key = self.joystick_map.get(event.button, None)
            if self.key: self.insert_buffer()

        elif event.type == pygame.CONTROLLERBUTTONUP:
            self.keyup = True
            self.key = self.joystick_map.get(event.button, None)
            if self.key: self.insert_buffer()

        if event.type == pygame.CONTROLLERAXISMOTION:
            return
            if event.axis == pygame.CONTROLLER_AXIS_TRIGGERLEFT:
                self.value["l_trigger"] = self.normalize_axis(event.value)
            if event.axis == pygame.CONTROLLER_AXIS_TRIGGERRIGHT:
                self.value["r_trigger"] = self.normalize_axis(event.value)
            self.insert_buffer()

    @staticmethod
    def normalize_axis(value):
        return value / 32768.0#value taken from documentation

    def continuous_input_checks(self):#caled every frame
        keys = pygame.key.get_pressed()
        self.value['l_stick'] = [0,0]
        self.value['r_stick'] = [0,0]

        if keys[pygame.K_RIGHT]:
            self.value["l_stick"][0] = 1
        if keys[pygame.K_LEFT]:
            self.value["l_stick"][0] = -1
        if keys[pygame.K_UP]:
            self.value["l_stick"][1] = -1
        if keys[pygame.K_DOWN]:
            self.value["l_stick"][1] = 1

        for controller in self.controllers:
            l_axis_x = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_LEFTX))
            l_axis_y = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_LEFTY))

            r_axis_x = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTX))
            r_axis_y = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_RIGHTY))

            if abs(l_axis_x) > 0.2:
                self.value["l_stick"][0] = l_axis_x
            if abs(l_axis_y) > 0.2:
                self.value["l_stick"][1] = l_axis_y
                #if abs(l_axis_y) > 0.98:
                #    self.value['l_stick'][0] = 0

            if abs(r_axis_x) > 0.1:
                self.value["r_stick"][0] = r_axis_x
            if abs(r_axis_y) > 0.1:
                self.value["r_stick"][1] = r_axis_y

        self.discrete_inputs_UI()#continious inout are made discrete for UI (UI relies on input buffer: player movement can read difrectly self.value)

    def discrete_inputs_UI(self):#inserts in buffer if there is a big change in input, or if there has been some time since last input
        current_time = time.time()
        l_stick = self.value['l_stick']

        # Check if a significant change occurred in the stick position
        significant_change = (
            abs(l_stick[0] - self.last_input['l_stick']['value'][0]) > 0.5 or
            abs(l_stick[1] - self.last_input['l_stick']['value'][1]) > 0.5
        )
        
        if significant_change or (current_time - self.last_input['l_stick']['time'] > self.input_cooldown):
            if abs(l_stick[0]) > 0.5 or abs(l_stick[1]) > 0.5:  # Threshold to consider as input
                self.keyup, self.keydown, self.key = False, False, None
                self.insert_buffer()
                self.last_input['l_stick']['time'] = current_time  # Update cooldown timer
                self.last_input['l_stick']['value'] = l_stick.copy()  # Update last stick position

    def insert_buffer(self):
        self.input_buffer.add(Inputs(self, self.key, self.keydown, self.keyup, self.value))

class Inputs():
    def __init__(self, controller, key, keydown, keyup, value, lifetime = 10):
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
            self.processed()

    def processed(self):
        self.controller.input_buffer.discard(self)
