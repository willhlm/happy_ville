import pygame
import Engine
import Entities
import Level
import Action
import UI
import Sprites

game=UI.Game_UI()

platforms = pygame.sprite.Group()
hero = pygame.sprite.Group()
enemies = pygame.sprite.Group()

knight=Entities.Player([400,300])
hero.add(knight)

sprites = {'knight': Sprites.Sprites_player()}

map=Level.Tilemap()
map.define_chunks('./Tiled/Level1.csv')

#tePlatforms,teEnemies=map.load_tiles('./Tiled/Level1.csv')
#platforms.add(tePlatforms)#whole map
#enemies.add(teEnemies)#whole map

def draw():
    platforms.draw(game.screen)
    hero.draw(game.screen)
    #enemies.draw(game.screen)

def scrolling():
    map.true_scroll[0]+=(knight.rect.center[0]-4*map.true_scroll[0]-410)/20
    map.true_scroll[1]+=(knight.rect.center[1]-map.true_scroll[1]-328)

    map.scroll=map.true_scroll.copy()
    map.scroll[0]=int(map.scroll[0])
    map.scroll[1]=int(map.scroll[1])

    if knight.action['death']:#if kngiht is dead, don't move game.screen
        map.scroll[0]=0
        map.scroll[1]=0

    platforms.update([-map.scroll[0],-map.scroll[1]])
    hero.update([-map.scroll[0],-map.scroll[1]])
    enemies.update([-map.scroll[0],-map.scroll[1]])

while True:
    game.screen.fill((255,255,255))#fill game.screen

    platforms,enemies=map.load_chunks()

    scrolling()

    game.input(knight)
    Entities.Enemy_1.move(knight,enemies)#the enemy Ai movement, based on knight position

    Engine.Physics.movement(hero)
    Engine.Physics.movement(enemies)
    Engine.Collisions.check_collisions(hero,platforms)
    Engine.Collisions.check_collisions(enemies,platforms)
    Engine.Animation.set_img(hero,sprites['knight'])
    Engine.Animation.set_img(enemies,sprites['knight'])
    

    Action.swing_sword(hero,platforms,enemies,game.screen)#sword swinger, target1,target2
    Action.swing_sword(enemies,platforms,hero,game.screen)#sword swinger, target1,target2

    pygame.draw.rect(game.screen, (255,0,0), knight.rect,2)#checking hitbox
    pygame.draw.rect(game.screen, (0,255,0), knight.hitbox,2)#checking hitbox

    draw()
    pygame.display.update()#update after every change
    game.clock.tick(60)#limmit FPS
