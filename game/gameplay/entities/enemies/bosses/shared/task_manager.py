import random

class TaskManager():#manager
    def __init__(self, entity, state_registry, patterns):
        self.entity = entity
        self.state_registry = state_registry
        self.selector = PatternSelector(entity, patterns)        
        self.task_queue = []  # Tasks to execute in order
        self.state = state_registry['idle'](self.entity)        
        
    def update(self, dt):
        self.track_player_distance()
        self.state.update(dt)
 
    def track_player_distance(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx, self.entity.game_objects.player.rect.centery - self.entity.rect.centery]

    def start_next_task(self):#start when state is finished        
        kwarg = self.task_queue.pop(0)        
        task_name = kwarg.pop("task")
        self.state = self.state_registry[task_name.lower()](self.entity, **kwarg)

        if kwarg.pop("repeat", False):
            self.queue_task(task=task_name, **kwarg)

    def queue_task(self, **kwarg):
        self.task_queue.append(kwarg)

    def clear_tasks(self):
        self.task_queue.clear()  # Clear current tasks

    def handle_input(self, input):
        self.state.handle_input(input)
    
    def increase_phase(self):
        self.state.increase_phase()

    def enter_state(self, newstate):
        self.clear_tasks()
        self.queue_task(task = newstate)
        self.start_next_task()        

class PatternSelector():
    def __init__(self, entity, patterns):
        self.entity = entity
        self.patterns = patterns

    def get_valid_ranges(self, dist_x, dist_y):
        ax = abs(dist_x)
        ay = abs(dist_y)

        if ax < self.entity.attack_distance[0] and ay < self.entity.attack_distance[1]:
            return ["close", "mid", "far"]
        elif ax < self.entity.jump_distance[0] and ay < self.entity.jump_distance[1]:
            return ["mid", "far"]
        else:
            return ["far"]

    def pick_pattern(self, dist_x, dist_y):#caleld from think
        valid_ranges = self.get_valid_ranges(dist_x, dist_y)
        options = [name for name, data in self.patterns.items() if data["range"] in valid_ranges or data["range"] == "any"]
        weights = [self.patterns[name]["weight"] for name in options]
        return self.patterns[random.choices(options, weights=weights, k=1)[0]]