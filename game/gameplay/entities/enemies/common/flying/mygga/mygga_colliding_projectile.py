from gameplay.entities.enemies.common.flying.mygga.mygga_colliding import MyggaColliding

class MyggaCollidingProjectile(MyggaColliding):#bounce around and eject projectiles
    def __init__(self,pos,game_objects):
        super().__init__(pos,game_objects)
        self.currentstate.enter_state('Roaming_attack', frequency = 100)

    def attack(self):#called from roaming AI
        dirs = [[1,1],[-1,1],[1,-1],[-1,-1]]
        for direction in dirs:
            obj = Projectile_1(self.hitbox.center, self.game_objects, dir = direction, amp = [3,3])
            self.game_objects.eprojectiles.add(obj)