import pygame
import pygame._sdl2.controller

class Controller:
    def __init__(self):
        self.keydown = False
        self.keyup = False
        self.value = {'l_stick': [0, 0], 'r_stick': [0, 0], 'd_pad': [0, 0], 'l_trigger': 0, 'r_trigger': 0}
        self.key = False
        self.outputs = [self.keydown, self.keyup, self.value, self.key]

        self.map_keyboard()
        self.map_joystick()
        self.methods = [self.keybord]
        self.input_buffer = set()

        pygame._sdl2.controller.init()  # Initialize the SDL2 controller module
        self.controllers = []
        
    def update_controller(self):
        self.initiate_controls()
        self.get_controller_type()

    def initiate_controls(self):        
        for controller_id in range(pygame._sdl2.controller.get_count()):  # Use get_count() to get controller count
            self.controllers.append(pygame._sdl2.controller.Controller(controller_id))

    def rumble(self, duration=1000):
        for controller in self.controllers:
            controller.rumble(0, 0.7, duration)  # Low frequency, high frequency, duration

    def get_controller_type(self):
        self.controller_type = []
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
            pygame.K_RIGHT: "right",
            pygame.K_LEFT: "left",
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
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
            self.key = self.keyboard_map.get(event.key, "")

            if self.key == "right":
                self.value["l_stick"][0] = 1
            elif self.key == "left":
                self.value["l_stick"][0] = -1
            elif self.key == "up":
                self.value["l_stick"][1] = -1
            elif self.key == "down":
                self.value["l_stick"][1] = 1

            self.insert_buffer()

        elif event.type == pygame.KEYUP:
            self.keyup = True
            self.key = self.keyboard_map.get(event.key, "")

            if self.key == "right" or self.key == "left":
                self.value["l_stick"][0] = 0
            elif self.key == "down" or self.key == "up":
                self.value["l_stick"][1] = 0

            self.insert_buffer()

        if event.type == pygame.CONTROLLERDEVICEADDED:
            self.update_controller()
            self.methods.append(self.joystick)

    def joystick(self, event):
        if event.type == pygame.CONTROLLERDEVICEREMOVED:
            self.update_controller()
            self.methods.pop()

        if event.type == pygame.CONTROLLERBUTTONDOWN:
            self.keydown = True
            self.key = self.joystick_map.get(event.button, "")
            self.insert_buffer()

        elif event.type == pygame.CONTROLLERBUTTONUP:
            self.keyup = True
            self.key = self.joystick_map.get(event.button, "")
            self.insert_buffer()

        if event.type == pygame.CONTROLLERAXISMOTION:
            if event.axis == pygame.CONTROLLER_AXIS_LEFTX:
                self.value["l_stick"][0] = self.normalize_axis(event.value)
            if event.axis == pygame.CONTROLLER_AXIS_LEFTY:
                self.value["l_stick"][1] = self.normalize_axis(event.value)
            if event.axis == pygame.CONTROLLER_AXIS_RIGHTX:
                self.value["r_stick"][0] = self.normalize_axis(event.value)
            if event.axis == pygame.CONTROLLER_AXIS_RIGHTY:
                self.value["r_stick"][1] = self.normalize_axis(event.value)
            if event.axis == pygame.CONTROLLER_AXIS_TRIGGERLEFT:
                self.value["l_trigger"] = self.normalize_axis(event.value)
            if event.axis == pygame.CONTROLLER_AXIS_TRIGGERRIGHT:
                self.value["r_trigger"] = self.normalize_axis(event.value)

            self.controller_angle("l_stick")
            self.insert_buffer()

    def normalize_axis(self, value):#value taken from documentation
        return value / 32768.0

    def continuous_input_checks(self):
        keys = pygame.key.get_pressed()
        value = {"l_stick": [0, 0]}
        if keys[pygame.K_RIGHT]:
            value["l_stick"][0] = 1
        if keys[pygame.K_LEFT]:
            value["l_stick"][0] = -1
        if keys[pygame.K_UP]:
            value["l_stick"][1] = -1
        if keys[pygame.K_DOWN]:
            value["l_stick"][1] = 1

        for controller in self.controllers:
            axis_x = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_LEFTX))
            axis_y = self.normalize_axis(controller.get_axis(pygame.CONTROLLER_AXIS_LEFTY))

            if abs(axis_x) > 0.1:
                value["l_stick"][0] = axis_x
            if abs(axis_y) > 0.1:
                value["l_stick"][1] = axis_y
                if abs(axis_y) > 0.98:
                    self.value['l_stick'][0] = 0                
        return value

    def insert_buffer(self):
        self.input_buffer.add(Inputs(self, self.key, self.keydown, self.keyup, self.value))

    def output(self):
        return [self.keydown, self.keyup, self.value, self.key]

    def controller_angle(self, stick):
        x, y = self.value[stick]
        if abs(y) > 0.98:
            self.value[stick][0] = 0

class Inputs:
    def __init__(self, controller, key, keydown, keyup, value, lifetime=10):
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
