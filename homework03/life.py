import pygame
import random
from pygame.locals import *
from copy import deepcopy

class GameOfLife:
    def __init__(self, width = 640, height = 480, cell_size = 10, speed = 3):
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

    def draw_grid(self):
        # http://www.pygame.org/docs/ref/draw.html#pygame.draw.line
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                (0, y), (self.width, y))

    def run(self):
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))
        running = True
        self.clist = self.cell_list(randomize=True)
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.draw_cell_list(self.clist)
            self.draw_grid()
            pygame.display.flip()
            clock.tick(self.speed)
            self.clist = self.update_cell_list(self.clist)
        pygame.quit()

    def cell_list(self, randomize=True):
        clist = []
        if randomize:
            for i in range(self.cell_height):
                clist += [[random.randint(0, 1) for j in range(self.cell_width)]]
        else:
            for i in range(self.cell_height):
                clist += [[0 for j in range(self.cell_width)]]
        return clist


    def draw_cell_list(self, clist):
        x, y = 0, 0
        for i in range(self.cell_height):
            for j in range(self.cell_width):
                if clist[i][j] == 0:
                    pygame.draw.rect(self.screen, pygame.Color('white'), (x, y, self.cell_size, self.cell_size))
                else:
                    pygame.draw.rect(self.screen, pygame.Color('green'), (x, y, self.cell_size, self.cell_size))
                if ((x + self.cell_size)//self.cell_size) == self.cell_width:
                    x = 0
                    y += self.cell_size
                else:
                    x += self.cell_size

    def get_neighbours(self, cell):
        pos = []    # pos - координаты соседних клеток
        neighbours = []
        i, j = cell
        tmp = ()
        for m in range(i - 1, i + 2):
            for n in range(j - 1, j + 2):
                if m == i and n == j:
                    pass
                else:
                    if 0 <= m <= self.cell_height-1 and 0 <= n <= self.cell_width-1:
                        tmp += (m, n)
                        pos.append(tmp)
                        tmp = ()
        for k in pos:
            neighbours.append(self.clist[k[0]][k[1]])
        return neighbours

    def update_cell_list(self, clist):
        updated_clist = self.cell_list(randomize=False)
        for i in range(len(clist)):
            for j in range(len(clist[i])):
                neighbours = self.get_neighbours((i, j))
                alive = sum(neighbours)
                if clist[i][j] == 1:
                    if not (alive == 2 or alive == 3):
                        updated_clist[i][j] = 0
                    else:
                        updated_clist[i][j] = 1
                else:
                    if alive == 3:
                        updated_clist[i][j] = 1
                    else:
                        updated_clist[i][j] = 0
        return updated_clist



if __name__ == '__main__':
    game = GameOfLife(320, 240, 20)
    game.run()

