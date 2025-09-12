import random
from gameplay.entities.items.base.item import Item

class EnemyDrop(Item):
    def __init__(self, pos, game_objects):
        super().__init__(pos, game_objects)
        self.lifetime = 500
        self.velocity = [random.uniform(-3, 3),-3]                

    def update(self, dt):
        super().update(dt)
        self.lifetime -= dt
        self.destory()        
        self.perform_bounce()     
        self.bounce_directions.clear()             

    def attract(self,pos):#the omamori calls on this in loot group
        if self.lifetime < 350:
            self.velocity = [0.1*(pos[0]-self.rect.center[0]),0.1*(pos[1]-self.rect.center[1])]

    def destory(self):
        if self.lifetime < 0:#remove after a while
            self.kill()

    def player_collision(self, player):#when the player collides with this object
        if self.currentstate.__class__.__name__ == 'Death': return#enter only once
        self.game_objects.sound.play_sfx(self.sounds['death'][0])#should be in states        
        self.currentstate.handle_input('Death')
        player.backpack.inventory.add(self)   