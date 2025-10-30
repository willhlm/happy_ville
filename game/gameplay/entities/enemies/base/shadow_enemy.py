from gameplay.entities.enemies.base.enemy import Enemy

class ShadowEnemy(Enemy):#enemies that can onlly take dmg in light -> dark forst
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)

    def check_light(self):
        for light in self.game_objects.lights.lights_sources:
            if not light.shadow_interact: continue
            collision = self.hitbox.colliderect(light.hitbox)
            if collision:
                self.light()
                return
        self.no_light()

    def no_light(self):
        self.flags['invincibility'] = True

    def light(self):
        self.flags['invincibility'] = False