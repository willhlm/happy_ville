import platforms

class SeedSpawner():
    def __init__(self, arrow):
        self.arrow = arrow

    def spawn_ground(self, dir, block):
        pos, size = self.get_seed_placement(dir, [64, 16])
        platform = Seed_platform(pos, size, self.arrow.game_objects)
        self.arrow.game_objects.platforms.add(platform)

    def spawn_water(self, dir, block):
        pass

    def spawn_mushroom(self, dir, block):
        pass

    def get_seed_placement(self, dir, size):
        if dir == [-1, 0]:
            size = [64, 16]
            pos = self.arrow.hitbox.midleft
        elif dir == [1, 0]:
            size = [64, 16]
            pos = self.arrow.hitbox.midright
        elif dir == [0, -1]:
            size = [16, 64]
            pos = self.arrow.hitbox.midbottom
        elif dir == [0, 1]:
            size = [16, 64]
            pos = self.arrow.hitbox.midtop
        return pos, size

    def spawn_seed(self, dir, block):
        material = getattr(block, 'type', 'ground')
        spawn_method = getattr(self, f"spawn_{material}", self.spawn_ground)  # Default to ground
        spawn_method(dir, block)           

class Seed_platform(platforms.Collision_block):
    def __init__(self, pos, size, game_objects):
        super().__init__(pos, size)
        self.lifetime = 200

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

