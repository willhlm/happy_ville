class Timer_manager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.timers = {}# Dictionary to store timers with IDs or default "normal" key

    def start_timer(self, duration, callback, ID = 'normal'):# Create and store the timer in the dictionary
        timer = Timer(self, duration, callback, ID)
        self.timers.setdefault(ID, [])# Initialize the list for this ID if not already created
        self.timers[ID].append(timer)
        return timer

    def remove_ID_timer(self, ID):# Remove all timers associated with this ID
        if ID in self.timers:
            del self.timers[ID]

    def remove_timer(self, timer):# Remove the specific timer from its ID category
        print('heej')
        print(timer.ID)
        self.timers[timer.ID].remove(timer)
        if not self.timers[timer.ID]:  # Clean up if there are no more timers under this ID
            del self.timers[timer.ID]

    def clear_timers(self):
        self.timers = {}  # Clear all timers

    def update(self):# Iterate through all timers in the dictionary, but do it safely
        for timers in list(self.timers.values()):  # Creating a copy of the values list for safe iteration
            for timer in timers[:]:  # Safe iteration over each list of timers
                timer.update()

class Timer():
    def __init__(self, timer_manager, duration, callback, ID):
        self.timer_manager = timer_manager
        self.duration = duration
        self.original_duration = duration
        self.callback = callback
        self.ID = ID

    def update(self):# Decrease the timer duration based on the game’s delta time
        self.duration -= self.timer_manager.game_objects.game.dt  # Adjusted based on frame time
        if self.duration <= 0:
            self.callback()  # Trigger the callback when the timer ends
            self.remove()  # Remove the timer from the manager

    def remove(self):# Remove the timer from the appropriate category (ID group)
        self.timer_manager.remove_timer(self)

    def reset(self):# Reset the timer back to its original duration
        self.duration = self.original_duration
