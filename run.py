from puzzle import Puzzle
from solver_brute import BruteForceSolver
from solver_logic import LogicBasedSolver


def read_input(path):
    puzzles, puzzle = [], None
    fin = open(path, "r")
    for line in fin.readlines():
        line = line.strip()
        if line:
            if puzzle is None:
                n, k = [int(x) for x in line.split()]
                puzzle = {"n": n, "k": k, "rules": []}
            else:
                puzzle["rules"].append(line)
                if len(puzzle["rules"]) == puzzle["k"]:
                    puzzles.append(puzzle)
                    puzzle = None
    return puzzles


if __name__ == "__main__":
    import json
    puzzles_raw = read_input("data/input5x5.txt")
    solved, failed = 0, 0
    for puzzle_raw in puzzles_raw:
        print(json.dumps(puzzle_raw, indent=2))
        p = Puzzle(puzzle_raw["n"])
        p.add_rules(puzzle_raw["rules"])
        # bfs = BruteForceSolver(p)
        # cnt = bfs.solve()
        # print(cnt)
        # assert cnt == 1
        lbs = LogicBasedSolver(p)
        ok = lbs.solve(4)
        if ok:
            solved += 1
        else:
            failed += 1
    print(solved, failed)
