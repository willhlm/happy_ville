from gameplay.entities.platforms.base.solid_platform import SolidPlatform


class TexturedPlatform(SolidPlatform):
    def __init__(self, pos, game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.dir = [1, 0]

    def update(self, dt):
        self.currentstate.update(dt)

    def update_render(self, dt):
        self.animation.update(dt)

    def reset_timer(self):
        self.currentstate.increase_phase()

    def release_texture(self):
        for state in self.sprites.keys():
            for frame in range(0, len(self.sprites[state])):
                self.sprites[state][frame].release()

    def draw(self, target):
        self.game_objects.game.display.render(
            self.image,
            target,
            position=(
                int(self.rect[0] - self.game_objects.camera_manager.camera.scroll[0]),
                int(self.rect[1] - self.game_objects.camera_manager.camera.scroll[1]),
            ),
        )
