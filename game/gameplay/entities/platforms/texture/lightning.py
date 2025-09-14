class Lighitning(StaticEntity):#a shader to make lighning barrier
    def __init__(self, pos, game_objects, parallax, size):
        super().__init__(pos, game_objects)
        self.parallax = parallax

        self.image = game_objects.game.display.make_layer(size).texture
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],self.image.width*0.8,self.rect[3])
        self.time = 0

    def release_texture(self):
        self.image.release()

    def update(self, dt):
        self.time += dt * 0.01

    def draw(self, target):
        self.game_objects.shaders['lightning']['TIME'] = self.time
        blit_pos = [self.rect.topleft[0] - self.parallax[0]*self.game_objects.camera_manager.camera.scroll[0], self.rect.topleft[1] - self.parallax[1]*self.game_objects.camera_manager.camera.scroll[1]]
        self.game_objects.game.display.render(self.image, self.game_objects.game.screen, position = blit_pos, shader = self.game_objects.shaders['lightning'])

    def player_collision(self):#player collision
        pm_one = sign(self.game_objects.player.hitbox.center[0]-self.hitbox.center[0])
        self.game_objects.player.take_dmg(dmg = 1, effects = [lambda: self.game_objects.player.knock_back(amp = [50, 0], dir = [pm_one, 0])])
        self.game_objects.player.currentstate.handle_input('interrupt')#interupts dash

    def player_noncollision(self):
        pass