import random

import pygame
from characters import PacMan

pygame.init()
pygame.font.init()

W = 448
H = 512
win = pygame.display.set_mode((W, H))
pygame.display.set_caption("PacMan")
pygame.display.set_icon(pygame.image.load("pacman1.png"))
clock = pygame.time.Clock()

BG = pygame.transform.scale2x(pygame.image.load("bg.png"))
CHERRY = pygame.transform.scale(pygame.image.load("cherry.png"), (24, 24))


def get_walls():
    with open("walls.txt", newline="") as file:
        lines = file.readlines()
        walls = []
        for line in lines:
            values = line.rstrip().split(", ")[:4]
            for x, value in enumerate(values):
                values[x] = int(value)
            walls.append(pygame.Rect(*values))
    return walls


def get_dots():
    with open("dots.txt", newline="") as file:
        lines = file.readlines()
        dots = []
        for line in lines:
            values = line.rstrip().split(", ")
            values[0], values[1] = int(values[0]), int(values[1])
            values[2] = bool(values[2])
            dots.append(values)
    return dots


walls = get_walls()

dots = get_dots()

cherry_pos = random.choice(dots)

pacman_pos = random.choice(dots)
while pacman_pos == cherry_pos:
    pacman_pos = random.choice(dots)
pacman_pos[2] = False


def check_dot_values(dots):
    for dot in dots:
        if dot[2]:
            return False
    return True


def redraw(win, dots, pacman, cherry_disp):
    win.blit(BG, (0, 0))
    for wall in walls:
        pygame.draw.rect(win, (255, 0, 0), wall)
    for dot in dots:
        if dot[2]:
            pygame.draw.circle(win, (255, 255, 255), dot[:2], 4)
    if cherry_disp:
        win.blit(CHERRY, (cherry_pos[0] - 12, cherry_pos[1] - 12))
    pacman.draw(win)
    pygame.display.flip()


def main():
    pacman = PacMan(*pacman_pos[:2], 32)
    while True:
        cherry_disp = check_dot_values(dots)
        collide_dot = pacman.update(W, H, [cherry_pos], walls) if cherry_disp else pacman.update(W, H, dots, walls)
        for dot in dots:
            if collide_dot and dot == collide_dot:
                dot[2] = False
        if cherry_disp and cherry_pos == collide_dot:
            return True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            pacman.move("left", walls)
        if keys[pygame.K_RIGHT]:
            pacman.move("right", walls)
        if keys[pygame.K_UP]:
            pacman.move("up", walls)
        if keys[pygame.K_DOWN]:
            pacman.move("down", walls)
        # pygame.event.pump()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT:
            #         pacman.move("left", walls)
            #     if event.key == pygame.K_RIGHT:
            #         pacman.move("right", walls)
            #     if event.key == pygame.K_UP:
            #         pacman.move("up", walls)
            #     if event.key == pygame.K_DOWN:
            #         pacman.move("down", walls)
            # if event.type == pygame.KEYUP and event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
            #     pacman.move("stopx", walls)
            # if event.type == pygame.KEYUP and event.key in [pygame.K_UP, pygame.K_DOWN]:
            #     pacman.move("stopy", walls)
        redraw(win, dots, pacman, cherry_disp)
        clock.tick(30)


if __name__ == '__main__':
    if main():
        print("You win!")
