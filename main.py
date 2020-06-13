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
font = pygame.font.SysFont("banger", 30, True)

BG = pygame.transform.scale2x(pygame.image.load("bg.png"))
CHERRY = pygame.transform.scale(pygame.image.load("cherry.png"), (24, 24))


def get_rect_values(filename):
    with open(filename, newline="") as file:
        lines = file.readlines()
        for x, line in enumerate(lines):
            numbers = line.rstrip().split(", ")
            for y, number in enumerate(numbers):
                numbers[y] = int(number)
            lines[x] = numbers
    return lines


moveables = get_rect_values("rect_movement.txt")
dots = get_rect_values("rect_dots.txt")
rects = [[Rectangle(i * 16, j * 16, 16, moveables[j][i], dots[j][i]) for i in range(28)] for j in range(32)]

cherry_list = random.choice(rects)
cherry_pos = random.choice(cherry_list)

pacman_list = random.choice(rects)
pacman_pos = random.choice(pacman_list)
while not pacman_pos.is_moveable:
    pacman_pos = random.choice(pacman_list)

pacman = PacMan(pacman_pos.x + 8, pacman_pos.y + 8, rects)
ghosts = {
    "blinky": Blinky(188, 259, 24),
    "inky": Inky(212, 259, 24),
    "pinky": Pinky(236, 259, 24),
    "clyde": Clyde(260, 259, 24)
}

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
        win.blit(CHERRY, (cherry_pos.x, cherry_pos.y))
    pacman.draw(win)
    pygame.display.flip()


def start_screen():
    redraw(win, rects, pacman, ghosts, None)
    text = font.render("READY!", 1, (255, 0, 0))
    win.blit(text, (W // 2 - text.get_width() // 2, 288))
    pygame.display.flip()
    for i in range(150):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(30)


def end_screen(is_win):
    redraw(win, rects, pacman, ghosts, None)
    if is_win:
        text = font.render("YOU WIN!", 1, (255, 0, 0))
    else:
        text = font.render("YOU LOSE!", 1, (255, 0, 0))
    win.blit(text, (W // 2 - text.get_width() // 2, 288))
    pygame.display.flip()
    for i in range(150):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        clock.tick(30)


def main():
    while True:
        cherry_disp = check_rect_values(rects)
        collide_rect = pacman.update(W, H, rects.append([[cherry_pos]])) if cherry_disp else pacman.update(W, H, rects)
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
            pacman.move("left", rects)
        if keys[pygame.K_RIGHT]:
            pacman.move("right", rects)
        if keys[pygame.K_UP]:
            pacman.move("up", rects)
        if keys[pygame.K_DOWN]:
            pacman.move("down", rects)
        for ghost in ghosts.values():
            if ghost.move(W, H, rects, pacman, ghosts["blinky"]):
                return False
        redraw(win, rects, pacman, ghosts, cherry_disp)
        clock.tick(30)


if __name__ == '__main__':
    start_screen()
    if main():
        end_screen(True)
    else:
        end_screen(False)
