from gameplay.entities.platforms.base.platform import Platform

class BaseTexture(Platform):#blocks that has tectures
    def __init__(self, pos, game_objects):
        super().__init__(pos)
        self.game_objects = game_objects
        self.dir = [1,0]#states need it

    def update(self, dt):
        self.currentstate.update(dt)
    
    def update_render(self, dt):                
        self.animation.update(dt)

    def collide_x(self,entity):
        if entity.velocity[0] > 0:#going to the right
            entity.right_collision(self)
        else:#going to the leftx
            entity.left_collision(self)
        entity.update_rect_x()

    def collide_y(self,entity):
        if entity.velocity[1] > 0:#going down
            entity.down_collision(self)
            entity.limit_y()
        else:#going up
            entity.top_collision(self)
        entity.update_rect_y()

    def reset_timer(self):#aniamtion need it
        self.currentstate.increase_phase()

    def release_texture(self):#called when .kill() and empty group
        for state in self.sprites.keys():
            for frame in range(0,len(self.sprites[state])):
                self.sprites[state][frame].release()

    def draw(self, target):
        self.game_objects.game.display.render(self.image, target, position = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])))#int seem nicer than round
