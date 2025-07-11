class InputInterpreter():#mashing
    def __init__(self, game_objects, grace_period_frames = 10, flick_threshold = 0.4):
        self.game_objects = game_objects
        self.grace_period_frames = grace_period_frames
        self.flick_threshold = flick_threshold
        self.last_l_stick = [0, 0]
        self.last_flick_time = [grace_period_frames, grace_period_frames]#horizontal and vertical
        self.flick_direction = [0, 0]

    def update(self):#check for flicking: called from game.py
        prev_x = self.last_l_stick[0]        
        curr_x = self.game_objects.controller.value['l_stick'][0]     
        prev_y = self.last_l_stick[1]        
        curr_y = self.game_objects.controller.value['l_stick'][1]

        self.last_flick_time[0] += self.game_objects.game.dt
        self.last_flick_time[1] += self.game_objects.game.dt

        self.last_l_stick = self.game_objects.controller.value['l_stick']          

        if abs(curr_x) > self.flick_threshold and abs(curr_x - prev_x) > 0.4:
            self.last_flick_time[0] = 0 
            self.flick_direction[0] = self.sign(curr_x)               
        elif abs(curr_y) > self.flick_threshold and abs(curr_y - prev_y) > 0.4:
            self.last_flick_time[1] = 0    
            self.flick_direction[1] = self.sign(curr_y)                   

    def interpret(self, input):
        if input.key == 'x':
            if self.last_flick_time[0] < self.grace_period_frames:      
                print('fe')          
                if self.flick_direction[0] > 0:
                    input.meta = {'smash': True, 'direction': 'right'}
                else:
                    input.meta = {'smash': True, 'direction': 'left'}

            elif self.last_flick_time[1] < self.grace_period_frames:
                if self.flick_direction[1] > 0:
                    input.meta = {'smash': True, 'direction': 'down'}
                else:
                    input.meta = {'smash': True, 'direction': 'up'}        
        return input

    @staticmethod
    def sign(number):
        if number > 0: return 1
        return -1
