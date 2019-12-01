import random


def read_sudoku(filename):
    """ Прочитать Судоку из указанного файла """
    digits = [c for c in open(filename).read() if c in '123456789.']
    grid = group(digits, 9)
    return grid


def display(values):
    """Вывод Судоку """
    width = 2
    line = '+'.join(['-' * (width * 3)] * 3)
    for row in range(9):
        print(''.join(values[row][col].center(width) + ('|' if str(col) in '25' else '') for col in range(9)))
        if str(row) in '25':
            print(line)
    print()


def group(values, n):
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов
    >>> group([1,2,3,4], 2)
    [[1, 2], [3, 4]]
    >>> group([1,2,3,4,5,6,7,8,9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    tmp = []
    L = []
    for i in range(len(values)):
        if (i+1) % n == 0:
            tmp += [values[j] for j in range(i+1-n, i+1)]
            L += [tmp]
            tmp = []
    return L


def get_row(values, pos):
    """ Возвращает все значения для номера строки, указанной в pos
    >>> get_row([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '2', '.']
    >>> get_row([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (1, 0))
    ['4', '.', '6']
    >>> get_row([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (2, 0))
    ['.', '8', '9']
    """
    return values[pos[0]]


def get_col(values, pos):
    """ Возвращает все значения для номера столбца, указанного в pos
    >>> get_col([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '4', '7']
    >>> get_col([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (0, 1))
    ['2', '.', '8']
    >>> get_col([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (0, 2))
    ['3', '6', '9']
    """
    tmp = []
    tmp += [values[i][pos[1]] for i in range(len(values))]
    return tmp


def get_block(values, pos):
    """ Возвращает все значения из квадрата, в который попадает позиция pos
    >>> grid = read_sudoku('puzzle1.txt')
    >>> get_block(grid, (0, 1))
    ['5', '3', '.', '6', '.', '.', '.', '9', '8']
    >>> get_block(grid, (4, 7))
    ['.', '.', '3', '.', '.', '1', '.', '.', '6']
    >>> get_block(grid, (8, 8))
    ['2', '8', '.', '.', '.', '5', '.', '7', '9']
    """
    tmp = []
    begin_row = 0  # begin_row, begin_col - координаты первого элемента квадрата, в котором находится заданный элемент
    begin_col = 0
    for i in range(pos[0], -1, -1):
        if i % 3 == 0:
            begin_row = i
            break
    for j in range(pos[1], -1, -1):
        if j % 3 == 0:
            begin_col = j
            break
    tmp += [values[m][n] for m in range(begin_row, begin_row + 3) for n in range(begin_col, begin_col + 3)]
    return tmp


def find_empty_positions(grid):
    """ Найти первую свободную позицию в пазле
    >>> find_empty_positions([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']])
    (0, 2)
    >>> find_empty_positions([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']])
    (1, 1)
    >>> find_empty_positions([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']])
    (2, 0)
    """
    pos = ()
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == ".":
                pos = (i, j)
                return pos
            if i == len(grid)-1 and j == len(grid[0])-1:
                return pos


def find_possible_values(grid, pos):
    """ Вернуть множество возможных значения для указанной позиции
    >>> grid = read_sudoku('puzzle1.txt')
    >>> values = find_possible_values(grid, (0,2))
    >>> values == {'1', '2', '4'}
    True
    >>> values = find_possible_values(grid, (4,7))
    >>> values == {'2', '5', '9'}
    True
    """
    a = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    numbers = set(a)
    tmp = []
    for i in range(len(get_row(grid, pos))):
        if get_row(grid, pos)[i] != ".":
            tmp += get_row(grid, pos)[i]
    a1 = numbers - set(tmp)
    tmp = []
    for j in range(len(get_col(grid, pos))):
        if get_col(grid, pos)[j] != ".":
            tmp += get_col(grid, pos)[j]
    a2 = numbers - set(tmp)
    tmp = []
    for m in range(len(get_block(grid, pos))):
        if get_block(grid, pos)[m] != ".":
            tmp += get_block(grid, pos)[m]
    a3 = numbers - set(tmp)
    return a3.intersection(a1, a2)


def solve(grid):
    """ Решение пазла, заданного в grid """
    """ Как решать Судоку?
        1. Найти свободную позицию
        2. Найти все возможные значения, которые могут находиться на этой позиции
        3. Для каждого возможного значения:
            3.1. Поместить это значение на эту позицию
            3.2. Продолжить решать оставшуюся часть пазла
    >>> grid = read_sudoku('puzzle1.txt')
    >>> solve(grid)
    [['5', '3', '4', '6', '7', '8', '9', '1', '2'], ['6', '7', '2', '1', '9', '5', '3', '4', '8'], ['1', '9', '8', '3', '4', '2', '5', '6', '7'], ['8', '5', '9', '7', '6', '1', '4', '2', '3'], ['4', '2', '6', '8', '5', '3', '7', '9', '1'], ['7', '1', '3', '9', '2', '4', '8', '5', '6'], ['9', '6', '1', '5', '3', '7', '2', '8', '4'], ['2', '8', '7', '4', '1', '9', '6', '3', '5'], ['3', '4', '5', '2', '8', '6', '1', '7', '9']]
    """
    pos = find_empty_positions(grid)
    if pos == ():
        return grid
    else:
        values = find_possible_values(grid, pos)
        if values == {}:
            return None
        else:
            for v in values:
                grid[pos[0]][pos[1]] = str(v)
                solution = solve(grid)
                if solution is not None:
                    return grid
    grid[pos[0]][pos[1]] = '.'


def check_solution(solution):
    """ Если решение solution верно, то вернуть True, в противном случае False """
    # TODO: Add doctests with bad puzzles
    tmp = 0
    for i in range(9):
        for j in range(9):
            for k in get_row(solution, (i, 0)):
                if k == solution[i][j]:
                    tmp += 1
                if tmp > 1:
                    return False
            tmp = 0
    for i in range(9):
        for j in range(9):
            for m in get_col(solution, (0, j)):
                if m == solution[i][j]:
                    tmp += 1
                if tmp > 1:
                    return False
            tmp = 0
    for i in range(9):
        for j in range(9):
            for n in get_block(solution, (i, j)):
                if n == solution[i][j]:
                    tmp += 1
                if tmp > 1:
                    return False
            return True


def generate_sudoku(N):
    """ Генерация судоку заполненного на N элементов
    >>> grid = generate_sudoku(40)
    >>> sum(1 for row in grid for e in row if e == '.')
    41
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(1000)
    >>> sum(1 for row in grid for e in row if e == '.')
    0
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(0)
    >>> sum(1 for row in grid for e in row if e == '.')
    81
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    """
    s = []
    s += [['.', '.', '.', '.', '.', '.', '.', '.', '.'] for i in range(9)]
    solution = solve(s)
    k = 0
    while k != (81 - N):
        a = random.randint(0, 8)
        b = random.randint(0, 8)
        solution[a][b] = '.'
        k += 1
    return solution


if __name__ == '__main__':
    for fname in ['puzzle1.txt', 'puzzle2.txt', 'puzzle3.txt']:
        grid = read_sudoku(fname)
        display(grid)
        solution = solve(grid)
        display(solution)