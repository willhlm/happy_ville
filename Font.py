import pygame

class Alphabet():
    def __init__(self,path):
        self.spacing=1
        self.letter_hight=16
        self.character_order=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
        sheet=pygame.image.load(path).convert()
        self.characters={}
        current_char_width=0
        character_count=0

        for x in range(sheet.get_width()):
            c=sheet.get_at((x,0))

            if character_count>=len(self.character_order):
                break
            else:
                if c[0]==238:#check for red color
                    char_img=self.clip(sheet,x-current_char_width,0, current_char_width,self.letter_hight)
                    self.characters[self.character_order[character_count]]=char_img.copy()
                    character_count+=1
                    current_char_width=0
                else:
                    current_char_width+=1
        self.space_width=self.characters['A'].get_width()

    def render(self,screen,text,loc):
        x_offset=0
        for char in text:
            if char!=' ':
                screen.blit(self.characters[char],(loc[0]+x_offset,loc[1]))
                x_offset+=self.characters[char].get_width()+self.spacing
            else:
                x_offset+=self.space_width+self.spacing

    def clip(self,surf,x,y,x_size,y_size):
        handle_surf=surf.copy()
        clipR=pygame.Rect(x,y,x_size,y_size)
        handle_surf.set_clip(clipR)
        image=surf.subsurface(handle_surf.get_clip())
        return image.copy()
