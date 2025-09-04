import sys

class Basic_states():
    def __init__(self,camera_manager):
        self.camera_manager = camera_manager

    def update(self):
        pass

    def enter_state(self,newstate,**kwarg):
        self.camera_manager.centraliser = getattr(sys.modules[__name__], newstate.capitalize())(self.camera_manager,**kwarg)#make a class based on the name of the newstate: need to import sys

    def handle_input(self, input, **kwarg):
        pass

    def handle_movement(self):#right analogue stick
        pass

class Idle(Basic_states):
    def __init__(self,camera_manager, **kwarg):
        super().__init__(camera_manager)

    def handle_movement(self, value):
        if max(abs(value[0]), abs(value[1])) > 0:
            self.enter_state('shift')

    def handle_input(self, input, **kwarg):#can be called from stop handleere
        if input == 'start':
            self.enter_state('centraliser', **kwarg)

class Shift(Basic_states):
    def __init__(self,camera_manager,**kwarg):
        super().__init__(camera_manager)
       
    def handle_movement(self, value):
        new_x = self.camera_manager.camera.center[0] - value[0]
        new_y = self.camera_manager.camera.center[1] - value[1]

        max_displacement = [100, 50]
        self.camera_manager.camera.center[0] = max(self.camera_manager.camera.original_center[0] - max_displacement[0], min(self.camera_manager.camera.original_center[0] + max_displacement[0], new_x))
        self.camera_manager.camera.center[1] = max(self.camera_manager.camera.original_center[1] - max_displacement[1], min(self.camera_manager.camera.original_center[1] + max_displacement[1], new_y)) 

        if max(abs(value[0]), abs(value[1])) == 0:#no input
            self.enter_state('centraliser')
        
class Centraliser(Basic_states):
    def __init__(self, camera_manager, **kwarg):
        super().__init__(camera_manager)       
        self.camera_manager = camera_manager    
        self.direction = kwarg.get('direction', [1, 1])#can put to zero if we only want to centralise one axis: need to fix exit_state if we need this functionallity
        self.smoothing_factor = [0.05 * self.direction[0], 0.05  * self.direction[1]].copy()

    def update(self):
        self.camera_manager.camera.center[0] += (self.camera_manager.camera.target[0] - self.camera_manager.camera.center[0]) * self.smoothing_factor[0]
        self.camera_manager.camera.center[1] += (self.camera_manager.camera.target[1] - self.camera_manager.camera.center[1]) * self.smoothing_factor[1]

        #self.camera_manager.camera.center[0] += sign(self.camera_manager.camera.original_center[0] - self.camera_manager.camera.center[0])
        #self.camera_manager.camera.center[1] += sign(self.camera_manager.camera.original_center[1] - self.camera_manager.camera.center[1])

        self.exit_state()

    def exit_state(self):#when centered
        if self.direction[0] * abs(self.camera_manager.camera.center[0] - self.camera_manager.camera.original_center[0]) < 0.1 and self.direction[1] * abs(self.camera_manager.camera.center[1] - self.camera_manager.camera.original_center[1]) < 0.1:
            self.enter_state('idle')

    def handle_movement(self, value):
        if max(abs(value[0]), abs(value[1])) > 0:
            self.enter_state('shift')

    def handle_input(self, input, **kwarg):#can be called from stop handleere
        if input == 'stop':
            self.enter_state('idle', **kwarg)
