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

class Empty_object():#instead of an entity
    def __init__(self):
        self.dir = [1,0]

class Rectangle():#the rectangles that will be blitted
    def __init__(self,pos, text,parent_rect):
        self.image = pygame.Surface((120,20)).convert()
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image,(255,255,255,255),self.rect)
        text_surface = font.render(str(text),True,(0,0,0))#antialias flag
        self.image.blit(text_surface,self.rect.topleft)
        self.rect.topleft = pos
        self.pos = pos
        self.click = False
        if parent_rect == None:
            self.parent_rect = self
        else:
            self.parent_rect = parent_rect

    def move(self):
        if self.click:
            self.rect.topleft = pygame.mouse.get_pos()
            self.pos = pygame.mouse.get_pos()

    def draw_line(self,surface):
        pygame.draw.line(surface,(255,255,255),self.rect.topleft,self.parent_rect.pos)

entity = Empty_object()
AI.build_tree(entity)

def find_all(node):
    result = []
    result.append(node)
    for child in node.children:
        result += find_all(child) # recursion; result will be a list
    return result

rects = []
def organise_nodes(nodes):
    for index, node in enumerate(nodes):
        if node.parent != None:
            row = node.get_level()
            col = node.parent.children.index(node)
            length = len(node.parent.children)
            position = [node.parent.pos[0] + (col - length*0.3)*400,node.parent.pos[1] + 40*row]
            rec = Rectangle(position, type(node).__name__,node.parent.rect)
        else:
            position = [700,0]
            rec = Rectangle(position, type(node).__name__,None)

        node.pos = position
        node.rect = rec
        rects.append(rec)

all_nodes = find_all(entity.AI)#take all nodes and make into a list
organise_nodes(all_nodes)

def on_click(pos):#make sure that only one rectangle is affected when clicking
    for index, rect in enumerate(rects):
        if rect.rect.collidepoint(pos):
            rect.click = True
            return

while True:
    display.fill((0,0,0))
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.quit()
            sys.exit()
        #clicking
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for index, rect in enumerate(rects):
                on_click(pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            for index, rect in enumerate(rects):
                rect.click = False

    for index, rect in enumerate(rects):
        rect.move()
        rect.draw_line(display)
        display.blit(rect.image,rect)

    pygame.display.update()
    clock.tick(60)
