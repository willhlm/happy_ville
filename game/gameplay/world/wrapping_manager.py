'if we want infinite scroller. Doesnt work maybe'

class WrappingManager():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.enabled = True
        self.world_width = 1920
    
    def update(self, dt):
        """Called once per frame in States_maps.update()"""
        if not self.enabled or self.world_width <= 0:
            return
        
        # Wrap all entities
        for group in [self.game_objects.players, self.game_objects.enemies, self.game_objects.npcs,
                      self.game_objects.fprojectiles, self.game_objects.eprojectiles, self.game_objects.loot]:
            for entity in group:
                entity.true_pos[0] = entity.true_pos[0] % self.world_width
                entity.hitbox.x = entity.true_pos[0]
        
        # Wrap collision blocks
        # (blocks don't move, but we need phantom copies for collision)
    
    def wrap_entity(self, entity):
        """Wrap a single entity's position"""
        if not self.enabled or self.world_width <= 0:
            return
        
        entity.true_pos[0] = entity.true_pos[0] % self.world_width
        try:
            entity.hitbox.x = entity.true_pos[0]
        except:
            pass

        

    def get_collision_blocks(self):
        """Returns blocks + phantom copies for collision detection"""
        if not self.enabled:
            return
        blocks = self.game_objects.platforms.sprites()

        camera = self.game_objects.camera_manager.camera
        view_left = camera.x - camera.width / 2 - 100  # margin
        view_right = camera.x + camera.width / 2 + 100
        
        all_blocks = list(blocks)
        
        # Add phantom copies of blocks near edges
        for block in blocks:
            # If block is on right side, add left phantom
            if block.rect.right > self.world_width - 200:
                phantom = self._make_phantom(block, -self.world_width)
                if view_left < phantom.rect.x < view_right:
                    all_blocks.append(phantom)
            
            # If block is on left side, add right phantom
            if block.rect.left < 200:
                phantom = self._make_phantom(block, self.world_width)
                if view_left < phantom.rect.x < view_right:
                    all_blocks.append(phantom)
        
        self.game_objects.platforms.add(all_blocks)
            
    def _make_phantom(self, block, offset):
        """Create a temporary phantom copy of a block"""
        phantom = type(block).__new__(type(block))  # Create without calling __init__
        phantom.rect = block.rect.copy()
        phantom.rect.x += offset
        try:
            phontom.hitbox = phantom.rect.copy()
        except:
            pass
        return phantom

    def draw_wrapped(self, entity, target, draw_func):
        """Wrapper for entity drawing"""
        if not self.enabled:
            draw_func(target)
            return
        
        camera = self.game_objects.camera_manager.camera
        view_left = camera.x - camera.width / 2
        view_right = camera.x + camera.width / 2
        
        # Draw at original position
        draw_func(target)
        
        # Draw phantoms if needed
        x = entity.true_pos[0]
        
        # Left phantom
        if x > self.world_width - 200:
            original = entity.true_pos[0]
            entity.true_pos[0] -= self.world_width
            draw_func(target)
            entity.true_pos[0] = original
        
        # Right phantom
        if x < 200:
            original = entity.true_pos[0]
            entity.true_pos[0] += self.world_width
            draw_func(target)
            entity.true_pos[0] = original        

    def draw_phantoms(self, entity, target):
        """Draw phantom copies if entity is near edges"""
        if not self.enabled or self.world_width <= 0:
            return
        
        camera = self.game_objects.camera_manager.camera
        x = entity.true_pos[0]
        
        # Draw left phantom if entity is near right edge
        if x > self.world_width - 640 / 2 - 100:
            original = entity.true_pos[0]
            entity.true_pos[0] -= self.world_width
            entity.draw(target)
            entity.true_pos[0] = original
        
        # Draw right phantom if entity is near left edge
        if x < 640 / 2 + 100:
            original = entity.true_pos[0]
            entity.true_pos[0] += self.world_width
            entity.draw(target)
            entity.true_pos[0] = original            