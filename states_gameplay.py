class Basic_states():#the rendering protocol changes if there is portal. This handles that
    def __init__(self, game_objects):
        self.game_objects = game_objects

    def render(self):
        pass

class Idle(Basic_states):
    def __init__(self, game_objects):
        super().__init__(game_objects)

    def render(self):
        self.game_objects.draw()

    def handle_input(self, input, **kwarg):
        if input == 'portal':
            self.game_objects.render_state = Portal(self.game_objects, kwarg['portal'])

class Portal(Basic_states):
    def __init__(self, game_objects, portal):
        super().__init__(game_objects)
        self.portal = portal

    def render(self):
        self.portal.empty_layer.clear(0,0,0,0)
        self.portal.bg_grey_layer.clear(0,0,0,0)

        self.game_objects.all_bgs.draw(self.portal.bg_distort_layer)
        self.game_objects.interactables.draw(self.portal.bg_distort_layer)#should be before bg_interact
        self.game_objects.bg_interact.draw(self.portal.bg_distort_layer)
        #we want the stuff above to be distored and grey 
        
        self.game_objects.enemies.draw(self.portal.bg_grey_layer)
        self.game_objects.npcs.draw(self.portal.bg_grey_layer)
        self.game_objects.fprojectiles.draw(self.portal.bg_grey_layer)
        self.game_objects.eprojectiles.draw(self.portal.bg_grey_layer)
        self.game_objects.loot.draw(self.portal.bg_grey_layer)
        self.game_objects.platforms.draw(self.portal.bg_grey_layer)
        self.game_objects.players.draw(self.portal.bg_grey_layer)
        self.game_objects.cosmetics.draw(self.portal.bg_grey_layer)#Should be before fgs
        #we want this one to be spirit colourm no distotion

        self.game_objects.special_shaders.draw(None)#portal inside will draws the layers properly onto the screen

        self.game_objects.all_fgs.draw(self.game_objects.game.screen)
        self.game_objects.lights.draw(self.game_objects.game.screen)#should be second to last
        self.game_objects.shader_render.draw(self.game_objects.game.screen)#housld be last        

    def handle_input(self, input, **kwarg):
        if input == 'idle':
            self.game_objects.render_state = Idle(self.game_objects)