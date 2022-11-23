import pygame
import Read_files
import Engine
import Entities
import map_loader
import sound
import states
import camera
import json
import weather
import constants as C

class Game_Objects():

    def __init__(self, game):
        self.game = game
        self.controller = Read_files.Controller('ps4')
        self.sound = sound.Sound()
        self.create_groups()
        self.weather = weather.Weather(self)#initiate weather
        self.collisions = Engine.Collisions(self)
        self.map = map_loader.Level(self)
        self.camera = camera.Auto(self)

        #should these be a world state class? which stores game information stuff
        self.cutscenes_complete = []
        self.statistics = {'kill':{'slime':0,'larv':0,'blue_bird':0,'cultist_warrior':0,'cultist_rogue':0},'ambers':0}
        self.state = 2
        self.world_state = 'state_' + str(self.state)#a flag that describes the progression of the game

    def create_groups(self):
        #define all sprite groups
        self.enemies = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.platforms_ramps = pygame.sprite.Group()
        self.all_bgs = pygame.sprite.LayeredUpdates()
        self.all_fgs = pygame.sprite.LayeredUpdates()
        self.bg_interact = pygame.sprite.Group()#small grass stuff so that interactables blends with BG
        self.eprojectiles = pygame.sprite.Group()#arrows and sword
        self.fprojectiles = pygame.sprite.Group()#arrows and sword
        self.loot = pygame.sprite.Group()
        self.entity_pause = Entities.PauseGroup() #all Entities that are far away
        self.cosmetics = pygame.sprite.Group()#things we just want to blit
        self.camera_blocks = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()#player collisions, when pressing T/Y and projectile collisions: chest, bushes, collision path, sign post, save point

        #initiate player
        self.player = Entities.Player([0,0],self)
        self.players = pygame.sprite.Group(self.player)


    def load_map(self, map_name, spawn = '1',fade = True):
        self.clean_groups()
        self.game.game_objects.player.reset_movement()
        self.map.load_map(map_name,spawn)
        self.camera.reset_player_center()

        if fade:
            new_game_state = states.Fading(self.game)
            new_game_state.enter_state()

    def load_bg_music(self):
        try:
            self.sound.load_bg_sound(self.map.level_name)
            self.sound.play_bg_sound()
        except FileNotFoundError:
            print("No BG music found")

    def clean_groups(self):
        self.npcs.empty()#maybe a problem if we have a bank?
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
        scroll = [-self.camera.scroll[0],-self.camera.scroll[1]]
        self.update_groups(scroll)

    def update_groups(self, scroll = (0,0)):
        self.platforms.update(scroll)
        self.platforms_ramps.update(scroll)
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

    def draw(self):
        self.all_bgs.draw(self.game.screen)
        self.interactables.draw(self.game.screen)
        self.bg_interact.draw(self.game.screen)

        self.enemies.draw(self.game.screen)
        self.npcs.draw(self.game.screen)
        self.players.draw(self.game.screen)
        self.fprojectiles.draw(self.game.screen)
        self.eprojectiles.draw(self.game.screen)
        self.loot.draw(self.game.screen)
        self.entity_pause.draw(self.game.screen)
        self.cosmetics.draw(self.game.screen)
        for sprite in self.cosmetics:
            sprite.special()
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

    def increase_world_state(self):#called when a boss dies
        self.state += 1
        self.world_state = 'state_'+str(self.state)

    def save_game(self):#save_obj calls to_json method in the object: write the to_json mthod such that it save the attributes of interest.
        Read_files.save_obj(self.player)
        Read_files.save_obj(self)

    def load_game(self):#load_obj class from_json: load the stiff from dictionary of interest
        Read_files.load_obj(self.player)
        Read_files.load_obj(self)

    def to_json(self):#stuff to save
        save_dict = {'cutscenes_complete':self.cutscenes_complete}
        return save_dict

    def from_json(self,data):#stuff to load
        self.cutscenes_complete = data['cutscenes_complete']
