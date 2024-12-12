import sys

class AI():
    def __init__(self, entity):
        self.entity = entity
        self.player_distance = [0,0]

    def enter_AI(self, newAI, **kwarg):
        self.entity.AI = getattr(sys.modules[__name__], newAI.capitalize())(self.entity, **kwarg)#make a class based on the name of the newstate: need to import sys

    def update(self):
        self.player_distance = [self.entity.game_objects.player.rect.centerx - self.entity.rect.centerx,self.entity.game_objects.player.rect.centery - self.entity.rect.centery]#check plater distance

    def deactivate(self):
        self.enter_AI('Idle')

    def handle_input(self, input):#input is hurt when taking dmg
        pass

class Idle(AI):#do nothing
    def __init__(self, entity, carry_dir = False,  timer = 90):
        super().__init__(entity)
        self.carry_dir = carry_dir
        self.idle_timer = timer

    def update(self):
        self.idle_timer -= 1
        if self.idle_timer == 0:
            if self.carry_dir:
                self.enter_AI('Walk', change_dir = True)
            else:
                self.enter_AI('Walk')

class Walk(AI):
    def __init__(self, entity, change_dir = False):
        super().__init__(entity)
        self.RETURN_FLAG = False
        if abs(self.entity.hitbox.x - self.entity.init_x) >= self.entity.patrol_dist:
            self.RETURN_FLAG = True
            self.entity.dir = [(self.entity.init_x - self.entity.hitbox.x)/abs(self.entity.hitbox.x - self.entity.init_x), self.entity.dir[1]]
        elif change_dir:
            self.entity.dir = [self.entity.dir[0] * -1, self.entity.dir[1]]

    def update(self):
        self.entity.walk()
        if self.check_ground(): self.enter_AI('Idle', carry_dir = True, timer = 50)
        elif self.check_wall(): self.enter_AI('Idle', carry_dir = True, timer = 50)
        if self.RETURN_FLAG:
            if abs(self.entity.hitbox.x - self.entity.init_x) < self.entity.patrol_dist:
                self.RETURN_FLAG = False
        elif abs(self.entity.hitbox.x - self.entity.init_x) > self.entity.patrol_dist:
            self.enter_AI('Idle')

    def check_ground(self):#this will always trigger when the enemy spawn, if they are spawn in air in tiled
        point = [self.entity.hitbox.midbottom[0] + self.entity.dir[0]*self.entity.hitbox[3],self.entity.hitbox.midbottom[1] + 8]
        collide = self.entity.game_objects.collisions.check_ground(point)
        if not collide:#there is no ground in front
            return True
        return False

    def check_wall(self):
        pass

#should the larva run away when attacked?
class Run_away(AI):
    def __init__(self,entity):
        super().__init__(entity)
