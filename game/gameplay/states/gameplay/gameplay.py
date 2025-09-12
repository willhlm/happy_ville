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
        self.game.game_objects.ui.hud.update(dt)
        self.game.game_objects.post_process.update_render(dt)#apply post process shaders to the composite screen, which is large

    def fade_update(self, dt):#called from fade out: update that should be played when fading: it is needed becayse depending on state, only part of the update loop should be called
        self.game.game_objects.update_render(dt)
        #self.game.game_objects.platform_collision(dt)
        self.game.game_objects.ui.hud.update(dt)

    def render(self):
        self.game.game_objects.draw()#rendered on multiple layers on each parallax screen
        self.game.screen_manager.render()#renders each parllax to a composite screen with pp shader, which makes it display size
        #self.game.game_objects.render_state.render()#handles normal and special rendering (e.g. portal rendering)
        self.game.game_objects.lights.draw(self.game.screen_manager.composite_screen)#before post procssing shader?
        self.game.game_objects.post_process.apply(self.game.screen_manager.composite_screen)#apply post process shaders to the composite screen, which is large
        self.game.game_objects.ui.hud.draw(self.game.screen_manager.composite_screen)#renders hud elements to the composite

        self.game.render_display(self.game.screen_manager.composite_screen.texture, scale = False)

    def handle_movement(self):#every frame
        #value = self.game.game_objects.controller.continuous_input_checks()
        value = self.game.game_objects.controller.value
        self.game.game_objects.player.currentstate.handle_movement(value)#move around
        self.game.game_objects.camera_manager.handle_movement(value)

    def handle_events(self, input):
        event = input.output()
        if event[0]:#press
            if event[-1]=='start':#escape button
                input.processed()
                self.game.state_manager.enter_state('Pause_menu', category = 'menu')

            elif event[-1]=='rb':
                input.processed()
                self.game.state_manager.enter_state('Ability_menu')

            elif event[-1] == 'y':
                input.processed()
                self.game.game_objects.collisions.check_interaction_collision()

            elif event[-1] == 'select':
                input.processed()
                self.game.state_manager.enter_state('UIs', page = 'inventory')

            elif event[-1] == 'down':
                input.processed()#should it be processed here or when passed through?
                self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

            elif sum(event[2]['d_pad']) != 0:#d_pad was pressed
                input.processed()
                self.game.game_objects.player.abilities.handle_input(event[2]['d_pad'])#to change movement ability with d pad

            else:
                interpreted = self.game.game_objects.input_interpreter.interpret(input)
                self.game.game_objects.player.currentstate.handle_press_input(interpreted)
                #self.game.game_objects.player.omamoris.handle_press_input(input)
        elif event[1]:#release
            self.game.game_objects.player.currentstate.handle_release_input(input)

        elif event[2]['l_stick'][1] > 0.85:#pressing down
            input.processed()#should it be processed here or when passed through?
            self.game.game_objects.collisions.pass_through(self.game.game_objects.player)

class Ability_menu(Gameplay):#when pressing tab
    def __init__(self, game):
        super().__init__(game)
        self.abilities = list(self.game.game_objects.player.abilities.spirit_abilities.keys())
        self.index = self.abilities.index(self.game.game_objects.player.abilities.equip)

        self.sprites = read_files.load_sprites_list('assets/sprites/ui/ability_hud/', game.game_objects)#TODO
        self.coordinates=[(40,0),(60,50),(30,60),(0,40),(20,0),(0,0)]
        self.surface = self.game.display.make_layer(self.game.window_size)#TODO

    def update(self, dt):
        dt *= 0.5#slow motion
        super().update(dt)

    def render(self):
        super().render()
        self.surface.clear(20,20,20,100)

        hud = self.sprites[self.index]
        for index, ability in enumerate(self.abilities):
            pos = [self.coordinates[index][0] + 250, self.coordinates[index][1] + 100]
            self.game.display.render(self.game.game_objects.player.abilities.spirit_abilities[ability].sprites['active_1'][0], self.surface,position =pos)

        self.game.display.render(hud, self.surface,position = (250,100))
        self.game.render_display(self.surface.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[2]['l_stick'][1] > 0:#dwpn
            self.index += 1
            if self.index > len(self.abilities)-1:
                self.index = 0
        elif event[2]['l_stick'][1] < 0:#up
            self.index-=1
            if self.index<0:
                self.index=len(self.abilities)-1
        elif event [1]:#release
            if event[-1]=='rb':
                self.game.game_objects.player.abilities.equip=self.abilities[self.index]
                self.game.state_manager.exit_state()

class Fadein(Gameplay):
    def __init__(self, game):
        super().__init__(game)
        self.count = 0
        self.fade_length = 25
        self.init()
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)

    def init(self):
        self.aila_state = 'Idle_main'#for respawn after death
        for state in self.game.state_manager.state_stack:
            if 'Death' == type(state).__name__:
                self.aila_state = 'Invisible_main'
                self.game.game_objects.player.currentstate.enter_state('Invisible_main')
                break

    def update_render(self, dt):
        self.fade_update(dt)#so that it doesn't collide with collision path
        self.count += dt
        if self.count > self.fade_length*2:
            self.exit()

    def exit(self):
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.currentstate.enter_state(self.aila_state)
        self.fade_surface.release()
        self.game.state_manager.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.render_display(self.fade_surface.texture)

