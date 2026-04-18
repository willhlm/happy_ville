import pygame, sys
from engine.utils import read_files
from engine import constants as C
from gameplay.states.base.game_state import GameState

class Gameplay(GameState):
    def __init__(self, game):
        super().__init__(game)

    def update(self, dt):
        self.game.game_objects.time_manager.update(dt)#setäs the timescale
        dt *= self.game.game_objects.time_manager.time_scale#apply time scale
        self.handle_movement()
        self.game.game_objects.update(dt)

    def update_render(self, dt):
        dt *= self.game.game_objects.time_manager.time_scale#apply time scale
        self.game.game_objects.update_render(dt)
        self.game.game_objects.world_transform_controller.update_render(dt)
        self.game.game_objects.ui.hud.update(dt)
        self.game.game_objects.post_process.update_render(dt)#apply post process shaders to the composite screen, which is large

    def fade_update(self, dt):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.game.game_objects.update_render(dt)
        #self.game.game_objects.platform_collision(dt)
        self.game.game_objects.ui.hud.update(dt)

    def render(self):
        self.game.game_objects.draw()#rendered on multiple layers on each parallax screen
        self.game.screen_manager.render()#renders each parllax to a composite screen with pp shader, which makes it display size
        self.game.game_objects.lights.draw(self.game.screen_manager.composite_screen)#before post procssing shader?
        self.game.game_objects.post_process.apply(self.game.screen_manager.composite_screen)#apply post process shaders to the composite screen, which is large
        self.game.game_objects.ui.hud.draw(self.game.screen_manager.composite_screen)#renders hud elements to the composite

        self.game.render_display(self.game.screen_manager.composite_screen.texture, scale = False)

    def handle_movement(self):#every frame
        axes = self.game.game_objects.controller.frame.axes
        self.game.game_objects.player.currentstate.handle_movement(axes)#move around
        self.game.game_objects.camera_manager.handle_movement(axes)

    def handle_events(self, input):
        if input.pressed:#press
            if input.name == 'start':#escape button
                input.processed()                
                self.game.state_manager.enter_state('pause_menu')

            elif input.name == 'rb':
                input.processed()
                self.game.state_manager.enter_state('ability_select')

            elif input.name == 'y':
                input.processed()
                self.game.game_objects.collisions.check_interaction_collision()

            elif input.name == 'select':
                input.processed()
                self.game.state_manager.enter_state('uis', page = 'inventory')

            elif input.name == 'down':
                input.processed()#should it be processed here or when passed through?
                self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

            elif input.name in ('up', 'left', 'right'):#directional UI-style actions are ignored in gameplay
                input.processed()
                pass

            else:
                interpreted = self.game.game_objects.input_interpreter.interpret(input)
                self.game.game_objects.player.currentstate.handle_press_input(interpreted)
                #self.game.game_objects.player.omamoris.handle_press_input(input)
        elif input.released:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)
