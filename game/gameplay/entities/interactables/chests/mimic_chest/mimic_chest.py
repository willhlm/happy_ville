from engine.utils import read_files
from gameplay.entities.interactables.base.interactables import Interactables

class MimicChest(Interactables):
    def __init__(self, pos, game_objects, content):
        super().__init__(pos, game_objects)
        self.sprites = read_files.load_sprites_dict('assets/sprites/entities/interactables/chests/' + type(self).__name__.lower() + '/', game_objects)
        self.image = self.sprites['idle'][0]
        self.rect = pygame.Rect(pos[0],pos[1],self.image.width,self.image.height)
        self.hitbox = pygame.Rect(pos[0],pos[1],32,32)
        self.hitbox.midbottom = self.rect.midbottom

    def update_render(self, dt):
        self.shader_state.update_render(dt)
   
    def take_dmg(self, effect):
        """Called by hit_component after modifiers run. Apply damage and effects."""
        
        
        # Play hurt sound
        self.shader_state.handle_input('hurt', colour = [1,1,1,1], direction = [1,0.5])
        
        return effect

