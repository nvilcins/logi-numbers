import os

from generator import BasicGenerator
from puzzle import Puzzle
from rule import Rule
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
    print("define rule from string")
    rule = Rule("A+BC=D-2E+11<=>F>G")
    print(rule)
    print()

    print("define rule with 'structured rule'")
    rule = Rule(rule_structured={
        "op": "!=",
        "lhs": {
            "value": "A",
        },
        "rhs": {
            "value": 2,
        }
    })
    print(rule)
    print()

    print("define puzzle (n=5) with a set of string rules")
    puzzle = Puzzle(5)
    puzzle.add_rules(rules_str=[
        "B+A=6",
        "E+B=C",
        "E+C+B=8",
    ])
    print(puzzle)
    print()

    print("solve the puzzle by brute force")
    bfs = BruteForceSolver(puzzle)
    cnt, solution = bfs.solve()
    print("number of solutions:", cnt)
    print("solution:", solution)
    print()

    print("define a puzzle with non-unique solution, solve by brute force")
    puzzle2 = Puzzle(5)
    puzzle2.add_rules(rules_str=[
        "E+B=C",
        "E+C+B=8",
    ])
    bfs = BruteForceSolver(puzzle2)
    cnt, _ = bfs.solve()
    print("number of solutions:", cnt)
    print()

    print("solve the puzzle by logic")
    lbs = LogicBasedSolver(puzzle, verbose=False)
    solved, possible_values = lbs.solve()
    print("solved by logic?:", solved)
    print("possible values after reduction (here it's  solution):", possible_values)
    print()

    print("see how far logical solver reduces the partial puzzle")
    lbs = LogicBasedSolver(puzzle2, verbose=False)
    # have to limit max number of steps or it will run forever on partial puzzles
    solved, possible_values = lbs.solve(max_steps=4)
    print("solved by logic?:", solved)
    print("possible values after reduction:", possible_values)
    print()

    print("generate a puzzle")
    bg = BasicGenerator(5, seed=2018, verbose=False)
    puzzle_generated = bg.generate()
    print(puzzle_generated)
    print()

    print("verify it has a unique solution with brute force")
    bfs = BruteForceSolver(puzzle_generated)
    cnt, solution = bfs.solve()
    print("number of solutions:", cnt)
    print("solution:", solution)
    print()

    print("check if it really is logically solvable")
    lbs = LogicBasedSolver(puzzle_generated, verbose=False)
    solved, possible_values = lbs.solve()
    print("solved by logic?:", solved)
    print("possible values after reduction (here it's  solution):", possible_values)
    print()

    input_files = [
        "input5x5.txt",
        "input6x6.txt",
        "input7x7.txt",
        "input8x8.txt",
    ]

    # print("go through all inputs and try to solve by brute force")
    # for input_file in input_files:
    #     print(input_file, ":")
    #     puzzles_raw = read_input(os.path.join(os.path.dirname(os.path.relpath(__file__)), "data", input_file))
    #     for puzzle_raw in puzzles_raw:
    #         puzzle = Puzzle(puzzle_raw["n"])
    #         puzzle.add_rules(rules_str=puzzle_raw["rules"])
    #         bfs = BruteForceSolver(puzzle)
    #         cnt, solution = bfs.solve()
    #         assert cnt == 1
    #         print(puzzle)
    #         print("solution:", solution)

    # print("go through all inputs and try to solve by logic")
    # print("(limit max number of steps, count successful and failed solves)")
    # for input_file in input_files:
    #     print(input_file, ":")
    #     successes, fails = 0, 0
    #     puzzles_raw = read_input(os.path.join(os.path.dirname(os.path.relpath(__file__)), "data", input_file))
    #     for puzzle_raw in puzzles_raw:
    #         puzzle = Puzzle(puzzle_raw["n"])
    #         puzzle.add_rules(rules_str=puzzle_raw["rules"])
    #         lbs = LogicBasedSolver(puzzle, verbose=False)
    #         success, _ = lbs.solve(max_steps=4)
    #         if success:
    #             successes += 1
    #         else:
    #             fails += 1
    #     print("  succeeded:", successes)
    #     print("  failed:", fails)
