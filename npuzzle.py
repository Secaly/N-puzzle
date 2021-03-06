import pickle
import itertools
import generator
import argparse


MOVE = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
FILE = 'redundant_move_7_12.txt'


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
            values = itertools.product(puzzle_1d[:puzzle_1d.index(value)],
                                       goal_1d[goal_1d.index(value):]):
            for prev_value, next_value in values:
                if prev_value == next_value:
                    n += 1
        except ValueError:
            raise NPuzzleError('invalid file')

    x_puzzle, y_puzzle = find_number(puzzle, size, 0)
    x_goal, y_goal = find_number(goal, size, 0)

    if n % 2 == ((abs(x_puzzle - x_goal) + abs(y_puzzle - y_goal)) % 2):
        return True

    return False


def find_number(puzzle, size, number):
    for x, y in itertools.product(range(size), repeat=2):
        if puzzle[x][y] == number:
            break

    return x, y


def euclidian_distance_change(puzzle, move, goal, size):
    x0, y0 = find_number(puzzle, size, 0)
    x0_goal, y0_goal = find_number(goal, size, 0)
    dist_0_cur = ((x0 - x0_goal) ** 2 + (y0 - y0_goal) ** 2) ** 0.5
    dist_0_next = ((x0 - move[0] - x0_goal) ** 2 +
                   (y0 - move[1] - y0_goal) ** 2) ** 0.5

    number = puzzle[x0 - move[0]][y0 - move[1]]
    xnumber_goal, ynumber_goal = find_number(goal, size, number)
    dist_number_cur = ((x0 - move[0] - xnumber_goal) ** 2 +
                       (y0 - move[1] - ynumber_goal) ** 2) ** 0.5
    dist_number_next = ((x0 - xnumber_goal) ** 2 +
                        (y0 - ynumber_goal) ** 2) ** 0.5

    return -(dist_0_next - dist_0_cur + dist_number_next - dist_number_cur)


def euclidian_distance(puzzle, goal, size):
    distance = 0
    for x, y in itertools.product(range(size), repeat=2):
        x_puzzle, y_puzzle = find_number(puzzle, size, goal[x][y])
        distance += ((x - x_puzzle) ** 2 + (y - y_puzzle) ** 2) ** 0.5

    return distance


