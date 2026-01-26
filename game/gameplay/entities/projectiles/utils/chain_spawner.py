from gameplay.entities.base.static_entity import StaticEntity

class ChainSpawner(StaticEntity):
    def __init__(self, pos, game_objects, projecticle, direction, distance, number, frequency):
        super().__init__(pos, game_objects)
        self.pos = pos#inital position
        self.projecticle = projecticle
        self.game_objects = game_objects
        self.direction = direction
        self.distance = distance
        self.number = number
        self.spawn_number = 0
        self.frequency = frequency
        self.time = frequency
        self.spawn()

    def draw(self, target):
        pass

    def release_texture(self):
        pass

    def update(self, dt):
        self.time -= dt
        if self.time <= 0:
            self.spawn()
            self.time = self.frequency#reset the timer

    def spawn(self):
        if self.spawn_number >= self.number:
            self.kill()
            return
        pos = [self.pos[0] + self.direction[0] * self.distance * self.spawn_number, self.pos[1]+ self.direction[1] * self.distance * self.spawn_number]
        self.game_objects.eprojectiles.add(self.projecticle(pos, self.game_objects, dir = self.direction))
        self.spawn_number += 1   