class Fadeout(Fadein):
    def __init__(self,game, previous_state, map_name, spawn, fade):
        super().__init__(game)
        self.previous_state = previous_state
        self.fade_length = 25
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))
        self.map_name = map_name
        self.spawn = spawn
        self.fade = fade

    def init(self):
        pass

    def update_render(self, dt):
        self.previous_state.fade_update(dt)#so that it don't consider player input
        self.count += dt
        if self.count > self.fade_length:
            self.exit()

    def exit(self):
        self.fade_surface.release()
        self.game.state_manager.exit_state()#has to be before loadmap
        self.game.game_objects.load_map2(self.map_name, self.spawn, self.fade)

    def render(self):
        self.previous_state.render()
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.render_display(self.fade_surface.texture)

class Safe_spawn_1(Gameplay):#basically fade. Uses it when collising a hole
    def __init__(self, game):
        super().__init__(game)
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.count = 0
        self.fade_length = 60
        self.fade_surface.clear(0,0,0,int(255/self.fade_length))

    def update(self, dt):
        super().update(dt)
        self.count += dt
        if self.count > self.fade_length:
            self.game.state_manager.exit_state()
            self.game.state_manager.enter_state('Safe_spawn_2')

    def render(self):
        super().render()#gameplay render
        self.fade_surface.clear(0,0,0,int(self.count*(255/self.fade_length)))
        self.game.render_display(self.fade_surface.texture)

class Safe_spawn_2(Gameplay):#fade
    def __init__(self, game):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.count = 0
        self.fade_length = 20
        self.fade_surface = self.game.display.make_layer(self.game.window_size)#TODO
        self.fade_surface.clear(0,0,0,255)
        self.game.game_objects.player.set_pos(self.game.game_objects.player.backpack.map.spawn_point['safe_spawn'])
        self.game.game_objects.player.currentstate.enter_state('crouch', phase = 'main')

    def update(self, dt):
        super().update(dt)
        self.count += dt
        if self.count > self.fade_length*2:
            self.game.game_objects.player.currentstate.handle_input('pray_post')
            self.game.state_manager.exit_state()

    def render(self):
        super().render()#gameplay render
        alpha = max(int((self.fade_length - self.count)*(255/self.fade_length)),0)
        self.fade_surface.clear(0,0,0,alpha)
        self.game.render_display(self.fade_surface.texture)

