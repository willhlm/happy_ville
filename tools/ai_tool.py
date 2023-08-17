import sys
sys.path.append('../')

import behaviour_tree
import pygame
import AI_exploding_mygga as AI#import the one you want to check

pygame.init()
display = pygame.display.set_mode((1500,1000))
screen = pygame.Surface((1500,1000))
clock = pygame.time.Clock()
font = pygame.font.Font('freesansbold.ttf',20)

class Empty_object():
    def __init__(self):
        self.dir = [1,0]

class Rectangle():
    def __init__(self,pos, text):
        self.image = pygame.Surface((120,20)).convert()
        self.rect = self.image.get_rect()
        self.pos = pos
        pygame.draw.rect(self.image,(255,255,255,255),self.rect)
        text_surface = font.render(str(text),True,(0,0,0))#antialias flag
        self.image.blit(text_surface,self.rect.topleft)

entity = Empty_object()
AI.build_tree(entity)

rects = []
pos = []

def make_tree(nodes, row, col):
    for index, child in enumerate(nodes.children):
        row = child.get_level()
        col = child.parent.children.index(child)
        length = len(child.parent.children)

        position = [child.parent.pos[0] + (col - length*0.3)*400,child.parent.pos[1] + 40*row]
        pos.append(position)
        child.pos = position
        rects.append(Rectangle(pos[-1], type(child).__name__))
        print(type(child).__name__)
        make_tree(child)


entity.AI.pos = [700,0]
make_tree(entity.AI)

while True:
    display.fill((0,0,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()

    for index, rect in enumerate(rects):
        display.blit(rect.image,pos[index])

    pygame.display.update()
    clock.tick(60)
