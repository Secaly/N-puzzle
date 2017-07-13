import pickle
import itertools
import generator
import sys
import argparse
import re

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
        try:
            for prev_value, next_value \
                    in itertools.product(puzzle_1d[:puzzle_1d.index(value)],
                                         goal_1d[goal_1d.index(value):]):
                if prev_value == next_value:
                    n += 1
        except ValueError:
            print('invalid file')
            exit(0)

    x_puzzle, y_puzzle = find_number(puzzle, size, 0)
    x_goal, y_goal = find_number(goal, size, 0)

    if n % 2 == (abs(x_puzzle - x_goal) + abs(y_puzzle - y_goal)) % 2:
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


def next_states(cur_state, size, redundants):
    x, y = find_number(cur_state[0], size, 0)

    move_possible = []
    if x != 0 and not [redundant for redundant in redundants['U']
                       if cur_state[1][-len(redundant):] == redundant]:
        move_possible.append('U')
    if y != 0 and not [redundant for redundant in redundants['L']
                       if cur_state[1][-len(redundant):] == redundant]:
        move_possible.append('L')
    if x != size - 1 and not [redundant for redundant in redundants['D']
                              if cur_state[1][-len(redundant):] == redundant]:
        move_possible.append('D')
    if y != size - 1 and not [redundant for redundant in redundants['R']
                              if cur_state[1][-len(redundant):] == redundant]:
        move_possible.append('R')

    next_states = [[[[cur_state[0][x][y] for y in range(size)]
                    for x in range(size)],
                    [cur_move for cur_move in cur_state[1]] + [move]]
                   for move in move_possible]
    return [[move_piece(next_states[i][0], x, y, MOVE[next_states[i][1][-1]]),
             next_states[i][1], cur_state[2], 0]
            for i in range(len(next_states))]


def distance_change(puzzle, move, goal, size):
    x0, y0 = find_number(puzzle, size, 0)
    x0_goal, y0_goal = find_number(goal, size, 0)
    dist_0_cur = abs(x0 - x0_goal) + abs(y0 - y0_goal)
    dist_0_next = abs(x0 - move[0] - x0_goal) + abs(y0 - move[1] - y0_goal)

    number = puzzle[x0 - move[0]][y0 - move[1]]
    xnumber_goal, ynumber_goal = find_number(goal, size, number)
    dist_number_cur = abs(x0 - move[0] - xnumber_goal) + \
        abs(y0 - move[1] - ynumber_goal)
    dist_number_next = abs(x0 - xnumber_goal) + abs(y0 - ynumber_goal)

    return -(dist_0_next - dist_0_cur + dist_number_next - dist_number_cur)


def astar(puzzle, goal, size, greedy=True):
    distance_init = manhattan_distance(puzzle, goal, size)
    opened = [[puzzle, [], distance_init / 2, distance_init / 2]]
    closed = []
    with open('redundant_move_7_12.txt', mode='rb') as f:
        redundants = pickle.load(f)

    while opened:
        if greedy:
            opened.sort(key=lambda x: (x[2], x[3]))
        else:
            opened.sort(key=lambda x: (x[3], x[2]))
        # [print(len(state[1]), state[1], state[2], state[3])
        #  for state in opened]
        # print()
        cur_state = opened.pop(0)
        if cur_state[0] == goal:
            return (cur_state)

        closed.append(cur_state)
        for state in next_states(cur_state, size, redundants):
            state[2] += distance_change(state[0], MOVE[state[1][-1]], goal,
                                        size) / 2
            state[3] = state[2] + len(state[1])
            opened.append(state)