class Conversation(Gameplay):
    def __init__(self, game, npc):
        super().__init__(game)
        self.game.game_objects.player.reset_movement()
        self.game.game_objects.player.velocity = [0,0]
        self.npc = npc
        self.print_frame_rate = C.animation_framerate
        self.text_window_size = (352, 96)
        self.blit_pos = [int((self.game.window_size[0]-self.text_window_size[0])*0.5),50]
        self.background = self.game.display.make_layer(self.text_window_size)#TODO
        self.conv_screen = self.game.display.make_layer(self.game.window_size)#TODO

        self.clean_slate()
        self.conv = self.npc.dialogue.get_conversation()
        self.alpha = 10#alpha of the conversation screen
        self.sign = 1#fade in and back

    def clean_slate(self):
        self.letter_frame = 0
        self.text_window = self.game.game_objects.font.fill_text_bg(self.text_window_size)
        self.game.display.render(self.text_window, self.background)#shader render

    def update(self, dt):
        super().update(dt)
        self.letter_frame += self.print_frame_rate*dt
        self.alpha += self.sign * dt * 5
        self.alpha = min(self.alpha,230)
        if self.alpha < 10:
            self.game.state_manager.exit_state()

    def render(self):
        super().render()
        self.conv_screen.clear(10,10,10,100)#needed to make the self.background semi trasnaprant

        text = self.game.game_objects.font.render((272,80), self.conv, int(self.letter_frame))
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,255)
        self.game.display.render(self.background.texture, self.conv_screen, position = self.blit_pos)
        self.game.display.render(text, self.conv_screen, position = (180,self.blit_pos[1] + 20), shader = self.game.game_objects.shaders['colour'])#shader render
        self.npc.render_potrait(self.conv_screen)#some conversation target may not have potraits
        text.release()
        self.game.game_objects.shaders['alpha']['alpha'] = self.alpha

        self.game.display.render(self.conv_screen.texture, self.game.screen_manager.screen, shader = self.game.game_objects.shaders['alpha'])#shader render
        self.game.render_display(self.game.screen_manager.screen.texture)

    def handle_events(self, input):
        event = input.output()
        input.processed()
        if event[0]:
            if event[-1] == 'start':
                self.fade_back()

            elif event[-1] == 'y':
                if self.letter_frame < len(self.conv):
                    self.letter_frame = 10000

                else:#check if we have a series of conversations or not
                    self.npc.dialogue.increase_conv_index()
                    conv = self.npc.dialogue.get_conversation()
                    if not conv:
                        self.fade_back()
                    else:
                        self.clean_slate()
                        self.conv = conv

    def fade_back(self):
        self.sign = -1

    def on_exit(self):
        self.conv_screen.release()
        self.background.release()
        self.npc.buisness()

class UIs(Gameplay):#pressing i: map, inventory, omamori, journal
    def __init__(self, game, page, **kwarg):
        super().__init__(game)
        self.game.game_objects.ui.set_ui(page, **kwarg)

    def update(self, dt):
        super().update(dt)
        self.game.game_objects.ui.update(dt)

    def render(self):
        super().render()
        self.game.game_objects.ui.render()

    def handle_events(self,input):
        self.game.game_objects.ui.handle_events(input)

class Blit_image_text(Gameplay):#when player obtaines a new ability, pick up inetractable item etc. It blits an image and text
    def __init__(self, game, image, text = '', callback = None):
        super().__init__(game)
        self.page = 0
        self.render_fade = [self.render_in, self.render_out]

        self.image = game.display.make_layer(image.size)#TODO
        self.game.display.render(image, self.image)#make a copy of the image
        self.text = self.game.game_objects.font.render((140,80), text)

        self.game.game_objects.player.reset_movement()

        self.fade = [0,0]
        self.callback = callback#a function to call when exiting

    def handle_movement(self):#every frame
        pass

    def render(self):
        super().render()
        self.render_fade[self.page]()

        self.game.game_objects.shaders['alpha']['alpha'] = self.fade[1]
        self.game.game_objects.shaders['colour']['colour'] = (255,255,255,self.fade[1])

        self.game.screen_manager.screen.clear(40, 40, 40, self.fade[0])

        self.game.display.render(self.image.texture, self.game.screen_manager.screen, position = (320, 120), shader = self.game.game_objects.shaders['alpha'])
        self.game.display.render(self.text, self.game.screen_manager.screen, position = (320,140), shader = self.game.game_objects.shaders['colour'])
        self.game.render_display(self.game.screen_manager.screen.texture)

    def render_in(self):
        self.fade[0] += 1
        self.fade[1] += 1
        self.fade[0] = min(self.fade[0],150)
        self.fade[1] = min(self.fade[1],255)

    def render_out(self):
        self.fade[0] -= 1
        self.fade[1] -= 1
        self.fade[0] = max(self.fade[0], 0)
        self.fade[1] = max(self.fade[1], 0)

        if self.fade[0] == 0:
            if self.callback: self.callback()
            self.game.state_manager.exit_state()

    def handle_events(self,input):
        event = input.output()
        input.processed()
        if event[0]:#press
            if event[-1] == 'start':
                self.page = 1
            elif event[-1] == 'a':
                self.page = 1
