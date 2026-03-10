import pygame
from gameplay.entities.platforms.collisions.collision_block import CollisionBlock

class EvilGate(CollisionBlock):#a gate. The ones that are owned by the lever will handle if the gate should be erect or not by it
    def __init__(self, pos, game_objects, size, **kwarg):
        super().__init__(pos, size)
        self.game_objects = game_objects
        self.ID_key = kwarg.get("ID", None)                
        erect = self.game_objects.world_state.load_bool(self.game_objects.map.level_name, "gate", self.ID_key, initial=kwarg.get("erect", False))

        self.image = game_objects.game.display.make_layer(size)
        self.rect = pygame.Rect(pos[0], pos[1], self.image.width, self.image.height)

        self.time = 0

    def update_render(self, dt):
        self.time += dt 
    
    def release_texture(self):
        self.image.release()

    def draw(self, target):
        self.game_objects.shaders['evil_gate']['u_time'] = self.time * 0.01
        pos = (int(self.true_pos[0] - self.game_objects.camera_manager.camera.scroll[0]),int(self.true_pos[1] - self.game_objects.camera_manager.camera.scroll[1]))
        self.game_objects.game.display.render(self.image.texture, target, position = pos, shader = self.game_objects.shaders['evil_gate'])#shader render            