from gameplay.entities.projectiles.base.projectiles import Projectiles

def sign(number):
    if number == 0: return 0
    elif number > 0: return 1
    else: return -1

class Melee(Projectiles):
    def __init__(self, entity, **kwarg):
        super().__init__([0,0], entity.game_objects, **kwarg)
        self.entity = entity#needs entity for making the hitbox follow the player in update hitbox
        self.dir = kwarg.get('dir', entity.dir.copy())
        self.direction_mapping = {(0, 0): ('center', 'center'), (1, 1): ('midbottom', 'midtop'),(-1, 1): ('midbottom', 'midtop'), (1, -1): ('midtop', 'midbottom'),(-1, -1): ('midtop', 'midbottom'),(1, 0): ('midleft', 'midright'),(-1, 0): ('midright', 'midleft')}

    def collision_enemy(self, collision_enemy):#projecticle enemy collision (including player)
        if self.flags['aggro']:
            pm_one = sign(collision_enemy.hitbox.center[0]-self.entity.hitbox.center[0])
            collision_enemy.take_dmg(dmg = self.dmg, effects = [lambda: collision_enemy.knock_back(amp = [25, 0], dir = [pm_one, 0])])

    def update_hitbox(self):#called from update hirbox in plaform entity
        rounded_dir = (sign(self.dir[0]), sign(self.dir[1]))#analogue controls may have none integer values
        hitbox_attr, entity_attr = self.direction_mapping[rounded_dir]
        setattr(self.hitbox, hitbox_attr, getattr(self.entity.hitbox, entity_attr))
        self.rect.center = self.hitbox.center#match the positions of hitboxes

    def reflect(self, dir, pos):#called from sword collision_projectile, purple initinty stone
        return
        self.entity.countered()
        self.kill()

    def update_rect_y(self):
        pass

    def update_rect_x(self):
        pass