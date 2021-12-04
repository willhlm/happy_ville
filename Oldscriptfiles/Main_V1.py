import pygame
import engine
import entities
import Level
import Action
import UI
import read_files
import BG

platforms = pygame.sprite.Group()
bg_blocks = pygame.sprite.Group()
hero = pygame.sprite.Group()
enemies = pygame.sprite.Group()
npc = pygame.sprite.Group()
invisible_blocks = pygame.sprite.Group()
weather = pygame.sprite.Group()
interactables = pygame.sprite.Group()
fprojectiles = pygame.sprite.Group()#arrows
eprojectiles = pygame.sprite.Group()#arrows
loot = pygame.sprite.Group()

game = UI.Game_UI()#initilise the game

weather_paricles = BG.Weather()

knight=entities.Player([200,50])
hero.add(knight)

sprites = {'knight': read_files.Sprites_player()}

map = Level.Tilemap('village1','auto')

#tePlatforms,teEnemies=map.load_tiles('./Tiled/village1_colision.csv')
#platforms.add(tePlatforms)#whole map
#enemies.add(teEnemies)#whole map

def draw():
    bg_blocks.draw(game.screen)
    platforms.draw(game.screen)
    interactables.draw(game.screen)
    hero.draw(game.screen)
    enemies.draw(game.screen)
    npc.draw(game.screen)
    fprojectiles.draw(game.screen)
    eprojectiles.draw(game.screen)
    loot.draw(game.screen)

def scrolling():
    map.scrolling(knight.rect,knight.shake)
    scroll = [-map.camera.scroll[0],-map.camera.scroll[1]]

    platforms.update(scroll)
    bg_blocks.update(scroll)
    hero.update(scroll)
    enemies.update(scroll)
    npc.update(scroll)
    interactables.update(scroll)
    invisible_blocks.update(scroll)
    weather.update(scroll,game.screen)
    eprojectiles.update(scroll)
    loot.update(scroll)
    fprojectiles.update(scroll)

while True:
    game.screen.fill((207,238,250))#fill game.screen


    weather=weather_paricles.create_particle('Rain')#weather effects

    platforms,bg_blocks,enemies,npc,invisible_blocks,interactables=map.load_chunks()#chunks
    weather=weather_paricles.create_particle('Sakura')#weather effects

    game.input(knight)#game inputs

    engine.Physics.movement(hero)
    engine.Physics.movement(enemies)
    engine.Physics.movement(npc)

    engine.Collisions.check_collisions(hero,platforms)
    engine.Collisions.check_collisions(enemies,platforms)
    engine.Collisions.check_collisions(npc,platforms)
    engine.Collisions.check_invisible(npc,invisible_blocks)
    engine.Collisions.check_interaction(knight,interactables)
    engine.Collisions.check_collisions_loot(loot,platforms)
    engine.Collisions.pickup_loot(knight,loot)
    loot=engine.Collisions.check_enemy_collision(knight,enemies,loot)

<<<<<<< HEAD
    fprojectiles, loot = Action.actions(fprojectiles,hero,platforms,enemies,game.screen,loot)#f_action swinger, target1,target2
    eprojectiles, loot = Action.actions(eprojectiles,enemies,platforms,hero,game.screen,loot)#f_action swinger, target1,target2

    scrolling()
=======
>>>>>>> dev/UI_migration

    for enemy in enemies.sprites():
        enemy.AI(knight,game.screen)#the enemy Ai movement, based on knight position
    for npcs in npc.sprites():
        npcs.AI()

    engine.Animation.set_img(hero)
    engine.Animation.set_img(enemies)
    engine.Animation.set_img(npc)

    pygame.draw.rect(game.screen, (255,0,0), knight.rect,2)#checking hitbox
    pygame.draw.rect(game.screen, (0,255,0), knight.hitbox,2)#checking hitbox

    draw()

    scrolling()


    game.screen.blit(game.blit_health(knight),(20,20))#blit hearts
    game.blit_fps()

    game.display.blit(pygame.transform.scale(game.screen,game.WINDOW_SIZE_scaled),(0,0))#scale the screen

    engine.Collisions.check_npc_collision(knight,npc,game.display)#need to be at the end so that the conversation text doesn't get scaled

    pygame.display.update()#update after every change
    game.clock.tick(60)#limmit FPS