def manhattan_distance_change(puzzle, move, goal, size):
    x0, y0 = find_number(puzzle, size, 0)
    x0_goal, y0_goal = find_number(goal, size, 0)
    dist_0_cur = abs(x0 - x0_goal) + abs(y0 - y0_goal)
    dist_0_next = abs(x0 - move[0] - x0_goal) + abs(y0 - move[1] - y0_goal)

    number = puzzle[x0 - move[0]][y0 - move[1]]
    xnumber_goal, ynumber_goal = find_number(goal, size, number)
    dist_number_cur = (
        abs(x0 - move[0] - xnumber_goal) + abs(y0 - move[1] - ynumber_goal)
    dist_number_next = abs(x0 - xnumber_goal) + abs(y0 - ynumber_goal)

    return -(dist_0_next - dist_0_cur + dist_number_next - dist_number_cur)


def manhattan_distance(puzzle, goal, size):
    distance = 0
    for x, y in itertools.product(range(size), repeat=2):
        x_puzzle, y_puzzle = find_number(puzzle, size, goal[x][y])
        distance += abs(x - x_puzzle) + abs(y - y_puzzle)

    return distance


def row_column_distance_change(puzzle, move, goal, size):
    distance_change = 0

    x0_puzzle, y0_puzzle = find_number(puzzle, size, 0)
    xn_puzzle, yn_puzzle = x0_puzzle - move[0], y0_puzzle - move[1]

    x0_goal = int(size / 2) if size % 2 else int((size + 1) / 2)
    y0_goal = int(size / 2)
    xn_goal, yn_goal = find_number(goal, size, puzzle[xn_puzzle][yn_puzzle])

    if (x0_puzzle == x0_goal) and (xn_puzzle != x0_goal):
        distance_change -= 1
    if (xn_puzzle == xn_goal) and (x0_puzzle != xn_goal):
        distance_change -= 1
    if (x0_puzzle != x0_goal) and (xn_puzzle == x0_goal):
        distance_change += 1
    if (xn_puzzle != xn_goal) and (x0_puzzle == xn_goal):
        distance_change += 1

    if (y0_puzzle == y0_goal) and (yn_puzzle != y0_goal):
        distance_change -= 1
    if (yn_puzzle == yn_goal) and (y0_puzzle != yn_goal):
        distance_change -= 1
    if (y0_puzzle != y0_goal) and (yn_puzzle == y0_goal):
        distance_change += 1
    if (yn_puzzle != yn_goal) and (y0_puzzle == yn_goal):
        distance_change += 1

    return distance_change


def row_column_distance(puzzle, goal, size):
    distance = 0

    for i in range(size):
        for j in range(size):
            if puzzle[i][j] not in goal[i]:
                distance += 1
            if puzzle[i][j] not in [goal[x][j] for x in range(size)]:
                distance += 1

    return distance


def hamming_distance_change(puzzle, move, goal, size):
    distance_change = 0
    x0, y0 = find_number(puzzle, size, 0)

    if goal[x0][y0] == 0:
        distance_change -= 1
    elif goal[x0 - move[0]][y0 - move[1]] == 0:
        distance_change += 1

    if goal[x0 - move[0]][y0 - move[1]] == puzzle[x0 - move[0]][y0 - move[1]]:
        distance_change -= 1
    elif goal[x0][y0] == puzzle[x0 - move[0]][y0 - move[1]]:
        distance_change += 1

    return distance_change


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


def astar(puzzle, goal, size, distance, distance_change):
    distance_init = distance(puzzle, goal, size)
    opened = [[puzzle, [], distance_init, distance_init]]
    closed = []
    number_opened = 1
    number_selected = 0
    with open(FILE, mode='rb') as f:
        redundants = pickle.load(f)

    while opened:
        opened.sort(key=lambda x: (x[2], len(x[1])))

        cur_state = opened.pop(0)
        number_selected += 1
        if cur_state[0] == goal:
            return cur_state[1], number_selected, number_opened

        closed.append(cur_state)
        for state in next_states(cur_state, size, redundants):
            state[2] += distance_change(state[0], MOVE[state[1][-1]], goal,
                                        size)
            state[3] = state[2] + len(state[1])
            opened.append(state)
            number_opened += 1


def join_path(state_start, state_end):
    reverse = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U'}
    for i in range(len(state_end)):
        state_start += reverse[state_end[-i - 1]]

    return state_start


def astar_bidirectionnal(puzzle, goal, size, distance, distance_change,                         greedy=True):

    distance_init = distance(puzzle, goal, size)
    opened_start = [[puzzle, [], distance_init, distance_init]]
    closed_start = []
    opened_end = [[goal, [], distance_init, distance_init]]
    closed_end = []
    number_opened = 2
    number_selected = 0
    with open(FILE, mode='rb') as f:
        redundants = pickle.load(f)

    while opened_start and opened_end:
        if greedy:
            opened_start.sort(key=lambda x: (x[2], len(x[1])))
            opened_end.sort(key=lambda x: (x[2], len(x[1])))
        else:
            opened_start.sort(key=lambda x: (len(x[1]), x[2]))
            opened_end.sort(key=lambda x: (len(x[1]), x[2]))

        cur_state_start = opened_start.pop(0)
        cur_state_end = opened_end.pop(0)
        number_selected += 2

        if cur_state_start[0] == goal:
            success = join_path(cur_state_start[1], [])
            break
        elif cur_state_end[0] == puzzle:
            success = join_path([], cur_state_end[1])
            break
        elif cur_state_start[0] == cur_state_end[0]:
            success = join_path(cur_state_start[1], cur_state_end[1])
            break

        end_join = [state for state in opened_end + closed_end
                    if cur_state_start[0] == state[0]]
        if end_join:
            success = join_path(cur_state_start[1], end_join[0][1])
            break

        start_join = [state for state in opened_start + closed_start
                      if cur_state_end[0] == state[0]]
        if start_join:
            success = join_path(start_join[0][1], cur_state_end[1])
            break

        closed_start.append(cur_state_start)
        for state in next_states(cur_state_start, size, redundants):
            state[2] += distance_change(state[0], MOVE[state[1][-1]], goal,
                                        size)
            state[3] = state[2] + len(state[1])
            opened_start.append(state)
            number_opened += 1

        closed_end.append(cur_state_end)
        for state in next_states(cur_state_end, size, redundants):
            state[2] += distance_change(state[0], MOVE[state[1][-1]], goal,
                                        size)
            state[3] = state[2] + len(state[1])
            opened_end.append(state)
            number_opened += 1

    return success, number_selected, number_opened


def read_args(args):
    if not args.file:
        puzzle = generator.make_puzzle(args.size)
        size = args.size
    else:
        puzzle = []
        size = 0
        try:
            with open(args.file, mode='r') as file_open:
                for line in file_open:
                    temp_array = []
                    line_split = line.split()
                    if len(puzzle) == size and size > 0 and (
                            line_split[0][0] != '#'):
                        raise NPuzzleError('Invalid data format')
                    if (len(line_split) > size and (
                            line_split[size][0] == '#') or (
                            line_split[0][0] == '#') or (
                            len(line_split) == size) or (
                            len(line_split) == 1 and size == 0) or (
                            size == 0 and len(line_split) > 1 and
                            line_split[1][0] == '#')):
                        if line_split[0][0] == '#':
                            continue
                        if size == 0:
                            size = int(line_split[0])
                        elif size > 0:
                            for array in range(0, size):
                                try:
                                    temp_array.append(int(line_split[array]))
                                except ValueError:
                                    raise NPuzzleError('Invalid value in the puzzle')
                            puzzle.append(temp_array)
                    else:
                        raise NPuzzleError('Unexpected error')
        except OSError:
            raise NPuzzleError('Fail to open the file')

    return(puzzle, size)


def print_result(result):
    path, number_selected, number_opened = result

    print('Number of path opened :')
    print(number_opened)
    print('Number of path selected :')
    print(number_selected)
    print('Length of the path :')
    print(len(path))
    print('Path :')
    print(path)


def main():

    """
    usage: npuzzle.py [-h] [-f [FILE] | -s [SIZE]] [-H heuristic] [-a algorithm]
    """

    parser = argparse.ArgumentParser(description='Choose your heuristic.',
                                     epilog='(´・ω・`)')

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-f', '--file', nargs='?',
        help='read a specific file and not a random generated map')
    group.add_argument(
        '-s', '--size', nargs='?', type=int, default=3,
        help='change the size of the random generated map (default: 3)')
    parser.add_argument(
        '-H', '--heuristic', metavar='heuristic', default='manhattan',
        choices=['manhattan', 'row-column', 'euclidian'],
        help='manhattan | row-column | euclidian (default: manhattan)')
    parser.add_argument(
        '-a', '--algorithm', metavar='algorithm', default='greedy',
        choices=['uniform-cost', 'greedy', 'both'],
        help='uniform-cost | greedy | both (default: greedy)')

    args = parser.parse_args()

    puzzle, size = read_args(args)

    goal = generator.make_goal(size)

    """
    puzzle example = [[5, 6, 7],
                      [4, 0, 8],
                      [3, 2, 1]]
    """

    print('Initiale puzzle :')
    [print(puzzle[i]) for i in range(size)]

    if args.heuristic == 'manhattan':
        distance = manhattan_distance
        distance_change = manhattan_distance_change
    elif args.heuristic == 'row-column':
        distance = row_column_distance
        distance_change = row_column_distance_change
    elif args.heuristic == 'euclidian':
        distance = euclidian_distance
        distance_change = euclidian_distance_change

    if is_solvable(puzzle, goal, size):
        if args.algorithm in ['uniform-cost', 'both']:
            print_result(astar_bidirectionnal(
                puzzle, goal, size, distance, distance_change, False))
        if args.algorithm in ['greedy', 'both']:
            print_result(astar_bidirectionnal(
                puzzle, goal, size, distance, distance_change))
    else:
        print('Puzzle not solvable.')


if __name__ == '__main__':
    main()
