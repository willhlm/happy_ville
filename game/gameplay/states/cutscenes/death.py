from .base.cutscene_engine import CutsceneEngine

class Death(CutsceneEngine):#when aila dies
    def __init__(self,game):
        super().__init__(game)
        self.stage = 0        

    def update(self, dt):
        super().update(dt)
        #if self.game.state_manager.state_stack[-1] != self: return#needed
        self.timer += dt
        if self.stage == 0:

            if self.timer > 120:
                self.state1()

        elif self.stage == 1:                
                #spawn effect
                pos = (0,0)#
                offset = 100#depends on the effect animation    
                self.spawneffect = Spawneffect(pos,self.game.game_objects)
                self.spawneffect.rect.midbottom=self.game.game_objects.player.rect.midbottom
                self.spawneffect.rect.bottom += offset
                self.game.game_objects.cosmetics.add(self.spawneffect)
                self.stage = 2

        elif self.stage == 2:
            if self.spawneffect.finish:#when the cosmetic effetc finishes        
                self.game.game_objects.player.currentstate.enter_state('respawn')
                self.game.state_manager.exit_state()

    def state1(self):
        if self.game.game_objects.player.backpack.map.spawn_point.get('bone', False):#respawn by bone
            map = self.game.game_objects.player.backpack.map.spawn_point['bone']['map']
            point = self.game.game_objects.player.backpack.map.spawn_point['bone']['point']
            del self.game.game_objects.player.backpack.map.spawn_point['bone']
        else:#normal resawn
            map = self.game.game_objects.player.backpack.map.spawn_point['map']
            point =  self.game.game_objects.player.backpack.map.spawn_point['point']        
        self.game.game_objects.load_map(self, map, point)
        self.stage = 1

    def handle_events(self,input):
        input.processed()

    def cinematic(self):
        pass
