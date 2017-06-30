from npuzzle import next_states
import pickle
import generator


if __name__ == '__main__':
    size = 3
    depth_max = 2
    goal = generator.make_goal(size)
    opened = [[goal, []]]
    closed = opened

    depth = 0
    redundants = {'U': [], 'D': [], 'R': [], 'L': []}
    while depth < depth_max:
        print(depth)
        next_opened = []
        for state in opened:
            next_opened += sorted(next_states(state, size, redundants),
                                  key=lambda x: x[1])
        for state in next_opened:
            for close in closed:
                if state[0] == close[0]:
                    next_opened.remove(state)
                    redundants[state[1][-1]].append(state[1][:-1])
                    break
            closed.append(state)
        opened = next_opened
        depth += 1
    with open('redundant_move.txt', mode='wb') as f:
        pickle.dump(redundants, f)
