from gameplay.entities.base.static_entity import StaticEntity
import math
from engine.utils import read_files

class ConversationBubbles(StaticEntity):#the thing npcs have hoovering above them for random messages
    BUBBLE_LAYOUTS = {
        'small': {'max_text_width': 18, 'text_box': (9, 13, 18, 12)},
        'medium': {'max_text_width': 26, 'text_box': (7, 13, 26, 12)},
        'large': {'max_text_width': 34, 'text_box': (7, 13, 34, 12)},
    }

    def __init__(self, pos, game_objects, text, lifetime = 200, size = (32,32)):
        super().__init__(pos, game_objects)    
        self.text = text
        self.lifetime = lifetime
        self.rect.bottomleft = pos
        self.true_pos = self.rect.topleft
        self.bubble_size = self._select_bubble_size()
        self.text_box = self.BUBBLE_LAYOUTS[self.bubble_size]['text_box']

        self.time = 0
        self.velocity = [0,0]

    def pool(game_objects):
        ConversationBubbles.sprites = read_files.load_sprites_dict("assets/sprites/entities/visuals/cosmetics/text_bubble/", game_objects)

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

    def _select_bubble_size(self):
        text_width, _ = self.game_objects.font.measure(self.text)
        for bubble_size in ('small', 'medium', 'large'):
            if text_width <= self.BUBBLE_LAYOUTS[bubble_size]['max_text_width']:
                return bubble_size
        return 'large'

    def draw(self, target):
        position = [int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1])]

        self.game_objects.game.display.render(self.sprites[self.bubble_size][0], target, position=position)

        self.game_objects.font.render(
            target,
            self.text,
            letter_frame=None,
            color=(0, 0, 0, 255),
            alignment='center',
            position=(position[0] + self.text_box[0], position[1] + self.text_box[1]),
            width=self.text_box[2],
        )
        
