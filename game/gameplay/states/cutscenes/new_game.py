from engine.utils import read_files
from gameplay.states.base.game_state import GameState

class NewGame(GameState):
    def __init__(self, game):
        self.game = game
        self.sprites = read_files.load_sprites_list('assets/cutscene/new_game', game.game_objects)
        self.size = game.window_size.copy()
        self.noise_layer = game.game_objects.game.display.make_layer(self.size)
        self.empty = game.game_objects.game.display.make_layer(self.size)

        self.frame = 0     
        self.time = 0        
        self.texts = ['Before frost found the earth, there was only song. The world was a great dream, breathed by those who walked among the stars. They shaped rivers from whispers, and lit the sky with memory.', 
        'In that land, no one wept. The dream and the living were one, and every heart was clear as glass. But even the purest light gathers shadow when it burns too long.', 
        'The shadow took root in one child. Her laughter stilled, and her eyes saw through the world into what should not be seen. The dream bent around her, and the ground beneath her feet began to weep.',
        'To keep her from breaking, they laid her beneath the roots of the Dreamtree. They sang her to sleep with names forgotten to all but wind and stone. The earth closed, and silence took her place.',
        'Seasons drifted into ages. The dream thinned. The songs faded. Yet the roots still breathe, and the whisper beneath them grows restless once more.',
        '"Mama", the child asks, "what if she wakes"? The mother smiles, though her eyes do not. "Then, little one… someone must remember how to dream again."']       

    def update_render(self,dt):
        self.time += dt

    def render(self):
        #noise
        self.game.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.001
        self.game.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.game.game_objects.shaders['noise_perlin']['scale'] = [1,1]
        self.game.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game.game_objects.shaders['squigglevision']['noiseTexture'] = self.noise_layer.texture
        self.game.game_objects.shaders['squigglevision']['time'] = self.time * 0
        self.game.display.render(self.sprites[self.frame], self.empty, shader = self.game.game_objects.shaders['squigglevision']) 

        self.game.game_objects.shaders['shimmer']['noiseTexture'] = self.noise_layer.texture
        self.game.game_objects.shaders['shimmer']['time'] = self.time * 0.5 
        self.game.display.render(self.empty.texture, self.game.screen_manager.screen, shader = self.game.game_objects.shaders['shimmer']) 

        self.render_text()
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:
          if event[-1] == 'a':
                self.frame += 1
                self.time = 0                
                if self.frame == len(self.sprites) :#if no more pages                                          
                    self.game.state_manager.exit_state()
                self.frame = min(self.frame, len(self.sprites) -1)

    def on_exit(self):
        self.game.state_manager.enter_state('gameplay')
        self.game.game_objects.map.load_map(self, 'rhoutta_encounter_1', spawn = '1', fade = False)                                        

    def render_text(self):        
        width = 300
        position = [self.game.window_size[0] * 0.5 - width * 0.5, self.game.window_size[1] * 0.75]
        self.game.display.render_text(self.game.game_objects.font.font_atals, self.game.screen_manager.screen, text = self.texts[self.frame], letter_frame = int(self.time), color = (255,255,255,255), width = width, position = position)


    def fade_update(self, dt):
        pass