def astar_rev(puzzle, goal, size, greedy=True):
    distance_init = manhattan_distance(puzzle, goal, size)
    opened_start = [[puzzle, [], distance_init / 2, distance_init / 2]]
    closed_start = []
    opened_end = [[goal, [], distance_init / 2, distance_init / 2]]
    closed_end = []
    with open('redundant_move_7_12.txt', mode='rb') as f:
        redundants = pickle.load(f)

    while opened_start and opened_end:
        if greedy:
            opened_start.sort(key=lambda x: (x[2], x[3]))
            opened_end.sort(key=lambda x: (x[2], x[3]))
        else:
            opened_start.sort(key=lambda x: (x[3], x[2]))
            opened_end.sort(key=lambda x: (x[3], x[2]))
        # [print(state) for state in opened_start]
        # print()
        # [print(state) for state in closed_start]
        # print()
        # [print(state) for state in opened_end]
        # print()
        # [print(state) for state in closed_end]
        # print()
        # print()
        cur_state_start = opened_start.pop(0)
        cur_state_end = opened_end.pop(0)
        if cur_state_start[0] == goal:
            print(cur_state_start)
            return 0
        elif cur_state_end[0] == puzzle:
            print(cur_state_end)
            return 0
        elif cur_state_start[0] == cur_state_end[0]:
            print(cur_state_start)
            print(cur_state_end)
            return 0

        end_join = [state for state in opened_end + closed_end
                    if cur_state_start[0] == state[0]]
        if end_join:
            print(cur_state_start)
            print(end_join[0])
            return 0

        start_join = [state for state in opened_start + closed_start
                      if cur_state_end[0] == state[0]]
        if start_join:
            print(start_join)
            print(cur_state_end)
            return 0

        closed_start.append(cur_state_start)
        for state in next_states(cur_state_start, size, redundants):
            state[2] += distance_change(state[0], MOVE[state[1][-1]], goal,
                                        size) / 2
            state[3] = state[2] + len(state[1])
            opened_start.append(state)

        closed_end.append(cur_state_end)
        for state in next_states(cur_state_end, size, redundants):
            state[2] += distance_change(state[0], MOVE[state[1][-1]], goal,
                                        size) / 2
            state[3] = state[2] + len(state[1])
            opened_end.append(state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Choose your heuristic.',
                                     epilog='(´・ω・`)')

    parser.add_argument('heuristic', metavar='Heuristic', choices=['Manhattan', 'Hamming', 'Heuristic3'],
                        help='Manhattan | Hamming | Heuristic3')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('--file', nargs='?',
                        help='read a specific file and not a random generated map')
    group.add_argument('--size', nargs='?', type=int, default=3,
                        help='change the size of the random generated map (default : 3)')
    parser.add_argument('algorithm', metavar='Algorithm', choices=['uniform-cost', 'greedy searches', 'both'],
                        help='uniform-cost | greedy searches | both')

    args = parser.parse_args()

    puzzle = []
    size = 0

    if not args.file:
        puzzle = generator.make_puzzle(args.size)
        size = args.size
    else:
        try:
            with open(args.file, mode='r') as file_open:
                for line in file_open:
                    temp_array = []
                    line_split = line.split()
                    if len(puzzle) == size and size > 0 and\
                        line_split[0][0] != '#':
                            print('invalid file 3')
                            exit(0)
                    if (len(line_split) > size and line_split[size][0] == '#') or\
                        line_split[0][0] == '#' or\
                        len(line_split) == size or\
                        (len(line_split) == 1 and size == 0) or\
                        (size == 0 and len(line_split) > 1 and\
                        line_split[1][0] == '#'):
                        if line_split[0][0] == '#':
                            continue
                        if size == 0:
                            size = int(line_split[0])
                        elif size > 0:
                            for array in range(0, size):
                                try:
                                    temp_array.append(int(line_split[array]))
                                except ValueError:
                                    print('invalid file 1')
                                    exit(0)
                            puzzle.append(temp_array)
                    else:
                        print('invalid file 2')
                        exit(0)
        except OSError:
            print('fail to open the file')
            exit(0)
    # puzzle = [[4, 1, 3],
    #           [0, 7, 5],
    #           [2, 8, 6]]
    # puzzle = [[4, 6, 8],
    #           [1, 0, 7],
    #           [2, 3, 5]]
    # puzzle = [[0, 5, 9, 7],
    #           [12, 15, 3, 6],
    #           [2, 4, 11, 13],
    #           [8, 1, 14, 10]]
    # puzzle = [[1, 2, 3, 4, 5],
    #           [16, 17, 22, 19, 6],
    #           [15, 20, 0, 24, 7],
    #           [14, 23, 18, 21, 8],
    #           [13, 12, 11, 10, 9]]
    goal = generator.make_goal(size)
    [print(puzzle[i]) for i in range(size)]
    print('manhattan:', manhattan_distance(puzzle, goal, size))
    if is_solvable(puzzle, goal, size):
        success = astar(puzzle, goal, size)
        print(len(success[1]), '\n', success[1])
        astar_rev(puzzle, goal, size, False)
    else:
        print('Puzzle not solvable.')
