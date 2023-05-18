import pygame
import Read_files
import Engine
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

from time import perf_counter

class Game_Objects():
    def __init__(self, game):
        self.game = game
        self.font = Read_files.Alphabet()#intitilise the alphabet class, scale of alphabet
        self.controller = Read_files.Controller()
        self.sound = sound.Sound()
        self.create_groups()
        self.weather = weather.Weather(self)#initiate weather
        self.collisions = Engine.Collisions(self)
        self.map = map_loader.Level(self)
        self.camera = camera.Camera(self)
        self.world_state = world_state.World_state(self)#save/handle all world state stuff here
        self.UI = {'gameplay':UI.Gameplay_UI(self),'map':UI.UI_loader(self,'map'),'omamori':UI.UI_loader(self,'omamori'),'journal':UI.UI_loader(self,'journal'),'fast_travel':UI.UI_loader(self,'fast_travel'),'ability_spirit_upgrade':UI.UI_loader(self,'ability_spirit_upgrade'),'ability_movement_upgrade':UI.UI_loader(self,'ability_movement_upgrade')}
        self.save_load = save_load.Save_load(self)#contains save and load attributes to load and save game
        #self.object_pool = object_pool.Object_pool(self)

    def create_groups(self):#define all sprite groups
        self.enemies = pygame.sprite.Group()#groups.Shader_group()
        self.npcs = pygame.sprite.Group()#groups.Shader_group()
        self.platforms = pygame.sprite.Group()
        self.platforms_ramps = pygame.sprite.Group()
        self.all_bgs = pygame.sprite.LayeredUpdates()#groups.Shader_layered_group()#
        self.all_fgs = pygame.sprite.LayeredUpdates()#groups.Shader_layered_group()#
        self.bg_interact = pygame.sprite.Group()#small grass stuff so that interactables blends with BG
        self.eprojectiles = pygame.sprite.Group()#groups.Shader_group()
        self.fprojectiles = pygame.sprite.Group()#groups.Shader_group()
        self.loot = pygame.sprite.Group()#groups.Shader_group()
        self.entity_pause = groups.PauseGroup() #all Entities that are far away
        self.cosmetics = pygame.sprite.Group()#groups.Shader_group()#things we just want to blit
        self.camera_blocks = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()#groups.Shader_group()#player collisions, when pressing T/Y and projectile collisions: chest, bushes, collision path, sign post, save point
        self.reflections = groups.Specialdraw_Group()
        self.layer_pause = groups.PauseLayer()

        #initiate player
        self.player = Entities.Player([0,0],self)
        self.players = pygame.sprite.Group()#groups.Shader_group()
        self.players.add(self.player)

    def load_map(self, map_name, spawn = '1',fade = True):
        t1_start = perf_counter()
        self.player.enter_idle()
        self.player.reset_movement()
        self.clean_groups()
        self.map.load_map(map_name,spawn)
        self.camera.reset_player_center()
        t1_stop = perf_counter()
        print(t1_stop-t1_start)

        if fade:
            new_game_state = states.Fading(self.game)
            new_game_state.enter_state()

    def load_bg_music(self):#called from fade
        if not self.map.area_change: return
        try:
            self.sound.load_bg_sound(self.map.area_name)
            self.sound.play_bg_sound()
        except FileNotFoundError:
            print("No BG music found")

    def clean_groups(self):
        self.npcs.empty()#maybe a problem if we have a bank? -> save the money to world state
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
        self.collisions.platform_collision(self.players)
        self.collisions.platform_collision(self.enemies)
        self.collisions.platform_collision(self.npcs)
        self.collisions.platform_collision(self.loot)

        self.collisions.player_collision(self.loot)
        self.collisions.player_collision(self.enemies)
        self.collisions.interactables_collision()

        self.collisions.counter(self.fprojectiles,self.eprojectiles)
        self.collisions.projectile_collision(self.fprojectiles,self.enemies)
        self.collisions.projectile_collision(self.eprojectiles,self.players)

    def update(self):
        self.camera.update()
        self.weather.update()
        scroll = [-self.camera.scroll[0],-self.camera.scroll[1]]
        self.update_groups(scroll)

    def update_groups(self, scroll = (0,0)):
        self.platforms.update(scroll)
        self.platforms_ramps.update(scroll)
        self.layer_pause.update(scroll)#should be before all_bgs and all_fgs
        self.all_bgs.update(scroll)
        self.bg_interact.update(scroll)
        self.all_fgs.update(scroll)
        self.players.update(scroll)
        self.entity_pause.update(scroll)#should be before enemies, npcs and interactable groups
        self.enemies.update(scroll)
        self.npcs.update(scroll)
        self.fprojectiles.update(scroll)
        self.eprojectiles.update(scroll)
        self.loot.update(scroll)
        self.cosmetics.update(scroll)
        self.camera_blocks.update(scroll)
        self.interactables.update(scroll)
        self.reflections.update(scroll)

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
        self.entity_pause.draw(self.game.screen)
        self.cosmetics.draw(self.game.screen)
        self.reflections.draw()#do not need to send screen. Should be before fgs
        self.all_fgs.draw(self.game.screen)
        #self.camera_blocks.draw(self.game.screen)

        #temporaries draws. Shuold be removed
        if self.game.RENDER_HITBOX_FLAG:
            for projectile in self.fprojectiles.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), projectile.hitbox,2)#draw hitbox
            for projectile in self.eprojectiles.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), projectile.hitbox,2)#draw hitbox
            for enemy in self.enemies.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), enemy.hitbox,2)#draw hitbox
                pygame.draw.rect(self.game.screen, (255,0,255), enemy.rect,2)#draw hitbox
            #for loot in self.loot.sprites():#go through the group
            #    pygame.draw.rect(self.game.screen, (0,0,255), loot.hitbox,2)#draw hitbox
            #    pygame.draw.rect(self.game.screen, (255,0,255), loot.rect,2)#draw hitbox
            for cos in self.interactables.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), cos.hitbox,2)#draw hitbox

            pygame.draw.rect(self.game.screen, (0,0,255), self.player.hitbox,2)#draw hitbox
            pygame.draw.rect(self.game.screen, (255,0,255), self.player.rect,2)#draw hitbox

            for platform in self.platforms:#go through the group
                pygame.draw.rect(self.game.screen, (255,0,0), platform.hitbox,1)#draw hitbox
            for ramp in self.platforms_ramps:
                pygame.draw.rect(self.game.screen, (255,100,100), ramp.hitbox,1)#draw hitbox
            for int in self.interactables:
                pygame.draw.rect(self.game.screen, (255,100,100), int.hitbox,1)#draw hitbox
