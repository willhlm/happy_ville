class InputInterpreter():#mashing
    def __init__(self, game_objects, grace_period_frames = 2, flick_threshold = 0.4):
        self.game_objects = game_objects
        self.grace_period_frames = grace_period_frames
        self.flick_threshold = flick_threshold
        self.last_l_stick = [0, 0]
        self.last_flick_time = grace_period_frames

    def update(self):#check for flicking
        prev_x = self.last_l_stick[0]
        curr_x = self.game_objects.controller.value['l_stick'][0]       
        self.last_flick_time += self.game_objects.game.dt

        if abs(curr_x) > self.flick_threshold and abs(curr_x - prev_x) > 0.4:
            self.last_flick_time = 0

        self.last_l_stick = self.game_objects.controller.value['l_stick']        

    def interpret(self, input):
        if input.key == 'x':
            if self.last_flick_time < self.grace_period_frames:
                input.key = 'smash_x'
        return input