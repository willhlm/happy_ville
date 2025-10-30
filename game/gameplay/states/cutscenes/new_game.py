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
        self.texts = ['Before frost found the earth, there was only song. The world was a great dream, breathed by those who walked among the stars. They shaped rivers from whispers, and lit the sky with memory.', 'In that land, no one wept.The dream and the living were one, and every heart was clear as glass.But even the purest light gathers shadow when it burns too long.', 'The shadow took root in one child.Her laughter stilled, and her eyes saw through the world — into what should not be seen.The dream bent around her, and the ground beneath her feet began to weep.']       

    def update_render(self,dt):
        self.time += dt

    def render(self):
        #noise
        self.game.game_objects.shaders['noise_perlin']['u_resolution'] = self.size
        self.game.game_objects.shaders['noise_perlin']['u_time'] = self.time*0.001
        self.game.game_objects.shaders['noise_perlin']['scroll'] = [0,0]
        self.game.game_objects.shaders['noise_perlin']['scale'] = [70,20]
        self.game.game_objects.game.display.render(self.empty.texture, self.noise_layer, shader=self.game.game_objects.shaders['noise_perlin'])#make perlin noise texture

        self.game.game_objects.shaders['squigglevision']['noiseTexture'] = self.noise_layer.texture
        self.game.game_objects.shaders['squigglevision']['time'] = self.time
        self.game.display.render(self.sprites[self.frame], self.game.screen_manager.screen, shader = self.game.game_objects.shaders['squigglevision']) 
        self.render_text()
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self,input):
        event = input.output()
        input.processed()

        if event[0]:
          if event[-1] == 'a':
                self.frame+= 1
                self.time = 0
                self.frame = min(self.frame, len(self.sprites) )
                if self.frame == len(self.sprites) :                                          
                    self.game.state_manager.exit_state()

    def on_exit(self):
        self.game.state_manager.enter_state('gameplay')
        self.game.game_objects.load_map(self.game.state_manager.state_stack[-1], 'rhoutta_encounter_1', spawn = '1', fade = False)                                        


    def render_text(self):        
        self.game.display.render_text(self.game.game_objects.font.font_atals, self.game.screen_manager.screen, text = self.texts[self.frame], letter_frame = int(self.time), color = (255,255,255,255), width = 300, position = (30,60))


