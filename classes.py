import math
from datetime import datetime

import pygame


class Rectangle:
    def __init__(self, x, y, width, is_moveable, has_dot):
        self.x = x
        self.y = y
        self.width = width
        self.is_moveable = is_moveable
        self.eaten = not has_dot
        self.is_powerpellet = True if self.y in (64, 384) and self.x in (16, 416) else False
        self.dot_width = 6 if self.is_powerpellet else 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.width)

    def draw(self, win):
        if not self.eaten:
            pygame.draw.circle(win, (255, 255, 255), (self.x + self.width // 2, self.y + self.width // 2),
                               self.dot_width)


class PacMan:
    pacman1 = pygame.transform.scale(pygame.image.load("pacman1.png"), (24, 24))
    pacman2 = pygame.transform.scale(pygame.image.load("pacman2.png"), (24, 24))
    pacman3 = pygame.transform.scale(pygame.image.load("pacman3.png"), (24, 24))
    imgs_left = [pacman1, pacman2, pacman3, pacman2]
    imgs_right = [pygame.transform.rotate(img, 180) for img in imgs_left]
    imgs_up = [pygame.transform.rotate(img, 270) for img in imgs_left]
    imgs_down = [pygame.transform.rotate(img, 90) for img in imgs_left]

    def __init__(self, x, y, rects):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x - 12, self.y - 12, 24, 24)
        self.imgs = self.imgs_right
        self.img = self.imgs[0]
        self.imgcnt = 0
        self.count = 0
        self.count_increment = 1
        self.dirchange = 2
        self.dirx = 0
        self.diry = 0
        self.sep = 3.5
        self.current_rect = self.collide(rects)

    def move(self, dirn, rects):
        if self.check_move(dirn, rects):
            if dirn == "left":
                self.dirx = - self.dirchange
                self.diry = 0
                self.imgs = self.imgs_left
            elif dirn == "right":
                self.dirx = self.dirchange
                self.diry = 0
                self.imgs = self.imgs_right
            elif dirn == "up":
                self.dirx = 0
                self.diry = - self.dirchange
                self.imgs = self.imgs_up
            elif dirn == "down":
                self.dirx = 0
                self.diry = self.dirchange
                self.imgs = self.imgs_down
            else:
                self.dirx = 0
                self.diry = 0

    def check_move(self, dirn, rects):
        if dirn == "left":
            point = (self.x - 2, self.y)
        elif dirn == "right":
            point = (self.x + 2, self.y)
        elif dirn == "up":
            point = (self.x, self.y - 2)
        elif dirn == "down":
            point = (self.x, self.y + 2)
        else:
            return True
        for rect_list in rects:
            for rect_it in rect_list:
                new_rect = pygame.Rect(rect_it.rect.left - 2 * self.sep, rect_it.rect.top - 2 * self.sep,
                                       rect_it.rect.width + 4 * self.sep, rect_it.rect.width + 4 * self.sep)
                if new_rect.collidepoint(*point) and not rect_it.is_moveable:
                    return False
        return True

    def update(self, W, H, rects):
        self.update_movement(W, H, rects)
        self.update_imgs()
        return self.collide(rects)

    def update_imgs(self):
        self.imgcnt += 1
        if self.imgcnt > 15:
            self.imgcnt = 0
        self.img = self.imgs[self.imgcnt // 4]

    def update_movement(self, W, H, rects):
        self.count += 1
        if self.count % self.count_increment == 0:
            if (self.dirx < 0 and self.check_move("left", rects)) or (
                    self.dirx > 0 and self.check_move("right", rects)) or (
                    self.diry < 0 and self.check_move("up", rects)) or (
                    self.diry > 0 and self.check_move("down", rects)):
                self.x += self.dirx
                self.y += self.diry
        if self.x > W:
            self.x = 0
        if self.x < 0:
            self.x = W
        if self.y > H:
            self.y = 0
        if self.y < 0:
            self.y = H
        self.rect = pygame.Rect(self.x - 12, self.y - 12, 24, 24)

    def draw(self, win):
        win.blit(self.img, (self.x - 12, self.y - 12))

    def collide(self, rects):
        for rect_list in rects:
            for rect in rect_list:
                if rect.rect.collidepoint((self.x, self.y)):
                    self.current_rect = rect
                    return rect
        return None


class Ghost:
    imgs = [pygame.image.load("ghost.png")]
    boundaries = {
        "left": 188,
        "right": 284,
        "up": 235,
        "down": 283,
    }

    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        for x, img in enumerate(self.imgs):
            self.imgs[x] = pygame.transform.scale(img, (self.width, self.width))
        self.img = self.imgs[0]
        self.rect = pygame.Rect(self.x - 12, self.y - 12, self.width, self.width)
        self.current_rect = self.rect
        self.dirchange = 2
        self.dirx = 0
        self.diry = 0
        self.current_dirn = None
        self.wait_time = 20
        self.start_time = datetime.now()
        self.use_super = True
        self.sep = 3.5
        self.pacman_dead = False

    def move(self, W, H, rects, pacman, blinky):
        self.get_dirns(rects, pacman, blinky)
        if self.x > W:
            self.x = 0
        if self.x < 0:
            self.x = W
        if self.y > H:
            self.y = 0
        if self.y < 0:
            self.y = H
        self.x += self.dirx
        self.y += self.diry
        self.rect = pygame.Rect(self.x - 12, self.y - 12, self.width, self.width)
        self.pacman_dead = pacman.rect.collidepoint((self.x, self.y))
        return self.pacman_dead

    def get_dirns(self, rects, pacman, blinky):
        if self.x < self.boundaries["left"]:
            self.dirx = 0
            self.diry = - self.dirchange
        if self.x + self.width > self.boundaries["right"]:
            self.dirx = 0
            self.diry = self.dirchange
        if self.y < self.boundaries["up"]:
            self.dirx = self.dirchange
            self.diry = 0
        if self.y + self.width > self.boundaries["down"]:
            self.dirx = - self.dirchange
            self.diry = 0
        if self.rect.collidepoint(233, 223) and (datetime.now() - self.start_time).seconds > 0.5:
            self.dirx = 0
            self.diry = -1
            return False
        return True

    def check_move(self, dirn, rects):
        if dirn == "left":
            point = (self.x - 2, self.y)
        elif dirn == "right":
            point = (self.x + 2, self.y)
        elif dirn == "up":
            point = (self.x, self.y - 2)
        elif dirn == "down":
            point = (self.x, self.y + 2)
        else:
            return True
        for rect_list in rects:
            for rect_it in rect_list:
                new_rect = pygame.Rect(rect_it.rect.left - 2 * self.sep, rect_it.rect.top - 2 * self.sep,
                                       rect_it.rect.width + 4 * self.sep, rect_it.rect.width + 4 * self.sep)
                if new_rect.collidepoint(*point) and not rect_it.is_moveable:
                    return False
        return True

    def get_list_of_dirns(self, rects):
        if self.dirx:
            if self.dirx > 1:
                dirn = "left"
            else:
                dirn = "right"
        elif self.diry:
            if self.diry > 1:
                dirn = "up"
            else:
                dirn = "down"
        else:
            dirn = None
        dirns = ["up", "left", "down", "right"]
        if dirn:
            index = dirns.index(dirn)
            dirns.pop(index)
        dirns = {dirn: self.check_move(dirn, rects) for dirn in dirns}
        return dirns

    def draw(self, win):
        win.blit(self.img, (self.x - 12, self.y - 12))

    def collide(self, rects):
        for rect_list in rects:
            for rect in rect_list:
                if rect.rect.collidepoint((self.x, self.y)):
                    self.current_rect = rect
                    return rect
        return None


class Blinky(Ghost):
    imgs = [pygame.image.load("ghost.png"),
            pygame.image.load("blinky.png")]

    def __init__(self, x, y, width):
        super().__init__(x, y, width)
        self.img = self.imgs[1]
        self.dirx = - self.dirchange
        self.diry = 0

    def get_dirns(self, rects, pacman, blinky):
        if self.use_super:
            self.use_super = super().get_dirns(rects, pacman, blinky)
        else:
            dirns = self.get_list_of_dirns(rects)
            distances = {}
            for dirn, val in dirns.items():
                if val == True:
                    new_pos = (self.x - 16, self.y) if dirn == "left" else (
                        (self.x + 16, self.y) if dirn == "right" else (
                            (self.x, self.y - 16) if dirn == "up" else (self.x, self.y + 16)))
                    x_sep = abs(new_pos[0] - pacman.x)
                    y_sep = abs(new_pos[1] - pacman.y)
                    distances[dirn] = math.sqrt(x_sep + y_sep)
            min_dist = None
            min_dirn = None
            for dirn, distance in distances.items():
                if not min_dist:
                    min_dist = distance
                    min_dirn = dirn
                elif distance < min_dist:
                    min_dist = distance
                    min_dirn = dirn

            if min_dirn == "left":
                self.dirx = - self.dirchange
                self.diry = 0
            elif min_dirn == "right":
                self.dirx = self.dirchange
                self.diry = 0
            elif min_dirn == "up":
                self.dirx = 0
                self.diry = - self.dirchange
            elif min_dirn == "down":
                self.dirx = 0
                self.diry = self.dirchange


class Pinky(Ghost):
    imgs = [pygame.image.load("ghost.png"),
            pygame.image.load("pinky.png")]

    def __init__(self, x, y, width):
        super().__init__(x, y, width)
        self.img = self.imgs[1]
        self.dirx = -1

    def get_dirns(self, rects, pacman, blinky):
        if self.use_super:
            self.use_super = super().get_dirns(rects, pacman, blinky)
        else:
            dirns = self.get_list_of_dirns(rects)
            distances = {}
            for dirn, val in dirns.items():
                if val == True:
                    new_pos = (self.x - 16, self.y) if dirn == "left" else (
                        (self.x + 16, self.y) if dirn == "right" else (
                            (self.x, self.y - 16) if dirn == "up" else (self.x, self.y + 16)))
                    current_dirn = "left" if pacman.dirx < 0 else ("right" if pacman.dirx > 0 else (
                        "up" if pacman.diry < 0 else ("down" if pacman.diry > 0 else "up")))
                    if current_dirn == "left":
                        target_x = pacman.x - 64
                        target_y = pacman.y
                    elif current_dirn == "right":
                        target_x = pacman.x + 64
                        target_y = pacman.y
                    elif current_dirn == "up":
                        target_x = pacman.x
                        target_y = pacman.y - 64
                    elif current_dirn == "down":
                        target_x = pacman.x
                        target_y = pacman.y + 64
                    x_sep = abs(new_pos[0] - target_x)
                    y_sep = abs(new_pos[1] - target_y)
                    distances[dirn] = math.sqrt(x_sep + y_sep)
            min_dist = None
            min_dirn = None
            for dirn, distance in distances.items():
                if not min_dist:
                    min_dist = distance
                    min_dirn = dirn
                elif distance < min_dist:
                    min_dist = distance
                    min_dirn = dirn

            if min_dirn == "left":
                self.dirx = - self.dirchange
                self.diry = 0
            elif min_dirn == "right":
                self.dirx = self.dirchange
                self.diry = 0
            elif min_dirn == "up":
                self.dirx = 0
                self.diry = - self.dirchange
            elif min_dirn == "down":
                self.dirx = 0
                self.diry = self.dirchange


class Inky(Ghost):
    imgs = [pygame.image.load("ghost.png"),
            pygame.image.load("inky.png")]

    def __init__(self, x, y, width):
        super().__init__(x, y, width)
        self.img = self.imgs[1]
        self.dirx = -1

    def get_dirns(self, rects, pacman, blinky):
        if self.use_super:
            self.use_super = super().get_dirns(rects, pacman, blinky)
        else:
            dirns = self.get_list_of_dirns(rects)
            distances = {}
            for dirn, val in dirns.items():
                if val == True:
                    new_pos = (self.x - 16, self.y) if dirn == "left" else (
                        (self.x + 16, self.y) if dirn == "right" else (
                            (self.x, self.y - 16) if dirn == "up" else (self.x, self.y + 16)))
                    current_dirn = "left" if pacman.dirx < 0 else ("right" if pacman.dirx > 0 else (
                        "up" if pacman.diry < 0 else ("down" if pacman.diry > 0 else "up")))
                    if current_dirn == "left":
                        target_x = pacman.x - 64
                        target_y = pacman.y
                    elif current_dirn == "right":
                        target_x = pacman.x + 64
                        target_y = pacman.y
                    elif current_dirn == "up":
                        target_x = pacman.x
                        target_y = pacman.y - 64
                    elif current_dirn == "down":
                        target_x = pacman.x
                        target_y = pacman.y + 64
                    x_sep = abs(new_pos[0] - target_x)
                    y_sep = abs(new_pos[1] - target_y)
                    distances[dirn] = math.sqrt(x_sep + y_sep)
            min_dist = None
            min_dirn = None
            for dirn, distance in distances.items():
                if not min_dist:
                    min_dist = distance
                    min_dirn = dirn
                elif distance < min_dist:
                    min_dist = distance
                    min_dirn = dirn

            if min_dirn == "left":
                self.dirx = - self.dirchange
                self.diry = 0
            elif min_dirn == "right":
                self.dirx = self.dirchange
                self.diry = 0
            elif min_dirn == "up":
                self.dirx = 0
                self.diry = - self.dirchange
            elif min_dirn == "down":
                self.dirx = 0
                self.diry = self.dirchange


class Clyde(Ghost):
    imgs = [pygame.image.load("ghost.png"),
            pygame.image.load("clyde.png")]

    def __init__(self, x, y, width):
        super().__init__(x, y, width)
        self.img = self.imgs[1]
        self.dirx = -1

    def get_dirns(self, rects, pacman, blinky):
        if self.use_super:
            self.use_super = super().get_dirns(rects, pacman, blinky)
        else:
            dirns = self.get_list_of_dirns(rects)
            distances = {}
            for dirn, val in dirns.items():
                if val == True:
                    current_x_sep = abs(self.x - pacman.x)
                    current_y_sep = abs(self.y - pacman.y)
                    if math.sqrt(current_x_sep + current_y_sep) < 8:
                        target_x = 8
                        target_y = 504
                    else:
                        target_x = pacman.x
                        target_y = pacman.y
                    new_pos = (self.x - 16, self.y) if dirn == "left" else (
                        (self.x + 16, self.y) if dirn == "right" else (
                            (self.x, self.y - 16) if dirn == "up" else (self.x, self.y + 16)))
                    x_sep = abs(new_pos[0] - target_x)
                    y_sep = abs(new_pos[1] - target_y)
                    distances[dirn] = math.sqrt(x_sep + y_sep)
            min_dist = None
            min_dirn = None
            for dirn, distance in distances.items():
                if not min_dist:
                    min_dist = distance
                    min_dirn = dirn
                elif distance < min_dist:
                    min_dist = distance
                    min_dirn = dirn

            if min_dirn == "left":
                self.dirx = - self.dirchange
                self.diry = 0
            elif min_dirn == "right":
                self.dirx = self.dirchange
                self.diry = 0
            elif min_dirn == "up":
                self.dirx = 0
                self.diry = - self.dirchange
            elif min_dirn == "down":
                self.dirx = 0
                self.diry = self.dirchange
