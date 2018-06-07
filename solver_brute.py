from itertools import permutations
from puzzle import Puzzle


class BruteForceSolver:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def solve(self):
        cnt = 0
        for permutation in permutations(list(range(1, self.puzzle.n+1))):
            values = dict(zip(self.puzzle.variables, permutation))
            for rule in self.puzzle.rules:
                ok = rule.eval_rule(values)
                if not ok:
                    break
            else:
                cnt += 1
        return cnt
