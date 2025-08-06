import pygame
import read_files
import collisions
import entities
import map_loader
import sound
import camera
import weather
import constants as C
import world_state
import UI
import save_load
import groups
import object_pool
import controller
import lights
import shader_render
from states import states_gameplay#handles the rendering protocols: better suited in game_play state perhaos. But need to be here because the nheritance of states wouild break
import quests_events
import timer
import signals
import time_manager
import alphabet
import input_interpreter


from time import perf_counter

class Game_Objects():
    def __init__(self, game):
        self.game = game
        self.font = alphabet.Alphabet(self)#intitilise the alphabet class, scale of alphabet
        self.shaders = read_files.load_shaders_dict(self)#load all shaders aavilable into a dict
        self.controller = controller.Controller()
        self.object_pool = object_pool.Object_pool(self)
        self.sound = sound.Sound()
        self.lights = lights.Lights(self)
        self.timer_manager = timer.Timer_manager(self)
        self.create_groups()
        self.weather = weather.Weather(self)
        self.collisions = collisions.Collisions(self)
        self.map = map_loader.Level(self)
        self.camera_manager = camera.Camera_manager(self)
        self.world_state = world_state.World_state(self)#save/handle all world state stuff here
        self.UI = UI.UI_manager(self)        
        self.save_load = save_load.Save_load(self)#contains save and load attributes to load and save game
        self.shader_render = shader_render.Screen_shader(self, 'vignette')     
        self.render_state = states_gameplay.Idle(self)
        self.quests_events = quests_events.Quests_events(self)        
        self.signals = signals.Signals()
        self.input_interpreter = input_interpreter.InputInterpreter(self)
        self.time_manager = time_manager.Time_manager(self)

    def create_groups(self):#define all sprite groups
        self.enemies = groups.Group()#enemies
        self.npcs = groups.Group()#npcs
        self.platforms = groups.Group()#platforms
        self.special_shaders = groups.Group()#portal use it for the drawing: draw not called normally but in different gameplay state
        self.platforms_ramps = groups.Group()#ramps
        self.all_bgs = groups.LayeredGroup()#[]
        self.all_fgs = groups.LayeredGroup()#[]
        self.bg_interact = groups.Group()#small grass stuff so that interactables blends with BG
        self.bg_fade = groups.Group()#fg stuff that should dissapear when player comes: this should not blit or update. it will just run collision checks
        self.eprojectiles = groups.Group()#enemy projectiles
        self.fprojectiles = groups.Group()#player prohectiles
        self.loot = groups.Group()#enemy drops and things player cn pickup upon collision
        self.entity_pause = groups.PauseGroup() #all Entities that are far away
        self.cosmetics = groups.Group()#things we just want to blit after the player layer
        self.cosmetics2 = groups.Group()#things we just want to blit before player layer
        self.interactables_fg = groups.Group()#interacrables but are blitted after the player layer
        self.cosmetics_no_clear = groups.Group()# a group that will not be cleared when changing map

        self.camera_blocks = groups.Group()#camera blocks
        self.interactables = groups.Group()#player collisions, when pressing T/Y and projectile collisions: chest, bushes, collision path, sign post, save point
        self.layer_pause = groups.PauseLayer()#like eneitty pause but for those at different parallax layers

        #initiate player
        self.player = entities.Player([0,0],self)
        self.players = groups.Group()#blits on float positions
        self.players.add(self.player)

    def load_map(self, previous_state, map_name, spawn = '1', fade = True):#called from path_col
        if fade:#for cutscenes
            kwarg = {'previous_state': previous_state, 'map_name': map_name,'spawn':spawn, 'fade': fade }
            self.game.state_manager.enter_state('Fadeout', **kwarg)
        else:
            self.load_map2(map_name, spawn, fade)

    def load_map2(self, map_name, spawn = '1', fade = True):#called from fadeout or load_map above
        self.clean_groups()
        t1_start = perf_counter()  
        self.map.load_map(map_name, spawn)#memory leak somwehre here
        t1_stop = perf_counter()
        print(t1_stop-t1_start)

        if fade:#for cutscenes
            self.game.state_manager.enter_state('Fadein')        

    def clean_groups(self):#called wgen changing map
        self.npcs.empty()
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()
        self.loot.empty()
        self.platforms_ramps.empty()
        self.entity_pause.empty()  
        self.all_bgs.empty()
        self.all_fgs.empty()
        self.camera_blocks.empty()
        self.bg_interact.empty()
        self.cosmetics.empty()
        self.cosmetics2.empty()
        self.layer_pause.empty()
        self.bg_fade.empty()
        self.special_shaders.empty()
        self.eprojectiles.empty()
        self.interactables_fg.empty()
        self.fprojectiles.empty()
        self.timer_manager.clear_timers()
        self.weather.empty()

    def collide_all(self, dt):        
        self.platform_collision(dt)

        self.collisions.player_collision(self.loot)
        self.collisions.player_collision(self.enemies)
        self.collisions.player_collision(self.bg_fade)
        self.collisions.interactables_collision(self.npcs)
        self.collisions.interactables_collision(self.players)#need to know when it doesn't collide

        self.collisions.counter(self.fprojectiles, self.eprojectiles)
        self.collisions.projectile_collision(self.fprojectiles, self.enemies)
        self.collisions.projectile_collision(self.eprojectiles, self.players)

    def platform_collision(self, dt):        
        self.collisions.platform_collision(self.players, dt)        
        self.collisions.platform_collision(self.enemies, dt)
        self.collisions.platform_collision(self.eprojectiles, dt)
        self.collisions.platform_collision(self.fprojectiles, dt)
        self.collisions.platform_collision(self.npcs, dt)
        self.collisions.platform_collision(self.loot, dt)

    def update(self, dt):#called before update_render
        self.camera_blocks.update_render(dt)#need to be before camera: caemras stop needs tobe calculated before the scroll        
        self.camera_manager.update(dt)#should be first        
        self.timer_manager.update(dt)
        self.platforms.update(dt)        
        self.platforms_ramps.update(dt)
        self.layer_pause.update(dt)#should be before all_bgs and all_fgs
        self.all_bgs.update(dt)
        self.bg_interact.update(dt)
        self.all_fgs.update(dt)
        self.players.update(dt)        
        self.entity_pause.update(dt)#should be before enemies, npcs and interactable groups
        self.enemies.update(dt)
        self.npcs.update(dt)
        self.fprojectiles.update(dt)
        self.eprojectiles.update(dt)
        self.loot.update(dt)
        self.interactables.update(dt)
        self.weather.update(dt)
        self.interactables_fg.update(dt)#twoD water use it

    def update_render(self, dt):#called after update_physics
        #self.camera_blocks.update_render(dt)#need to be before camera: caemras stop needs to be calculated before the scroll        
        self.camera_manager.update_render(dt)#should be first     
        self.platforms.update_render(dt)        
        self.platforms_ramps.update_render(dt)
        self.all_bgs.update_render(dt)
        self.bg_interact.update_render(dt)
        self.all_fgs.update_render(dt)
        self.players.update_render(dt)
        self.enemies.update_render(dt)
        self.npcs.update_render(dt)
        self.fprojectiles.update_render(dt)
        self.eprojectiles.update_render(dt)
        self.loot.update_render(dt)
        self.cosmetics.update_render(dt)
        self.cosmetics_no_clear.update_render(dt)
        self.cosmetics2.update_render(dt)
        self.interactables.update_render(dt)
        self.interactables_fg.update_render(dt)#twoD water use it
        self.special_shaders.update_render(dt)#portal use it
        self.lights.update_render(dt)
        self.shader_render.update_render(dt)#housld be last

    def draw(self):#called from render states
        self.lights.clear_normal_map()        
        layer = self.all_bgs.draw(self.game.screen_manager.screens)#returns the last layer      
        player_layer_screen = self.game.screen_manager.screens[layer].layer
        self.interactables.draw(player_layer_screen)#should be before bg_interact
        self.bg_interact.draw(player_layer_screen)
        self.cosmetics2.draw(player_layer_screen)#Should be before enteties
        
        self.enemies.draw(player_layer_screen)
        self.npcs.draw(player_layer_screen)
        self.loot.draw(player_layer_screen)
        self.players.draw(player_layer_screen)
                
        self.platforms.draw(player_layer_screen)
        self.fprojectiles.draw(player_layer_screen)
        self.eprojectiles.draw(player_layer_screen)        
        
        self.interactables_fg.draw(player_layer_screen)#shoud be after player
        self.cosmetics.draw(player_layer_screen)#Should be before fgs
        self.cosmetics_no_clear.draw(player_layer_screen)#Should be before fgs
        
        layer = self.all_fgs.draw(self.game.screen_manager.screens)#returns the last layer              
        #self.camera_blocks.draw()
        self.lights.draw(self.game.screen_manager.screens[layer].layer)#should be second to last
        self.shader_render.draw(self.game.screen_manager.screens[layer].layer)#housld be last: screen shader
        
        #temporaries draws. Shuold be removed
        if self.game.RENDER_HITBOX_FLAG:
            image = pygame.Surface(self.game.window_size,pygame.SRCALPHA,32).convert_alpha()

            pygame.draw.rect(image, (255,0,255), (round(self.player.hitbox[0]-self.camera_manager.camera.true_scroll[0]),round(self.player.hitbox[1]-self.camera_manager.camera.true_scroll[1]),self.player.hitbox[2],self.player.hitbox[3]),2)#draw hitbox
            pygame.draw.rect(image, (0,0,255), (round(self.player.rect[0]-self.camera_manager.camera.true_scroll[0]),round(self.player.rect[1]-self.camera_manager.camera.true_scroll[1]),self.player.rect[2],self.player.rect[3]),2)#draw hitbox

            for projectile in self.fprojectiles.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(projectile.hitbox[0]-self.camera_manager.camera.scroll[0]),int(projectile.hitbox[1]-self.camera_manager.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for projectile in self.eprojectiles.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(projectile.hitbox[0]-self.camera_manager.camera.scroll[0]),int(projectile.hitbox[1]-self.camera_manager.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for enemy in self.enemies.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), [enemy.hitbox[0]-self.camera_manager.camera.scroll[0],enemy.hitbox[1]-self.camera_manager.camera.scroll[1],enemy.hitbox[2],enemy.hitbox[3]],2)#draw hitbox
                pygame.draw.rect(image, (255,0,255), [enemy.rect[0]-self.camera_manager.camera.scroll[0],enemy.rect[1]-self.camera_manager.camera.scroll[1],enemy.rect[2],enemy.rect[3]],2)#draw hitbox
            for enemy in self.npcs.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), [enemy.hitbox[0]-self.camera_manager.camera.scroll[0],enemy.hitbox[1]-self.camera_manager.camera.scroll[1],enemy.hitbox[2],enemy.hitbox[3]],2)#draw hitbox
                pygame.draw.rect(image, (255,0,255), [enemy.rect[0]-self.camera_manager.camera.scroll[0],enemy.rect[1]-self.camera_manager.camera.scroll[1],enemy.rect[2],enemy.rect[3]],2)#draw hitbox
            for cos in self.interactables.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(cos.hitbox[0]-self.camera_manager.camera.scroll[0]),int(cos.hitbox[1]-self.camera_manager.camera.scroll[1]),cos.hitbox[2],cos.hitbox[3]),1)#draw hitbox
                pygame.draw.rect(image, (255,0,255), (int(cos.rect[0]-self.camera_manager.camera.scroll[0]),int(cos.rect[1]-self.camera_manager.camera.scroll[1]),cos.rect[2],cos.rect[3]),1)#draw hitbox
            for cos in self.loot.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(cos.hitbox[0]-self.camera_manager.camera.scroll[0]),int(cos.hitbox[1]-self.camera_manager.camera.scroll[1]),cos.hitbox[2],cos.hitbox[3]),1)#draw hitbox
                pygame.draw.rect(image, (255,0,255), (int(cos.rect[0]-self.camera_manager.camera.scroll[0]),int(cos.rect[1]-self.camera_manager.camera.scroll[1]),cos.rect[2],cos.rect[3]),1)#draw hitbox
            for platform in self.platforms:#go through the group
                if type(platform).__name__ == 'Collision_oneway_up':
                    pygame.draw.rect(image, (255,0,255), (int(platform.hitbox[0]-self.camera_manager.camera.scroll[0]),int(platform.hitbox[1]-self.camera_manager.camera.scroll[1]),platform.hitbox[2],platform.hitbox[3]),1)#draw hitbox
                else:
                    pygame.draw.rect(image, (255,0,0), (int(platform.hitbox[0]-self.camera_manager.camera.scroll[0]),int(platform.hitbox[1]-self.camera_manager.camera.scroll[1]),platform.hitbox[2],platform.hitbox[3]),1)#draw hitbox
            for ramp in self.platforms_ramps:
                pygame.draw.rect(image, (0,0,0), (int(ramp.hitbox[0]-self.camera_manager.camera.scroll[0]),int(ramp.hitbox[1]-self.camera_manager.camera.scroll[1]),ramp.hitbox[2],ramp.hitbox[3]),1)#draw hitbox
            for fade in self.bg_fade:
                pygame.draw.rect(image, (255,100,100), (int(fade.hitbox[0]-fade.parallax[0]*self.camera_manager.camera.scroll[0]),int(fade.hitbox[1]-fade.parallax[1]*self.camera_manager.camera.scroll[1]),fade.hitbox[2],fade.hitbox[3]),1)#draw hitbox
            for light in self.lights.lights_sources:
                pygame.draw.rect(image, (255,100,100), (int(light.hitbox[0]-light.parallax[0]*self.camera_manager.camera.scroll[0]),int(light.hitbox[1]-light.parallax[1]*self.camera_manager.camera.scroll[1]),light.hitbox[2],light.hitbox[3]),1)#draw hitbox
            #for reflect in self.reflections:
            #    pygame.draw.rect(image, (255,100,100), (int(reflect.reflect_rect[0]),int(reflect.reflect_rect[1]),reflect.reflect_rect[2],reflect.reflect_rect[3]),1)#draw hitbox
            #    pygame.draw.rect(image, (255,100,100), (int(reflect.rect[0]-self.camera.scroll[0]),int(reflect.rect[1]-self.camera.scroll[1]),reflect.rect[2],reflect.rect[3]),1)#draw hitbox
            for group in self.all_bgs.group_dict.values():
                for obj in group:
                    if type(obj).__name__ == 'Reflection':
                        pygame.draw.rect(image, (0,0,255), (int(reflect.reflect_rect[0]),int(reflect.reflect_rect[1]),reflect.reflect_rect[2],reflect.reflect_rect[3]),1)#draw hitbox
                        pygame.draw.rect(image, (255,0,0), (int(reflect.rect[0]-reflect.parallax[0]*self.camera_manager.camera.scroll[0]),int(reflect.rect[1]-reflect.parallax[1]*self.camera_manager.camera.scroll[1]),reflect.rect[2],reflect.rect[3]),1)#draw hitbox

            for reflect in self.cosmetics:
                if type(reflect).__name__ == 'Reflection':
                    pygame.draw.rect(image, (0,0,255), (int(reflect.reflect_rect[0]),int(reflect.reflect_rect[1]),reflect.reflect_rect[2],reflect.reflect_rect[3]),1)#draw hitbox
                    pygame.draw.rect(image, (255,0,0), (int(reflect.rect[0]-reflect.parallax[0]*self.camera_manager.camera.scroll[0]),int(reflect.rect[1]-reflect.parallax[1]*self.camera_manager.camera.scroll[1]),reflect.rect[2],reflect.rect[3]),1)#draw hitbox

            tex = self.game.display.surface_to_texture(image)
            self.game.display.render(tex, player_layer_screen)#shader render
            tex.release()
