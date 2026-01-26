from gameplay.entities.platforms import Bubble, SeedPlatform

class SeedSpawner():
    def __init__(self, arrow):
        self.arrow = arrow

    def spawn_ground(self, dir):#default
        platform = SeedPlatform(self.arrow, self.arrow.game_objects, dir)
        self.arrow.game_objects.platforms.add(platform)

    def spawn_bubble(self):#called from twoDliquid collisions with arrow
        platform = Bubble(self.arrow.hitbox.midbottom, self.arrow.game_objects, lifetime = 400)
        self.arrow.game_objects.platforms.add(platform)

    def spawn_mushroom(self, dir, block):
        pass

    def spawn_seed(self, block, dir = None):
        material = getattr(block, 'type', 'ground')
        spawn_method = getattr(self, f"spawn_{material}", self.spawn_ground)  # Default to ground
        spawn_method(dir)
