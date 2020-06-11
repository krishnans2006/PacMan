import random

import pygame

from classes import Rectangle, PacMan, Blinky, Pinky, Inky, Clyde

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


walls = get_walls()
rects = [[Rectangle(i * 16, j * 16, 16, True, True, False) for i in range(28)] for j in range(32)]

cherry_list = random.choice(rects)
cherry_pos = random.choice(cherry_list)

pacman_list = random.choice(rects)
pacman_pos = random.choice(pacman_list)
for i, rect_list in enumerate(rects):
    for j, rect in enumerate(rect_list):
        if rect == pacman_pos:
            rects[i][j].eaten = True


def check_rect_values(rects):
    for rect_list in rects:
        for rect in rect_list:
            if not rect.eaten:
                return False
    return True


def redraw(win, rects, pacman, ghosts, cherry_disp):
    win.blit(BG, (0, 0))
    for rect_list in rects:
        for rect in rect_list:
            rect.draw(win)
    for ghost in ghosts.values():
        ghost.draw(win)
    if cherry_disp:
        win.blit(CHERRY, (cherry_pos[0] - 12, cherry_pos[1] - 12))
    for wall in walls:
        pygame.draw.rect(win, (0, 255, 0), wall, 1)
    pacman.draw(win)
    pygame.display.flip()


def main():
    pacman = PacMan(pacman_pos.x + 8, pacman_pos.y + 8, rects)
    ghosts = {
        "blinky": Blinky(176, 247, 24),
        "inky": Inky(200, 247, 24),
        "pinky": Pinky(224, 247, 24),
        "clyde": Clyde(248, 247, 24)
    }
    while True:
        cherry_disp = check_rect_values(rects)
        collide_rect = pacman.update(W, H, [cherry_pos], walls) if cherry_disp else pacman.update(W, H, rects, walls)
        for i, rect_list in enumerate(rects):
            for j, rect in enumerate(rect_list):
                if collide_rect and rect == collide_rect:
                    rects[i][j].eaten = True
        if cherry_disp and cherry_pos == collide_rect:
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
        for ghost in ghosts.values():
            ghost.move()
        redraw(win, rects, pacman, ghosts, cherry_disp)
        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    if main():
        print("You win!")
