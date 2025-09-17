from .base.cutscene_engine import CutsceneEngine

class RhouttaEncounter(CutsceneEngine):#called from trigger before first rhoutta: shuold spawn lightning and a gap spawns, or something -> TODO make a cutsene
    def __init__(self, game):
        super().__init__(game)
        spawn_pos = (1520-40,416-336)#topleft position in tiled - 40 to spawn it behind aila
        lightning = entities.Lighitning(spawn_pos,self.game.game_objects, parallax = [1,1], size = [64,336])
        effect = entities.Spawneffect(spawn_pos,self.game.game_objects)
        effect.rect.midbottom = lightning.rect.midbottom
        self.game.game_objects.interactables.add(lightning)
        self.game.game_objects.cosmetics.add(effect)
        self.game.game_objects.weather.flash()
