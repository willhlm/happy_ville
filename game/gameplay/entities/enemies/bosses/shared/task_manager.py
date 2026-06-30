import random
from gameplay.entities.enemies.common.shared.state_machine.cooldown_manager import CooldownManager

class TaskManager():#manager
    def __init__(self, entity, state_registry, patterns, selector_config):
        self.entity = entity
        self.state_registry = state_registry
        self.patterns = patterns
        self.cooldowns = CooldownManager()
        self.selector = build_pattern_selector(entity, patterns, selector_config)
        self.task_queue = []  # Tasks to execute in order
        self.state = state_registry['idle'](self.entity)        
        
    def update(self, dt):
        self.cooldowns.update(dt)
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

    def set_pattern_cycle(self, pattern_cycle, reset=False):
        self.selector.set_pattern_cycle(pattern_cycle, reset=reset)

    def handle_input(self, input):
        self.state.handle_input(input)

    def consume_contact_state(self):
        current_state = getattr(self, 'state', None)
        if current_state and hasattr(current_state, 'consume_contact_state'):
            current_state.consume_contact_state()
    
    def increase_phase(self):
        self.state.increase_phase()

    def enter_state(self, newstate):
        self.clear_tasks()
        self.queue_task(task = newstate)
        self.start_next_task()    

    def die(self):
        self.entity.flags['aggro'] = False
        death_cls = self.state_registry['death']
        dead_cls = self.state_registry['dead']
        if isinstance(self.state, death_cls) or isinstance(self.state, dead_cls):
            return

        self.entity.killed()
        self.clear_tasks()
        self.state = death_cls(self.entity)
   
class BasePatternSelector():
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

    def set_pattern_cycle(self, pattern_cycle, reset=False):
        return None

    def is_pattern_available(self, name, data):
        cooldown_name = data.get("cooldown")
        if not cooldown_name:
            return True
        return self.entity.currentstate.cooldowns.get(cooldown_name) <= 0

    def pick_pattern(self, dist_x, dist_y):#caleld from think
        pass

class RandomPatternSelector(BasePatternSelector):
    def pick_pattern(self, dist_x, dist_y):#caleld from think
        valid_ranges = self.get_valid_ranges(dist_x, dist_y)
        options = [
            name for name, data in self.patterns.items()
            if (data["range"] in valid_ranges or data["range"] == "any")
            and self.is_pattern_available(name, data)
        ]
        if not options:
            return None
        weights = [self.patterns[name].get("weight", 1) for name in options]
        return self.patterns[random.choices(options, weights=weights, k=1)[0]]

class DeterministicPatternSelector(BasePatternSelector):
    def __init__(self, entity, patterns, pattern_cycle):
        super().__init__(entity, patterns)
        self.pattern_cycle = pattern_cycle
        self.index = 0

    def set_pattern_cycle(self, pattern_cycle, reset=False):
        self.pattern_cycle = pattern_cycle
        if reset:
            self.index = 0

    def pick_pattern(self, dist_x, dist_y):
        if not self.pattern_cycle:
            raise ValueError("Deterministic pattern selector requires at least one pattern")

        valid_ranges = self.get_valid_ranges(dist_x, dist_y)
        for offset in range(len(self.pattern_cycle)):
            cycle_index = (self.index + offset) % len(self.pattern_cycle)
            pattern_name = self.pattern_cycle[cycle_index]
            pattern = self.patterns[pattern_name]
            if (
                (pattern["range"] in valid_ranges or pattern["range"] == "any")
                and self.is_pattern_available(pattern_name, pattern)
            ):
                self.index = (cycle_index + 1) % len(self.pattern_cycle)
                return pattern

        return None

def build_pattern_selector(entity, patterns, selector_config):
    if selector_config['mode'] == 'deterministic':
        return DeterministicPatternSelector(
            entity,
            patterns,
            pattern_cycle=selector_config['pattern_cycle'],
        )
    if selector_config['mode'] == 'random':
        return RandomPatternSelector(entity, patterns)
    raise ValueError(f"Unknown selector mode: {selector_config['mode']}")
