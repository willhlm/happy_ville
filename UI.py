import pygame


class game():
    def __init__(self,ESC=False):
        self.screen=pygame.display.set_mode((800,600))
        self.clock=pygame.time.Clock()
        self.gameover=False
        self.ESC=ESC

        def start_menu(self):
            while self.ESC:

                start_surface=game_font.render('Start Game',True,(255,255,255))#antialias flag
                start_rect=start_surface.get_rect(center=(200,100))#position


                pygame.draw.rect(self.screen,(255,255,255),start_rect,width=2)
                pygame.draw.rect(self.screen,(255,255,255),exit_rect,width=2)

                if start_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                    self.ESC=False
                    self.click=False
                elif exit_rect.collidepoint((pygame.mouse.get_pos())) ==True and self.click==True:
                    pygame.quit()
                    sys.exit()

                for event in pygame.event.get():
                    if event.type==pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type==pygame.MOUSEBUTTONDOWN:
                        self.click=True
                    if event.type==pygame.MOUSEBUTTONUP:
                        self.click=False
