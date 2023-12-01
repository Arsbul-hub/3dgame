import pygame
import sys

pygame.init()
width, height = (600, 600)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Крестики-нолики")


item_width, item_height = (width / 3, height / 3)
mas = [[0, 0, 0],
       [0, 0, 0],
       [0, 0, 0]]

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x_mouse, y_mouse = pygame.mouse.get_pos()

            x_cord, y_cord = int(x_mouse / item_width), int(y_mouse / item_height)

            mas[y_cord][x_cord] = 1

    for y in range(3):
        for x in range(3):
            if mas[y][x] == 1:
                pygame.draw.rect(screen, (190, 129, 255), (x * item_width, y * item_height, item_width, item_height))
            else:
                pygame.draw.rect(screen, (0, 0, 0), (x * item_width, y * item_height, item_width, item_height))

    pygame.display.update()
