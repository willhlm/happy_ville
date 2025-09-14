import pygame
from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class FastTravel(Interactables):
    cost = 50
    def __init__(self,pos,game_objects,map):
        super().__init__(pos,game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/animations/fast_travel/',game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = self.rect.copy()
        self.map = map
        self.init_cord = [pos[0],pos[1]-100]

        try:#if it has been unlocked
            self.game_objects.world_state.travel_points[map]
            self.locked = False
        except:
            self.locked = True#starts locked. After paying some ambers, it unlocks and fast travel is open

    def unlock(self):#called from Fast_travel_unlock
        if self.game_objects.player.backpack.inventory.get_quantity('amber_droplet') > self.cost:
            self.game_objects.player.backpack.inventory.remove('amber_droplet', self.cost)
            self.locked = False
            Fast_travel.cost *= 5#increase by 5 for every unlock
            self.game_objects.backpack.map.save_travelpoint(self.map,self.init_cord)
            return True
        else:
            return False

    def interact(self):#when player press t/y
        if self.locked:
            self.game_objects.game.state_manager.enter_state(state_name = 'Fast_travel_unlock', category = 'game_states_facilities', fast_travel = self)
        else:
            self.currentstate.handle_input('Once',animation_name = 'once',next_state='Idle')
            self.game_objects.game.state_manager.enter_state(state_name = 'Fast_travel_menu', category = 'game_states_facilities')

