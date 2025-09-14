import random
from gameplay.entities.items.base.item import Item
from engine.utils import read_files
from . import interactale_item_states

class InteractableItem(Item):#need to press Y to pick up - #key items: need to pick up instead of just colliding
    def __init__(self, pos, game_objects, **kwarg):
        super().__init__(pos, game_objects)        
        if kwarg.get('state', 'idle') == 'wild':#if it is spawn in the wild
            self.currentstate = interactale_item_states.Wild(self, **kwarg)
        else:
            self.currentstate = interactale_item_states.Idle(self, **kwarg)

    def update(self, dt):
        super().update(dt)
        self.perform_bounce()     
        self.bounce_directions.clear()     

    def pickup(self, player):
        self.game_objects.world_state.state[self.game_objects.map.level_name]['interactable_items'][type(self).__name__] = True#save in state file that the items on this map has picked up (assume that only one interactable item on each room)

    def twinkle(self):#called from interactale_item_states in wild state, in its update
        return
        pos = [self.hitbox.centerx + random.randint(-50, 50), self.hitbox.centery + random.randint(-50, 50)]
        twinkle = entities.Twinkle(pos, self.game_objects)#twinkle.animation.frame = random.randint(0, len(twinkle.sprites['idle']) - 1)
        self.game_objects.cosmetics.add(twinkle)

    def interact(self, player):#when player press T
        player.currentstate.enter_state('crouch')
        self.pickup(player)#object specific
        self.game_objects.game.state_manager.enter_state(state_name = 'Blit_image_text', image = self.sprites['idle'][0], text = self.description, callback = self.on_exit)
        self.kill()

    def on_exit(self):#called when eiting the blit_image_text state
        self.game_objects.player.currentstate.handle_input('pray_post')

    def kill(self):
        super().kill()
        self.game_objects.lights.remove_light(self.light)

    def set_owner(self, entity):
        self.entity = entity

    @classmethod
    def pool(cls, game_objects):
        cls.sprites['wild'] = read_files.load_sprites_list('assets/sprites/enteties/items/interactables_items/',game_objects)#the sprite to render when they are in the wild   