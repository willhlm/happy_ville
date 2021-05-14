import pygame
import Engine
import Entities
import Level
import Action
import UI
import Read_files
import BG

platforms = pygame.sprite.Group()
bg_blocks = pygame.sprite.Group()
hero = pygame.sprite.Group()
enemies = pygame.sprite.Group()
npc = pygame.sprite.Group()
invisible_blocks = pygame.sprite.Group()
weather=pygame.sprite.Group()

game=UI.Game_UI()#initilise the game

weather_paricles=BG.Background()
weather.add(weather_paricles)

knight=Entities.Player([200,50])
hero.add(knight)

sprites = {'knight': Read_files.Sprites_player()}

map=Level.Tilemap('village1')
#map.define_chunks('./Tiled/Level1.csv')
map.define_chunks()#('./Tiled/layer_test_collision.csv')

#tePlatforms,teEnemies=map.load_tiles('./Tiled/village1_colision.csv')
#platforms.add(tePlatforms)#whole map
#enemies.add(teEnemies)#whole map

def draw():
    bg_blocks.draw(game.screen)
    platforms.draw(game.screen)
    hero.draw(game.screen)
    enemies.draw(game.screen)
    npc.draw(game.screen)

def scrolling():
    map.scrolling(knight.rect)
    scroll = [-map.scroll[0],-map.scroll[1]]
    platforms.update(scroll)
    bg_blocks.update(scroll)
    hero.update(scroll)
    enemies.update(scroll)
    npc.update(scroll)
    invisible_blocks.update(scroll)
    weather.update(scroll,game.screen)

while True:
    game.screen.fill((207,238,250))#fill game.screen

    weather=weather_paricles.create_particle('sakura')

    platforms,bg_blocks,enemies,npc,invisible_blocks=map.load_chunks()

    scrolling()

    game.input(knight)

    for entity in enemies.sprites():
        entity.AI(knight)#the enemy Ai movement, based on knight position
    for entity in npc.sprites():
        entity.AI()

    Engine.Physics.movement(hero)
    Engine.Physics.movement(enemies)
    Engine.Physics.movement(npc)

    Engine.Collisions.check_collisions(hero,platforms)
    Engine.Collisions.check_collisions(enemies,platforms)
    Engine.Collisions.check_collisions(npc,platforms)
    Engine.Collisions.check_invisible(npc,invisible_blocks)

    Engine.Animation.set_img(hero)
    Engine.Animation.set_img(enemies)
    Engine.Animation.set_img(npc)

    Action.f_action(hero,platforms,enemies,game.screen)#f_action swinger, target1,target2
    Action.f_action(enemies,platforms,hero,game.screen)#f_action swinger, target1,target2

    pygame.draw.rect(game.screen, (255,0,0), knight.rect,2)#checking hitbox
    pygame.draw.rect(game.screen, (0,255,0), knight.hitbox,2)#checking hitbox

    draw()

    game.screen.blit(game.blit_health(knight),(20,20))#blir hearts
    game.display.blit(pygame.transform.scale(game.screen,game.WINDOW_SIZE_scaled),(0,0))

    Engine.Collisions.check_npc_collision(knight,npc,game.display)#need to be at the end so that the conversation text doesn't get scaled

    print(game.clock)
    pygame.display.update()#update after every change
    game.clock.tick(60)#limmit FPS
