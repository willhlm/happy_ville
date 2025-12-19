from gameplay.entities.interactables.base.interactables import Interactables

class DoorInteract(Interactables): #game object for itneracting with locked door
    def __init__(self, pos, game_objects, door_obj):
        super().__init__(pos, game_objects)
        self.door = door_obj
        self.rect = door_obj.rect.copy()
        self.rect = self.rect.inflate(5,0)
        self.hitbox = self.rect.inflate(0,0)

    def interact(self):
        if type(self.door.currentstate).__name__ == 'Erect':
            if self.game_objects.player.backpack.inventory.get_quantity(self.door.key):
                self.door.currentstate.handle_input('Transform')
                if self.sfx: self.play_sfx()
            else:
                self.door.shake()

    def collision(self, entity):#player collision
        pass

    def update(self, dt):
        pass

    def draw(self, target):
        pass

    def release_texture(self):
        pass

