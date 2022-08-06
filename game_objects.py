import pygame
import Read_files
import Engine
import Entities
import map_loader
import particles
import sound
import states
import camera
import json
import weather

class Game_Objects():

    def __init__(self, game):
        self.game = game
        self.controller = Read_files.Controller('xbox')
        self.sound = sound.Sound()
        self.cutscenes_complete = []
        self.create_groups()
        self.weather=weather.Weather(self)#initiate weather
        self.weather.create_particles('Sakura')#this should be callen when loading the map I suppose, or trigegr

        #self.reflection=BG.Reflection()
        self.camera = [camera.Auto(self)]
        self.collisions = Engine.Collisions(self)

    def save_game(self):#save_obj calls to_json method in the object: write the to_json mthod such that it save the attributes of interest.
        Read_files.save_obj(self.player)
        Read_files.save_obj(self)

    def load_game(self):
        Read_files.load_obj(self.player)
        Read_files.load_obj(self)

    def create_groups(self):
        #define all sprite groups
        self.enemies = pygame.sprite.Group()# pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.platforms_ramps = pygame.sprite.Group()
        self.all_bgs = pygame.sprite.LayeredUpdates()
        self.all_fgs = pygame.sprite.LayeredUpdates()
        self.weather_paricles = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.eprojectiles = pygame.sprite.Group()#arrows and sword
        self.fprojectiles = pygame.sprite.Group()#arrows and sword
        self.loot = pygame.sprite.Group()
        self.entity_pause = Entities.PauseGroup() #include all Entities that are far away,Entities.PauseGroup()
        self.cosmetics = pygame.sprite.Group() #spirits
        self.camera_blocks = pygame.sprite.Group()
        self.triggers = pygame.sprite.Group()
        self.all_Entities = pygame.sprite.Group()
        self.interacting_cosmetics = pygame.sprite.Group()

        #initiate player
        self.player = Entities.Player([200,50],self)
        self.players = pygame.sprite.Group(self.player)
        self.player_center = (int(self.game.WINDOW_SIZE[0]/2),int(2*self.game.WINDOW_SIZE[1]/3))

    def load_map(self, map_name, spawn = '1',fade=True):
        self.map = map_loader.Level(map_name, self, spawn)
        self.initiate_groups()
        if fade:
            new_game_state = states.Fading(self.game)
            new_game_state.enter_state()

    def load_bg_music(self):
        try:
            self.sound.load_bg_sound(self.map.level_name)
            self.sound.play_bg_sound()
        except FileNotFoundError:
            print("No BG music found")

    def initiate_groups(self):
        #clean all groups
        self.npcs.empty()#maybe a problem if we have a bank?
        self.enemies.empty()
        self.interactables.empty()
        self.platforms.empty()
        self.platforms_ramps.empty()
        self.entity_pause.empty()
        self.all_bgs.empty()
        self.all_fgs.empty()
        self.camera_blocks.empty()
        self.triggers.empty()
        self.interacting_cosmetics.empty()

        #load all objects and art
        self.map.load_statics()
        self.map.load_collision_layer()
        self.map.load_bg()

    def collide_all(self):
        self.collisions.collide(self.players,self.platforms, self.platforms_ramps)
        self.collisions.collide(self.enemies,self.platforms, self.platforms_ramps)
        self.collisions.collide(self.npcs,self.platforms, self.platforms_ramps)
        self.collisions.collide(self.loot,self.platforms, self.platforms_ramps)
        self.collisions.pickup_loot(self.player,self.loot)
        self.collisions.check_enemy_collision(self.player,self.enemies)

        self.collisions.check_trigger(self.player,self.triggers)

        self.collisions.interact_cosmetics()

        #if we make all abilities spirit based maybe we don't have to collide with all the platforms? and only check for enemy collisions?
        self.collisions.counter(self.fprojectiles,self.eprojectiles)
        self.collisions.action_collision(self.fprojectiles,self.platforms,self.enemies)
        self.collisions.action_collision(self.eprojectiles,self.platforms,self.players)
        #self.collisions.weather_paricles(self.weather,self.platforms)#weather collisino.

    def scrolling(self):
        self.camera[-1].update()
        scroll = [-self.camera[-1].scroll[0],-self.camera[-1].scroll[1]]
        self.update_groups(scroll)

    def update_groups(self, scroll = (0,0)):
        self.platforms.update(scroll)
        self.platforms_ramps.update(scroll)
        self.all_bgs.update(scroll)
        self.all_fgs.update(scroll)
        self.players.update(scroll)
        self.entity_pause.update(scroll)#should be before enemies and npcs group
        self.enemies.update(scroll)
        self.npcs.update(scroll)
        self.interacting_cosmetics.update(scroll)#bushes, maybye move to enemy?
        self.interactables.update(scroll)
        self.weather_paricles.update(scroll)
        self.fprojectiles.update(scroll)
        self.eprojectiles.update(scroll)
        self.loot.update(scroll)
        self.cosmetics.update(scroll)
        self.camera_blocks.update(scroll)
        self.triggers.update(scroll)

    def draw(self):
        self.all_bgs.draw(self.game.screen)

        #self.platforms.draw(self.game.screen)
        self.interactables.draw(self.game.screen)
        self.enemies.draw(self.game.screen)
        self.npcs.draw(self.game.screen)
        self.players.draw(self.game.screen)
        self.fprojectiles.draw(self.game.screen)
        self.eprojectiles.draw(self.game.screen)
        self.loot.draw(self.game.screen)
        self.entity_pause.draw(self.game.screen)
        self.cosmetics.draw(self.game.screen)
        self.all_fgs.draw(self.game.screen)
        self.interacting_cosmetics.draw(self.game.screen)#bushes move to enemy?
        self.weather_paricles.draw(self.game.screen)

        #self.triggers.draw(self.game.screen)
        #self.camera_blocks.draw(self.game.screen)
        #self.reflection.draw(self.game.screen)
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
            for cos in self.interacting_cosmetics.sprites():#go through the group
                pygame.draw.rect(self.game.screen, (0,0,255), cos.hitbox,2)#draw hitbox

            pygame.draw.rect(self.game.screen, (0,0,255), self.player.hitbox,2)#draw hitbox
            pygame.draw.rect(self.game.screen, (255,0,255), self.player.rect,2)#draw hitbox

            for platform in self.platforms:#go through the group
                pygame.draw.rect(self.game.screen, (255,0,0), platform.hitbox,2)#draw hitbox
            for ramp in self.platforms_ramps:
                pygame.draw.rect(self.game.screen, (255,100,100), ramp.hitbox,2)#draw hitbox
            for int in self.interactables:
                pygame.draw.rect(self.game.screen, (255,100,100), int.hitbox,2)#draw hitbox

    def to_json(self):#stuff to save
        save_dict={'cutscenes_complete':self.cutscenes_complete}
        return save_dict

    def from_json(self,data):#stuff to load
        self.cutscenes_complete=data['cutscenes_complete']
