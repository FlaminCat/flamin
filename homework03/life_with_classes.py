mimport pygame
from pygame.locals import *
import random
from copy import deepcopy

class GameOfLife:

    def __init__(self, width=640, height=480, cell_size=10, speed=10):
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
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                    (x, 0), (x, self.height))
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color('black'),
                    (0, y), (self.width, y))

    def run(self):
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption('Game of Life')
        self.screen.fill(pygame.Color('white'))

        # Создание списка клеток
        self.clist = CellList(self.cell_width, self.cell_height, randomize=True)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
            self.draw_grid()

            # Отрисовка списка клеток
            # Выполнение одного шага игры (обновление состояния ячеек)
            for a in range(len(self.clist.clist)):
                for b in range(len(self.clist.clist[0])):
                    if self.clist.clist[a][b].is_alive() == 0:
                        pygame.draw.rect(self.screen, pygame.Color('white'), (a*self.cell_size+1, b*self.cell_size+1, self.cell_size-1, self.cell_size-1))
                    else:
                        pygame.draw.rect(self.screen, pygame.Color('green'), (a*self.cell_size+1, b*self.cell_size+1, self.cell_size-1, self.cell_size-1))
            self.clist.update()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


class Cell:

    def __init__(self, row, col, state=0):
        self.row = row
        self.col = col
        self.state = state

    def is_alive(self):
        return self.state

    def __str__(self):
        return str(int(self.state))

    def __repr__(self):
        return self.__str__()


class CellList:

    def __init__(self, nrows, ncols, randomize=False, grid=[]):
        self.nrows = nrows
        self.ncols = ncols
        if not grid:
            if randomize:
                self.clist = [[Cell(r, c, random.randint(0,1)) for c in range(ncols)] for r in range(nrows)]
            else:
                self.clist = [[Cell(r, c, 0) for c in range(ncols)] for r in range(nrows)]
        else:
            self.clist = grid

    def get_neighbours(self, cell):
        neighbours = []
        for row in range(cell.row - 1, cell.row + 2):
            for col in range(cell.col - 1, cell.col + 2):
                if row != -1 and row != len(self.clist) and col != -1 and col != len(self.clist[0]):
                    if (row, col) != (cell.row, cell.col):
                        neighbours.append(self.clist[row][col])
        return neighbours

    def update(self):
        new_clist = [[Cell(r, c, 0) for c in range(self.ncols)] for r in range(self.nrows)]
        for i in range(len(self.clist)):
            for j in range(len(self.clist[i])):
                l = 0
                neighbours = self.get_neighbours(self.clist[i][j])
                neighbours = [neighbours[k].is_alive() for k in range(len(neighbours))]
                for a in range(len(neighbours)):
                    if neighbours[a] == 1:
                        l = l + 1
                if self.clist[i][j].is_alive() == 1:
                    if l in {2, 3}:
                        new_clist[i][j] = Cell(i, j, 1)
                else:
                    if l == 3:
                        new_clist[i][j] = Cell(i, j, 1)
        self.clist = new_clist[:]
        return self

    def __iter__(self):
        self.max = [self.nrows - 1, self.ncols - 1]
        self.curr = [0, 0]
        return self

    def __next__(self):
        cell_coor = self.curr[:]
        if self.curr[0] > self.max[0]:
            raise StopIteration
        self.curr[1] += 1
        if self.curr[1] > self.max[1]:
            self.curr[0] += 1
            self.curr[1] = 0
        return self.clist[cell_coor[0]][cell_coor[1]]

    def __str__(self):
        b = ''
        for i in range(len(self.clist)):
            a = ''
            for j in range(len(self.clist[i])):
                a += str(self.clist[i][j].state) + ' '
            if i != len(self.clist) - 1:
                a += '\n'
            b += a
        return str(b)

    @classmethod
    def from_file(cls, filename):
        grid = []
        with open(filename) as f:
            for nrow, line in enumerate(f):
                row = [Cell(nrow, ncol, int(state)) for ncol, state in enumerate(line) if state in "01"]
                grid.append(row)
        return cls(len(grid), len(grid[0]), randomize=False, grid=grid)


if __name__ == '__main__':
    game = GameOfLife(320, 240, 20)
    game.run()