from gameplay.entities.base.static_entity import StaticEntity
import math

class ConversationBubbles(StaticEntity):#the thing npcs have hoovering above them for random messages
    def __init__(self, pos, game_objects, text, lifetime = 200, size = (32,32)):
        super().__init__(pos, game_objects)    
        self.text = text   
        self.lifetime = lifetime
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        ConversationBubbles.bg = game_objects.font.fill_text_bg(size, 'text_bubble')

    def release_texture(self):
        pass

    def update(self, dt):
        self.time += dt * 0.1
        self.update_vel()
        self.update_pos(dt)
        self.lifetime -= dt
        if self.lifetime < 0:
            self.kill()

    def update_pos(self, dt):
        self.true_pos = [self.true_pos[0] + self.velocity[0]*dt,self.true_pos[1] + self.velocity[1]*dt]
        self.rect.topleft = self.true_pos

    def update_vel(self):
        self.velocity[1] = 0.25*math.sin(self.time)

    def draw(self, target):
        position = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]

        self.game_objects.game.display.render(self.bg, target, position = position)#shader render
        self.game_objects.game.display.render_text(self.game_objects.font.font_atals, target, text = self.text, letter_frame = 9999, color = (0, 0, 0, 255), position = position)
        