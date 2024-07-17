import pygame
import sys
import psutil
process = psutil.Process()


# Initialize Pygame
pygame.init()

# Set up the display
window_size = (800, 600)
screen = pygame.display.set_mode(window_size)
#print(pygame.print_debug_info())
# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the screen with a color (optional, here we fill it with white)
    screen.fill((255, 255, 255))
    print(process.memory_info().rss/1000000)  
    # Update the display
    pygame.display.update()



# Quit Pygame
pygame.quit()
sys.exit()

