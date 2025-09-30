import pygame
from engine.utils import read_files

class Alphabet():
    def __init__(self, game_objects, font_name = None, font_size = 12):
        self.game_objects = game_objects
        self.font_atals = game_objects.game.display.make_font_atlas(font_path = 'assets/sprites/utils/fonts/8BitSnobbery.ttf', font_size = 12)        
         
        self.font = pygame.font.Font('assets/sprites/utils/fonts/8BitSnobbery' + '.ttf', font_size)
        self.text_bg_dict = {'default':read_files.generic_sheet_reader("assets/sprites/utils/text_bg5.png",16,16,3,3), 'text_bubble':read_files.generic_sheet_reader("assets/sprites/utils/text_bg6.png",16,16,3,3)}

    def get_height(self):
        return self.font.get_height()

    def render(self, surface_size=False, text='', letter_frame=1000, color=(255, 255, 255), alignment='left'):
        # Limit text to `letter_frame`
        visible_text = text[:letter_frame]

        # **If text is empty or only spaces, return an empty transparent texture**
        if not visible_text.strip():
            if surface_size:
                size = surface_size
            else:
                size = (1,1)
            empty_surface = pygame.Surface(size, pygame.SRCALPHA, 32).convert_alpha()
            empty_surface.fill((0, 0, 0, 0))  # Transparent
            return self.game_objects.game.display.surface_to_texture(empty_surface)

        # Initialize
        words = visible_text.split(" ")
        if surface_size:
            max_width = surface_size[0]
        else:
            max_width = self.font.size(visible_text)[0] + 1

        line_height = self.font.get_height()
        lines, line_widths = [], []
        current_line = ""
        x, y = 0, 0

        # Word wrapping based on visible text
        for word in words:
            test_line = (current_line + " " + word).strip()

            # If new word exceeds width, wrap it
            if self.font.size(test_line)[0] > max_width and current_line:
                lines.append(current_line)
                line_widths.append(self.font.size(current_line)[0])
                current_line = word  # Start new line
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)
            line_widths.append(self.font.size(current_line)[0])

        # **Ensure surface is large enough**
        if not surface_size:
            total_height = len(lines) * line_height
            surface_size = (max_width, total_height)

        # Create transparent surface
        text_surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()
        text_surface.fill((0, 0, 0, 0))  # Transparent background

        # Render each line correctly
        for i, line in enumerate(lines):
            rendered_text = self.font.render(line, False, color)
            if alignment == 'center':
                x = (surface_size[0] - line_widths[i]) // 2  # Centering
            else:
                x = 0  # Left alignment

            text_surface.blit(rendered_text, (x, y))
            y += line_height  # Move to next line

        return self.game_objects.game.display.surface_to_texture(text_surface)

    def fill_text_bg(self, surface_size, type = 'default'):
        col = int(surface_size[0]/16)
        row = int(surface_size[1]/16)
        surface = pygame.Surface(surface_size, pygame.SRCALPHA, 32).convert_alpha()

        for r in range(0,row):
            for c in range(0,col):
                if r==0:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][0],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][2],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][1],(c*16,r*16))
                elif r==row-1:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][6],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][8],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][7],(c*16,r*16))
                else:
                    if c==0:
                        surface.blit(self.text_bg_dict[type][3],(c*16,r*16))
                    elif c==col-1:
                        surface.blit(self.text_bg_dict[type][5],(c*16,r*16))
                    else:
                        surface.blit(self.text_bg_dict[type][4],(c*16,r*16))

        return self.game_objects.game.display.surface_to_texture(surface)
