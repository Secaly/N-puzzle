import sys
import copy
import itertools
import generator


MOVE = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


def array2d_to_array1d(array_2d, size):

    array_1d = []

    for x in range(size):
        for y in range(size):
            array_1d.append(array_2d[x][y])

    return(array_1d)


def is_solvable(puzzle, goal, size):

    puzzle_1d = array2d_to_array1d(puzzle, size)
    goal_1d = array2d_to_array1d(goal, size)

    n = 0

    for value in goal_1d:
        for prev_value, next_value \
                in itertools.product(puzzle_1d[:puzzle_1d.index(value)],
                                     goal_1d[goal_1d.index(value):]):
            if prev_value == next_value:
                n += 1

    x_puzzle, y_puzzle = find_number(puzzle, size, 0)
    x_goal, y_goal = find_number(goal, size, 0)

    print(n)

    if n % 2 == (abs(x_puzzle - x_goal) + abs(y_puzzle - y_goal)) % 2:
        print('ok')
        return True

    return False


def find_number(puzzle, size, number):
    for x, y in itertools.product(range(size), repeat=2):
        if puzzle[x][y] == number:
            break

    return x, y


def manhattan_distance(puzzle, goal, size):
    distance = 0
    for x, y in itertools.product(range(size), repeat=2):
        x_puzzle, y_puzzle = find_number(puzzle, size, goal[x][y])
        distance += abs(x - x_puzzle) + abs(y - y_puzzle)

    return distance


def hamming_distance(puzzle, goal, size):
    distance = 0
    for x, y in itertools.product(range(size), repeat=2):
        if puzzle[x][y] != goal[x][y]:
            distance += 1

    return distance


def move_piece(puzzle, x, y, move):

    new_puzzle = puzzle
    new_puzzle[x][y] = new_puzzle[x + move[0]][y + move[1]]
    new_puzzle[x + move[0]][y + move[1]] = 0

    return new_puzzle


def reliable_move(move_1, move_2):
    if not move_2 or \
            MOVE[move_1][0] + MOVE[move_2][0] != 0 or \
            MOVE[move_1][1] + MOVE[move_2][1] != 0:
        return True
    return False


def next_states(cur_state, size):
    x, y = find_number(cur_state[0], size, 0)
    last_move = ''
    if cur_state[1]:
        last_move = cur_state[1][-1]
    move_possible = []
    if x != 0 and reliable_move('U', last_move):
        move_possible.append('U')
    if y != 0 and reliable_move('L', last_move):
        move_possible.append('L')
    if x != size - 1 and reliable_move('D', last_move):
        move_possible.append('D')
    if y != size - 1 and reliable_move('R', last_move):
        move_possible.append('R')

    next_states = [[[[cur_state[0][x][y] for y in range(size)]
                    for x in range(size)],
                    [cur_move for cur_move in cur_state[1]] + [move]]
                   for move in move_possible]
    return [[move_piece(next_states[i][0], x, y, MOVE[next_states[i][1][-1]]),
             next_states[i][1]] for i in range(len(next_states))]


def state_already_view(state, distance, opened, closed):
    if distance in opened:
        for open_state in opened[distance]:
            if state[0] == open_state[0]:
                return True
    if state[0] in closed:
        return True
    return False


def astar_rec(opened, goal, size, depth_max=1, depth=0):
    print('depth:', depth, ", depth_max:", depth_max)
    print([(dis, puzz) for dis, puzz in list(opened.items())])
    print()
    if opened:
        cur_state = opened[min(opened)].pop(0)
    else:
        print('depth_max + 1')
        return None
        # astar_rec(, goal, size, depth_max + 1, 0)
    if not opened[min(opened)]:
        del(opened[min(opened)])
    if cur_state[0] == goal:
        return cur_state
    elif depth > depth_max:
        return astar_rec(opened, goal, size, depth_max, 0)
    else:
        next_opened = {}
        for state in next_states(cur_state, size):
            distance = manhattan_distance(state[0], goal, size)
            if distance in next_opened:
                next_opened[distance].append(state)
            else:
                next_opened[distance] = [state]
        return astar_rec(next_opened, goal, size, depth_max,
                         depth + 1)


def astar(puzzle, goal, size):
    opened = {manhattan_distance(puzzle, goal, size): [[puzzle, []]]}
    closed = []
    succes = None
    num_succes = 1

    while opened:
        if succes:
            return succes
            for distance in list(opened.keys()):
                i = 0
                while i < len(opened[distance]):
                    if len(succes[1]) < len(opened[distance][i][1]):
                        closed.append(opened[distance].pop(i)[0])
                    else:
                        i += 1
                if not opened[distance]:
                    del(opened[distance])

        if opened:
            cur_state = opened[min(opened)].pop(0)
            if not opened[min(opened)]:
                del(opened[min(opened)])
            if cur_state[0] == goal:
                succes = cur_state
                print(num_succes, len(succes[1]))
                num_succes += 1

            closed.append(cur_state[0])
            for state in next_states(cur_state, size):
                distance = manhattan_distance(state[0], goal, size)
                if state[0] == goal or not state_already_view(state, distance,
                                                              opened, closed):
                    if distance in opened:
                        opened[distance].append(state)
                    else:
                        opened[distance] = [state]
                else:
                    if len(state[1]) + distance > len(cur_state[1]) + \
                            1 + distance:
                        state[1] = cur_state[1] + state[-1]
                        if state[0] in closed:
                            closed.pop(state[0])
                            if distance in opened:
                                opened[distance].append(state)
                            else:
                                opened[distance] = [state]

    if succes:
        [print(succes[0][i]) for i in range(size)]
        print(succes[1])
        print(len(succes[1]))


if __name__ == '__main__':
    # sys.setrecursionlimit(1000000)
    size = 5
    goal = generator.make_goal(size)
    puzzle = generator.make_puzzle(size)
    # puzzle = [[4, 2, 1],
    #           [6, 0, 3],
    #           [8, 7, 5]]
    [print(puzzle[i]) for i in range(size)]
    print('manhattan:', manhattan_distance(puzzle, goal, size))
    # print(astar(puzzle, goal, size))
    print(astar_rec({manhattan_distance(puzzle, goal, size): [[puzzle, []]]},
                    goal, size))
