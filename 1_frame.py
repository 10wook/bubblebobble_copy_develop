import pygame
import os

pygame.init()
screen_width = 448
screen_height = 720
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Puzzle Bobble")
clock = pygame.time.Clock()


current_path = os.path.dirname(__file__)
#배경
background = pygame.image.load(os.path.join(current_path,"background.png"))


running = True
while running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(background,(0,0))
    pygame.display.update()
     
    
    
pygame.quit()