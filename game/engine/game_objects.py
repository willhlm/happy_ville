import pygame
from engine.utils import read_files
from engine.system import activation_manager, time_field_manager, save_load, object_pool, controller, lights, timer, signals, time_manager, alphabet, input_interpreter, transition_controller, sequence_manager
from engine import groups
from engine.sound import game_audio
from gameplay.entities.player import player
from engine.render import post_process
from engine.render.normal_map_generator import NormalMapGenerator
from engine.camera import camera
from engine.physics import PhysicsManager

from gameplay.world import world_state
from gameplay.world.map.map_coordinator import MapCoordinator
from gameplay.world.weather import weather
from engine import constants as C
from gameplay.ui.managers import ui
from gameplay.narrative.quests_events.manager import QuestsEventsManager

from gameplay.registry.registry_manager import RegistryManager
from engine.particles.particle_system import ParticleSystem

from gameplay.world.transforms.world_transform_controller import WorldTransformController

class GameObjects():
    def __init__(self, game):
        self.game = game
        self.font = alphabet.Alphabet(self)#intitilise the alphabet class, scale of alphabet          
        self.signals = signals.Signals()        
        self.shaders = read_files.load_shaders_dict(self)#load all shaders aavilable into a dict
        self.normal_map_generator = NormalMapGenerator(self)
        self.controller = controller.Controller()
        self.object_pool = object_pool.Object_pool(self)
        self.lights = lights.Lights(self)
        self.timer_manager = timer.Timer_manager(self)
        self._create_groups()
        self.activation_manager = activation_manager.ActivationManager(self)
        self.weather = weather.Weather(self)
        self.physics = PhysicsManager(self)
        
        self.transition = transition_controller.TransitionController(self)
        self.sequence_manager = sequence_manager.SequenceManager(self)
        self.map = MapCoordinator(self) 
        self.camera_manager = camera.Camera_manager(self)
        self.sound = game_audio.GameAudio(camera_scroll_getter=lambda: self.camera_manager.camera.true_scroll)
        self.world_state = world_state.World_state(self)#save/handle all world state stuff here
        self.ui = ui.UiManager(self)
        self.save_load = save_load.Save_load(self)#contains save and load attributes to load and save game
        self.quests_events = QuestsEventsManager(self)        
        self.input_interpreter = input_interpreter.InputInterpreter(self)
        self.time_manager = time_manager.Time_manager(self)
        self.post_process = post_process.CompositePipeline(self)
        self.registry = RegistryManager()
        self.particles = ParticleSystem(self)
        self.world_transform_controller = WorldTransformController(self)
        self.time_field_manager = time_field_manager.TimeFieldManager()

    def _create_groups(self):#define all sprite groups
        self.enemies = groups.Group()#enemies
        self.npcs = groups.Group()#npcs
        self.platforms = groups.Group()#platforms, including ramps
        self.all_bgs = groups.LayeredGroup()#[]
        self.all_fgs = groups.LayeredGroup()#[]
        self.bg_interact = groups.Group()#small grass stuff so that interactables blends with BG
        self.bg_fade = groups.Group()#fg stuff that should dissapear when player comes: this should not blit or update. it will just run collision checks
        self.projectiles = groups.ProjectileGroups()
        self.loot = groups.Group()#enemy drops and things player cn pickup upon collision
        self.entity_pause = groups.PauseGroup() #all Entities that are far away
        self.cosmetics = groups.Group()#things we just want to blit after the player layer
        self.cosmetics_bg = groups.Group()#things we just want to blit before player layer
        self.interactables_fg = groups.Group()#interacrables but are blitted after the player layer

        self.camera_blocks = groups.Group()#camera blocks
        self.interactables = groups.Group()#player collisions, when pressing T/Y and projectile collisions: chest, bushes, collision path, sign post, save point
        self.layer_pause = groups.PauseLayer()#like eneitty pause but for those at different parallax layers

        #initiate player
        self.player = player.Player([0,0], self)
        self.players = groups.Group()
        self.players.add(self.player)

    def clean_groups(self):#called wgen changing map
        self.npcs.empty()
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()
        self.loot.empty()
        self.entity_pause.empty()
        self.all_bgs.empty()
        self.all_fgs.empty()
        self.camera_blocks.empty()
        self.bg_interact.empty()
        self.cosmetics.empty()
        self.cosmetics_bg.empty()
        self.layer_pause.empty()
        self.bg_fade.empty()
        self.projectiles.empty()
        self.interactables_fg.empty()
        self.timer_manager.clear_timers()
        self.weather.empty()
        self.physics.clear_state()

    def clear_world_state(self):#called when poping gameplay state
        self.sound.fade_all_music()
        self.sound.clear_spatial_sounds()
        self.clean_groups()
        self.map.reset()

    def collide_all(self, dt):
        self.physics.dispatch_overlaps(dt)

    def update(self, dt):        
        self.platforms.update(dt)
        self.physics.rebuild_platform_index()

        # Update camera-derived regions before waking entities. Platform collision
        # queries use the spatial index directly, so the index must be rebuilt
        # before entities simulate for the frame.
        self.activation_manager.update()
        self.entity_pause.update(dt)#should be before enemies, npcs and interactable groups
        self.physics.simulate_group(self.players, dt)
        self.physics.simulate_group(self.enemies, dt)
        self.physics.simulate_group(self.npcs, dt)

        self.projectiles.friendly.update(dt)
        self.projectiles.enemy.update(dt)
        self.physics.simulate_group(self.projectiles.enemy_platform, dt)
        self.physics.simulate_group(self.projectiles.friendly_platform, dt)
        self.physics.simulate_group(self.loot, dt)

        #check non-platform collisions after motion has been resolved
        self.collide_all(dt)

        #camera and calculate true pos
        self.camera_manager.update(dt)#should be first

        #update cosmetics and BGs
        self.timer_manager.update(dt)
        self.layer_pause.update(dt)#should be before all_bgs and all_fgs
        self.all_bgs.update(dt)
        self.bg_interact.update(dt)
        self.all_fgs.update(dt)
        self.cosmetics.update(dt)
        self.cosmetics_bg.update(dt)
        self.interactables.update(dt)
        self.weather.update(dt)
        self.interactables_fg.update(dt)#twoD water use it
        self.sequence_manager.update(dt)

    def update_render(self, dt):#called after update_physics
        #self.camera_blocks.update(dt)#need to be before camera: caemras stop needs to be calculated before the scroll
        self.camera_manager.update_render(dt)#should be first
        self.lights.update_render(dt)

        self.platforms.update_render(dt)
        self.all_bgs.update_render(dt)
        self.bg_interact.update_render(dt)
        self.all_fgs.update_render(dt)
        self.sound.update_render(self.player.hitbox.center)#for emitters and tracking distance for sound
        self.players.update_render(dt)
        self.enemies.update_render(dt)
        self.npcs.update_render(dt)
        self.projectiles.update_render(dt)
        self.loot.update_render(dt)
        self.cosmetics.update_render(dt)
        self.cosmetics_bg.update_render(dt)
        self.interactables.update_render(dt)
        self.interactables_fg.update_render(dt)#twoD water use it
        self.sequence_manager.update_render(dt)

    def draw(self):#called from render states         
        self.lights.clear_normal_map()

        self.all_bgs.draw(self.game.screen_manager.screens)

        #bg1:
        layer = self.all_bgs.get_topmost_screen()#returns the last layer
        last_bg_screen = self.game.screen_manager.screens[layer].layer

        self.platforms.draw(last_bg_screen)

        self.interactables.draw(last_bg_screen)#should be before bg_interact

        self.bg_interact.draw(last_bg_screen)#small grass stuff so that interactables blends with BG

        self.cosmetics_bg.draw(last_bg_screen)#Should be before enteties

        self.enemies.draw(last_bg_screen)

        self.npcs.draw(last_bg_screen)        

        self.players.draw(self.game.screen_manager.screens['player'].layer)

        #after the player but bg1:
        player_fg_screen = self.game.screen_manager.screens['player_fg'].layer

        self.loot.draw(player_fg_screen)

        self.projectiles.draw(player_fg_screen)

        self.interactables_fg.draw(player_fg_screen)#shoud be after the player -> upstream, 2D water

        self.cosmetics.draw(player_fg_screen)

        self._draw_hitboxes(player_fg_screen)           

        #fgs
        self.all_fgs.draw(self.game.screen_manager.screens)
        #self.camera_blocks.draw()

    def _draw_hitboxes(self, target):
        #temporaries draws. Shuold be removed
        if self.game.RENDER_HITBOX_FLAG:
            image = pygame.Surface(self.game.window_size,pygame.SRCALPHA,32).convert_alpha()

            pygame.draw.rect(image, (255,0,255), (round(self.player.hitbox[0]-self.camera_manager.camera.true_scroll[0]),round(self.player.hitbox[1]-self.camera_manager.camera.true_scroll[1]),self.player.hitbox[2],self.player.hitbox[3]),2)#draw hitbox
            pygame.draw.rect(image, (0,0,255), (round(self.player.rect[0]-self.camera_manager.camera.true_scroll[0]),round(self.player.rect[1]-self.camera_manager.camera.true_scroll[1]),self.player.rect[2],self.player.rect[3]),2)#draw hitbox

            for projectile in self.projectiles.friendly.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(projectile.hitbox[0]-self.camera_manager.camera.scroll[0]),int(projectile.hitbox[1]-self.camera_manager.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for projectile in self.projectiles.friendly_platform.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(projectile.hitbox[0]-self.camera_manager.camera.scroll[0]),int(projectile.hitbox[1]-self.camera_manager.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for projectile in self.projectiles.enemy.sprites():#go through the group
                pygame.draw.rect(image, (0,0,255), (int(projectile.hitbox[0]-self.camera_manager.camera.scroll[0]),int(projectile.hitbox[1]-self.camera_manager.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for projectile in self.projectiles.enemy_platform.sprites():#go through the group
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
                if type(platform).__name__ == 'OneWayUpPlatform':
                    pygame.draw.rect(image, (255,0,255, 150), (int(platform.hitbox[0]-self.camera_manager.camera.scroll[0]),int(platform.hitbox[1]-self.camera_manager.camera.scroll[1]),platform.hitbox[2],platform.hitbox[3]), 0)#draw hitbox
                elif type(platform).__name__ == 'CollisionRightAngle':
                    pygame.draw.rect(image, (0,255,0, 150), (int(platform.hitbox[0]-self.camera_manager.camera.scroll[0]),int(platform.hitbox[1]-self.camera_manager.camera.scroll[1]),platform.hitbox[2],platform.hitbox[3]), 1)#draw hitbox
                else:
                    pygame.draw.rect(image, (0,0,0, 150), (int(platform.hitbox[0]-self.camera_manager.camera.scroll[0]),int(platform.hitbox[1]-self.camera_manager.camera.scroll[1]),platform.hitbox[2],platform.hitbox[3]), 0)#draw hitbox
            for fade in self.bg_fade:
                pygame.draw.rect(image, (255,100,100), (int(fade.hitbox[0]-fade.parallax[0]*self.camera_manager.camera.scroll[0]),int(fade.hitbox[1]-fade.parallax[1]*self.camera_manager.camera.scroll[1]),fade.hitbox[2],fade.hitbox[3]),1)#draw hitbox
            for light in self.lights.lights_sources:
                pygame.draw.rect(image, (255,100,100), (int(light.hitbox[0]-light.parallax[0]*self.camera_manager.camera.scroll[0]),int(light.hitbox[1]-light.parallax[1]*self.camera_manager.camera.scroll[1]),light.hitbox[2],light.hitbox[3]),1)#draw hitbox

            for group in self.all_bgs.group_dict.values():
                for obj in group:
                    if type(obj).__name__ == 'River':
                        pygame.draw.rect(image, (0,0,255), (int(obj.reflect_rect[0]),int(obj.reflect_rect[1]),obj.reflect_rect[2],obj.reflect_rect[3]),1)#draw hitbox
                        pygame.draw.rect(image, (255,0,0), (int(obj.rect[0]-obj.parallax[0]*self.camera_manager.camera.scroll[0]),int(obj.rect[1]-obj.parallax[1]*self.camera_manager.camera.scroll[1]),obj.rect[2],obj.rect[3]),1)#draw hitbox

            for group in self.all_fgs.group_dict.values():
                for obj in group:
                    if type(obj).__name__ == 'River':
                        pygame.draw.rect(image, (0,0,255), (int(obj.reflect_rect[0]),int(obj.reflect_rect[1]),obj.reflect_rect[2],obj.reflect_rect[3]),1)#draw hitbox
                        pygame.draw.rect(image, (255,0,0), (int(obj.rect[0]-obj.parallax[0]*self.camera_manager.camera.scroll[0]),int(obj.rect[1]-obj.parallax[1]*self.camera_manager.camera.scroll[1]),obj.rect[2],obj.rect[3]),1)#draw hitbox

            for reflect in self.cosmetics:
                if type(reflect).__name__ == 'River':
                    pygame.draw.rect(image, (0,0,255), (int(reflect.reflect_rect[0]),int(reflect.reflect_rect[1]),reflect.reflect_rect[2],reflect.reflect_rect[3]),1)#draw hitbox
                    pygame.draw.rect(image, (255,0,0), (int(reflect.rect[0]-reflect.parallax[0]*self.camera_manager.camera.scroll[0]),int(reflect.rect[1]-reflect.parallax[1]*self.camera_manager.camera.scroll[1]),reflect.rect[2],reflect.rect[3]),1)#draw hitbox

            tex = self.game.display.surface_to_texture(image)
            self.game.display.render(tex, target)#shader render
            tex.release()
