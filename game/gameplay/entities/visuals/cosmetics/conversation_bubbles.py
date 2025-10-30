from gameplay.entities.base.static_entity import StaticEntity
import math

class ConversationBubbles(StaticEntity):#the thing npcs have hoovering above them for random messages
    def __init__(self, pos, game_objects, text, lifetime = 200, size = (32,32)):
        super().__init__(pos, game_objects)
        self.render_text(text)

        self.lifetime = lifetime
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        size = (32,32)
        ConversationBubbles.layer = game_objects.game.display.make_layer(size)
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

    def render_text(self, text):
        texture = self.game_objects.font.render(text = text)
        self.game_objects.game.display.render(self.bg, self.layer)#shader render
        self.game_objects.game.display.render(texture, self.layer, position = [10, self.rect[3]])#shader render
        self.image = self.layer.texture
        texture.release()

#shader base
