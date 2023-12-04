import pygame
import Read_files
import collisions
import Entities
import map_loader
import sound
import states
import camera
import weather
import constants as C
import world_state
import UI
import save_load
import groups
import object_pool
import controller

from time import perf_counter

class Game_Objects():
    def __init__(self, game):
        self.game = game
        self.font = Read_files.Alphabet()#intitilise the alphabet class, scale of alphabet
        self.controller = controller.Controller('playsation')
        self.sound = sound.Sound()
        self.create_groups()
        self.weather = weather.Weather(self)#initiate weather
        self.collisions = collisions.Collisions(self)
        self.map = map_loader.Level(self)
        self.camera = camera.Camera(self)
        self.world_state = world_state.World_state(self)#save/handle all world state stuff here
        self.UI = {'gameplay':UI.Gameplay_UI(self)}
        self.save_load = save_load.Save_load(self)#contains save and load attributes to load and save game
        self.object_pool = object_pool.Object_pool(self)

    def create_groups(self):#define all sprite groups
        self.enemies = groups.Group(self)#groups.Shader_group()
        self.npcs = groups.Group(self)#groups.Shader_group()
        self.platforms = groups.Specialdraw_Group()
        self.platforms_ramps = groups.Specialdraw_Group()
        self.all_bgs = groups.LayeredUpdates(self)#groups.Shader_layered_group()#
        self.all_fgs = groups.LayeredUpdates(self)#groups.Shader_layered_group()#
        self.bg_interact = groups.Group(self)#small grass stuff so that interactables blends with BG
        self.bg_fade = groups.Group(self)#fg stuff that should dissapear when player comes: this should not blit or update. it will just run collision checks
        self.eprojectiles = groups.Group(self)#groups.Shader_group()
        self.fprojectiles = groups.Group(self)#groups.Shader_group()
        self.loot = groups.Group(self)#groups.Shader_group()
        self.entity_pause = groups.PauseGroup() #all Entities that are far away
        self.cosmetics = groups.Group(self)#groups.Shader_group()#things we just want to blit
        self.camera_blocks = groups.Group(self)#pygame.sprite.Group()
        self.interactables = groups.Group(self)#player collisions, when pressing T/Y and projectile collisions: chest, bushes, collision path, sign post, save point
        self.reflections = groups.Specialdraw_Group()
        self.layer_pause = groups.PauseLayer()

        #initiate player
        self.player = Entities.Player([0,0],self)
        self.players = groups.Group_player(self)#blits on float positions
        self.players.add(self.player)

    def load_map(self, previous_state, map_name, spawn = '1',fade = True):#fade out before loading the map
        if fade:#for cutscenes
            new_game_state = states.Fadeout(self.game, previous_state, map_name, spawn,fade)#it will call load_map2 after loading
            new_game_state.enter_state()
        else:
            self.load_map2(map_name, spawn, fade)

    def load_map2(self, map_name, spawn = '1',fade = True):#called from fadeout
        self.clean_groups()
        t1_start = perf_counter()
        self.map.load_map(map_name,spawn)
        t1_stop = perf_counter()
        print(t1_stop-t1_start)

        if fade:#for cutscenes
            new_game_state = states.Fadein(self.game)#when this state is finished, it will set aila to idle
            new_game_state.enter_state()

    def load_bg_music(self):#called from fade
        if not self.map.area_change: return
        try:
            self.sound.load_bg_sound(self.map.area_name)
            self.sound.play_bg_sound()
        except FileNotFoundError:
            print("No BG music found")

    def clean_groups(self):
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
        self.reflections.empty()
        self.cosmetics.empty()
        self.layer_pause.empty()

    def collide_all(self):
        self.platform_collision()

        self.collisions.player_collision(self.loot)
        self.collisions.player_collision(self.enemies)
        self.collisions.player_collision(self.bg_fade)
        self.collisions.interactables_collision()

        self.collisions.counter(self.fprojectiles,self.eprojectiles)
        self.collisions.projectile_collision(self.fprojectiles,self.enemies)
        self.collisions.projectile_collision(self.eprojectiles,self.players)

    def platform_collision(self):
        self.collisions.platform_collision(self.players)
        self.collisions.platform_collision(self.enemies)
        self.collisions.platform_collision(self.npcs)
        self.collisions.platform_collision(self.loot)

    def update(self):
        self.camera_blocks.update()#need to be before camera: caemras stop needs tobe calculated before the scroll
        self.camera.update()#should be first
        self.platforms.update()
        self.platforms_ramps.update()
        self.layer_pause.update()#should be before all_bgs and all_fgs
        self.all_bgs.update()
        self.bg_interact.update()
        self.all_fgs.update()
        self.players.update()
        self.entity_pause.update()#should be before enemies, npcs and interactable groups
        self.enemies.update()
        self.npcs.update()
        self.fprojectiles.update()
        self.eprojectiles.update()
        self.loot.update()
        self.cosmetics.update()
        self.interactables.update()
        self.reflections.update()
        self.weather.update()

    def draw(self):
        self.all_bgs.draw(self.game.screen)
        self.interactables.draw(self.game.screen)#should be before bg_interact
        self.bg_interact.draw(self.game.screen)

        self.enemies.draw(self.game.screen)
        self.npcs.draw(self.game.screen)
        self.players.draw(self.game.screen)
        self.fprojectiles.draw(self.game.screen)
        self.eprojectiles.draw(self.game.screen)
        self.loot.draw(self.game.screen)
        self.platforms.draw()
        self.cosmetics.draw(self.game.screen)
        self.reflections.draw()#do not need to send screen. Should be before fgs
        self.all_fgs.draw(self.game.screen)
        #self.camera_blocks.draw(self.game.screen)

        #temporaries draws. Shuold be removed
        if self.game.RENDER_HITBOX_FLAG:
            pygame.draw.rect(self.game.screen, (0,0,255), (round(self.player.hitbox[0]-self.camera.true_scroll[0]),round(self.player.hitbox[1]-self.camera.true_scroll[1]),self.player.hitbox[2],self.player.hitbox[3]),2)#draw hitbox
            pygame.draw.rect(self.game.screen, (255,0,255), (round(self.player.rect[0]-self.camera.true_scroll[0]),round(self.player.rect[1]-self.camera.true_scroll[1]),self.player.rect[2],self.player.rect[3]),2)#draw hitbox

            for projectile in self.fprojectiles.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), (int(projectile.hitbox[0]-self.camera.scroll[0]),int(projectile.hitbox[1]-self.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for projectile in self.eprojectiles.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), (int(projectile.hitbox[0]-self.camera.scroll[0]),int(projectile.hitbox[1]-self.camera.scroll[1]),projectile.hitbox[2],projectile.hitbox[3]),1)#draw hitbox
            for enemy in self.enemies.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), [enemy.hitbox[0]-self.camera.scroll[0],enemy.hitbox[1]-self.camera.scroll[1],enemy.hitbox[2],enemy.hitbox[3]],2)#draw hitbox
                pygame.draw.rect(self.game.screen, (255,0,255), [enemy.rect[0]-self.camera.scroll[0],enemy.rect[1]-self.camera.scroll[1],enemy.rect[2],enemy.rect[3]],2)#draw hitbox
            for cos in self.interactables.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), (int(cos.hitbox[0]-self.camera.scroll[0]),int(cos.hitbox[1]-self.camera.scroll[1]),cos.hitbox[2],cos.hitbox[3]),1)#draw hitbox
                pygame.draw.rect(self.game.screen, (255,0,255), (int(cos.rect[0]-self.camera.scroll[0]),int(cos.rect[1]-self.camera.scroll[1]),cos.rect[2],cos.rect[3]),1)#draw hitbox
            for cos in self.loot.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), (int(cos.hitbox[0]-self.camera.scroll[0]),int(cos.hitbox[1]-self.camera.scroll[1]),cos.hitbox[2],cos.hitbox[3]),1)#draw hitbox
                pygame.draw.rect(self.game.screen, (255,0,255), (int(cos.rect[0]-self.camera.scroll[0]),int(cos.rect[1]-self.camera.scroll[1]),cos.rect[2],cos.rect[3]),1)#draw hitbox
            for platform in self.platforms:#go through the group
                pygame.draw.rect(self.game.screen, (255,0,0), (int(platform.hitbox[0]-self.camera.scroll[0]),int(platform.hitbox[1]-self.camera.scroll[1]),platform.hitbox[2],platform.hitbox[3]),1)#draw hitbox
            for ramp in self.platforms_ramps:
                pygame.draw.rect(self.game.screen, (255,100,100), (int(ramp.hitbox[0]-self.camera.scroll[0]),int(ramp.hitbox[1]-self.camera.scroll[1]),ramp.hitbox[2],ramp.hitbox[3]),1)#draw hitbox
            for fade in self.bg_fade:
                pygame.draw.rect(self.game.screen, (255,100,100), (int(fade.hitbox[0]-fade.parallax[0]*self.camera.scroll[0]),int(fade.hitbox[1]-fade.parallax[1]*self.camera.scroll[1]),fade.hitbox[2],fade.hitbox[3]),1)#draw hitbox
