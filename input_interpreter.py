class InputInterpreter():
    def __init__(self, game_objects, double_tap_window = 10):
        self.game_objects = game_objects
        self.double_tap_window = double_tap_window
        self.inputs = {}

        self.double_tap_actions = {
            'x': {
                'single': 'x',
                'double': 'double_x',
            },
        }

    def interpret(self, input):
        event = input.output()
        key = event[-1]

        config = self.double_tap_actions.get(key)
        if not config: return input  # Non-configured key, pass through            

        press_info = self.inputs.setdefault(key, {'last_press_time': 0,'timer': None,'press': 0})

        if self.inputs[key]['press'] >= 1:            
            self.game_objects.timer_manager.remove_timer(press_info['timer'])
            self.inputs[key]['press'] = 0
            input.key = config['double']
            return input

        # Single press (set up delayed emission)
        def emit_single():
            input.key = config['single']
            self.inputs[key]['press'] = 0
            self.game_objects.player.currentstate.handle_press_input(input)

        self.inputs[key]['press'] += 1
        timer = self.game_objects.timer_manager.start_timer(self.double_tap_window, emit_single)                
        self.inputs[key]['timer'] = timer   
        input.key = None
        return input  # Don’t emit anything yet
