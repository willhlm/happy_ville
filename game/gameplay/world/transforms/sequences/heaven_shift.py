from gameplay.entities.interactables import Portal

class HeavenIntro():
    def __init__(self, game_objects, source_pos):
        self.game_objects = game_objects
        self.source_pos = source_pos
        self.timer = 0.0
        self.finished = False
        self.phase = 0
        self.did_tile_swap = False
        self.did_spawn = False

        self._begin()

    def _begin(self):
        player = self.game_objects.player
        self.game_objects.cosmetics.add(Portal(self.source_pos, self.game_objects))
        #player.lock_input(duration=0.3)

        #self.game_objects.game.screen_manager.append_shader('Vignette', ['bg1'], vignette_opacity=0, colour=[1, 1, 1, 1])

        #self.game_objects.audio.fade_ambience(target_volume=0.3, duration=1.0)
        #self.game_objects.particles.pull_upward(center=self.source_pos, duration=1.0)

    def update_render(self, dt):
        self.timer += dt

        #self._update_visuals()

        if self.timer >= 0.5 and not self.did_tile_swap:
            self.did_tile_swap = True
            #self.game_objects.world.replace_skybox("heaven")
            #self.game_objects.world.swap_tiles_in_radius(center=self.source_pos, radius=600,ruleset="forest_to_heaven")

        if self.timer >= 1.0 and not self.did_spawn:
            self.did_spawn = True
            #self.game_objects.world.spawn_set("heaven_intro", near=self.source_pos)

        if self.timer >= 2.0:
            self._finish()

    def _update_visuals(self):
        progress = min(self.timer / 2.0, 1.0)
        self.game_objects.game.screen_manager.set_shader_param(
            'Vignette',
            'vignette_opacity',
            progress
        )
        self.game_objects.world.set_desaturation(progress)

    def _finish(self):
        self.finished = True
        #self.game_objects.player.unlock_input()