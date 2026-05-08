from engine.utils.functions import sign

from gameplay.entities.shared.components.body.entity_body import EntityBody


class MeleeBody(EntityBody):
    def __init__(self, entity):
        super().__init__(entity)
        self.direction_mapping = {
            (0, 0): ('center', 'center'),
            (1, 1): ('midbottom', 'midtop'),
            (-1, 1): ('midbottom', 'midtop'),
            (1, -1): ('midtop', 'midbottom'),
            (-1, -1): ('midtop', 'midbottom'),
            (1, 0): ('midleft', 'midright'),
            (-1, 0): ('midright', 'midleft'),
        }

    def update_hitbox(self):
        rounded_dir = (sign(self.entity.dir[0]), sign(self.entity.dir[1]))
        hitbox_attr, entity_attr = self.direction_mapping[rounded_dir]
        setattr(self.entity.hitbox, hitbox_attr, getattr(self.entity.entity.hitbox, entity_attr))
        self.entity.rect.center = self.entity.hitbox.center

class SwordBody(MeleeBody):
    def update_hitbox(self):
        super().update_hitbox()
        self.entity.currentstate.update_rect()
