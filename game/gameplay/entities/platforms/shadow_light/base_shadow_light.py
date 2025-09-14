import pygame
from gameplay.entities.platforms.texture.base_texture import BaseTexture
from gameplay.entities.platforms.collisions.collision_block import CollisionBlock

class BaseShadowLight(BaseTexture):#parent class: add the subclasses to cosmetics group
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.platforms = []#keep diffeernt collision blocks to dynamically change the size

    def check_light(self):
        new_platforms = []
        for light in self.game_objects.lights.lights_sources:
            #if not light.shadow_light: continue
            if not self.hitbox.colliderect(light.hitbox): continue

            overlap_rect = self.hitbox.clip(light.hitbox)
            if len(new_platforms) < len(self.platforms):
                platform = self.platforms[len(new_platforms)]
                platform.hitbox = overlap_rect
                platform.rect = overlap_rect
            else:
                platform = CollisionBlock(overlap_rect.topleft, size=[overlap_rect.width, overlap_rect.height])
                self.game_objects.platforms.add(platform)

            new_platforms.append(platform)

        for platform in self.platforms[len(new_platforms):]:# Remove platforms that are no longer active
            self.game_objects.platforms.remove(platform)

        self.platforms = new_platforms# Update the platforms list

    def draw(self, target):
        #copy the light texture
        blit_pos = (int(self.rect[0]-self.game_objects.camera_manager.camera.scroll[0]),int(self.rect[1]-self.game_objects.camera_manager.camera.scroll[1]))
        self.cut_rect.topleft = blit_pos
        self.game_objects.game.display.render(self.game_objects.lights.layer3.texture, self.lights, flip = [False, True], section = self.cut_rect, shader = self.game_objects.shaders['reverse_y'])#cut out the light texture

        #blend
        self.game_objects.shaders['blend_shadow_light']['platform'] = self.image
        self.game_objects.game.display.render(self.lights.texture, target, position = blit_pos, shader = self.game_objects.shaders['blend_shadow_light'])#blend light and rectangle

    def release_texture(self):#called when .kill() and empty group
        super().release_texture()
        self.platforms = []
        self.lights.release()
