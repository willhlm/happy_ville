import pygame, random
from engine.utils import read_files
from gameplay.narrative import dialogue

from gameplay.entities.base.character import Character
from gameplay.entities.npc import states_npc
from gameplay.entities.visuals.cosmetics import InteractableIndicator, ConversationBubbles

class NPC(Character):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.group = game_objects.npcs
        self.pause_group = game_objects.entity_pause
        self.load_sprites()
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1], 18, 40)
        self.rect.bottom = self.hitbox.bottom   #match bottom of sprite to hitbox

        self.currentstate = states_npc.Idle(self)
        self.dialogue = dialogue.Dialogue(self)#handles dialoage and what to say
        self.active_comment_bubble = None
        self.comment_timer_id = f"npc_comment:{id(self)}"
        self.comment_timer = None
        self.comment_scheduler = self.get_comment_scheduler_config()
        self.schedule_comment_timer(initial = True)

    def collision(self, entity):
        pass

    def on_noncollision(self, entity):
        self.indicator.kill()
        
    def on_collision(self, entity):        
        self.indicator = InteractableIndicator(self.rect.topright, self.game_objects)
        self.game_objects.cosmetics.add(self.indicator)

    def load_sprites(self, name):
        self.name = name
        self.sprites = read_files.load_sprites_dict("assets/sprites/entities/npc/" + name + "/animation/", self.game_objects)
        img = pygame.image.load('assets/sprites/entities/npc/' + name +'/potrait.png').convert_alpha()
        self.portrait = self.game_objects.game.display.surface_to_texture(img)#need to save in memoery

    def update(self, dt):
        super().update(dt)
        #self.group_distance()

    def render_potrait(self, terget):
        self.game_objects.game.display.render(self.portrait, terget, position = (32,32))#shader render

    def interact(self):#when plater press t
        self.game_objects.game.state_manager.enter_state('conversation', speaker = self)#pehrpame make a callback insted of "buissness"

    def random_conversation(self, text):#can say stuff through a text bubble           
        random_conv = ConversationBubbles(self.rect.topright,self.game_objects, text)
        self.game_objects.cosmetics.add(random_conv)
        self.active_comment_bubble = random_conv
        return random_conv

    def on_conversation_complete(self):
        pass

    def on_conversation_cancelled(self):
        pass

    def release_texture(self):#called when .kill() and empty group
        self.comment_timer = None
        self.game_objects.timer_manager.remove_ID_timer(self.comment_timer_id)
        super().release_texture()

    def get_comment_scheduler_config(self):
        config = {
            'enabled': bool(getattr(self.dialogue, 'comment_nodes', [])),
            'interval_min': 400,
            'interval_max': 900,
            'chance': 0.6,
            'radius': 180,
        }
        config.update(self.dialogue.get_comment_settings())
        return config

    def schedule_comment_timer(self, *, initial = False):
        if not self.comment_scheduler.get('enabled', False):
            return

        interval_min = self.comment_scheduler.get('interval_min', 400)
        interval_max = self.comment_scheduler.get('interval_max', interval_min)
        duration = random.randint(interval_min, max(interval_min, interval_max))
        if initial:
            duration = max(duration // 2, 1)

        self.comment_timer = self.game_objects.timer_manager.start_timer(duration, self.on_comment_timer, ID = self.comment_timer_id)

    def on_comment_timer(self):
        self.comment_timer = None
        try:
            self.try_emit_comment()
        finally:
            self.schedule_comment_timer()

    def try_emit_comment(self):
        if not self.can_emit_comment():
            return

        if random.random() > self.comment_scheduler.get('chance', 1.0):
            return

        text = self.dialogue.get_comment()
        if not text:
            return

        self.random_conversation(text)

    def can_emit_comment(self):
        if not self.comment_scheduler.get('enabled', False):
            return False

        if self.active_comment_bubble and self.active_comment_bubble.alive():
            return False

        if not self._is_player_nearby():
            return False

        return True

    def _is_player_nearby(self):
        player_center = self.game_objects.player.hitbox.center
        npc_center = self.hitbox.center
        dx = player_center[0] - npc_center[0]
        dy = player_center[1] - npc_center[1]
        radius = self.comment_scheduler.get('radius', 180)
        return dx * dx + dy * dy <= radius * radius
