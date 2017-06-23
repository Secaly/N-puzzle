import random
import itertools


def make_goal(size):
    puzzle = [[0 for x in range(size)] for y in range(size)]
    n = 1
    x_start = y_start = 0
    x_end = y_end = size - 1

    while n < size * size:
        for y in range(y_start, y_end + 1):
            puzzle[x_start][y] = n
            n += 1
        x_start += 1
        for x in range(x_start, x_end + 1):
            puzzle[x][y_end] = n
            n += 1
        y_end -= 1
        for y in range(y_end, y_start - 1, -1):
            puzzle[x_end][y] = n
            n += 1
        x_end -= 1
        for x in range(x_end, x_start - 1, -1):
            puzzle[x][y_start] = n
            n += 1
        y_start += 1
    if not size % 2:
        puzzle[x][y] = 0

    return puzzle


def make_puzzle(size, solvable=True):
    random.seed()
    puzzle = make_goal(size)
    for x, y in itertools.product(range(size), repeat=2):
        if puzzle[x][y] == 0:
            zero = (x, y)
            break

    for i in range(10000):
        possibilities = []
        if zero[0] != 0:
            possibilities.append((-1, 0))
        if zero[1] != 0:
            possibilities.append((0, -1))
        if zero[0] != size - 1:
            possibilities.append((1, 0))
        if zero[1] != size - 1:
            possibilities.append((0, 1))

        choice = random.choice(possibilities)
        puzzle[zero[0]][zero[1]] = puzzle[zero[0] + choice[0]][zero[1] +
                                                               choice[1]]
        puzzle[zero[0] + choice[0]][zero[1] + choice[1]] = 0
        zero = (zero[0] + choice[0], zero[1] + choice[1])

    if not solvable:
        if puzzle[0][0] == 0 or puzzle[0][1] == 0:
            puzzle[-1][-1], puzzle[-1][-2] = puzzle[-1][-2], puzzle[-1][-1]
        else:
            puzzle[0][0], puzzle[0][1] = puzzle[0][1], puzzle[0][0]

    return puzzle
