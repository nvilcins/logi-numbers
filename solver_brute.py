from itertools import permutations
from puzzle import Puzzle


class BruteForceSolver:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def solve_full_search(self):
        """
        check all possible value assignments
        count the number of assignments that satisfy the puzzle
        also return one of the solutions
        """
        cnt, last_solution = 0, None
        for permutation in permutations(list(range(1, self.puzzle.n+1))):
            values = dict(zip(self.puzzle.variables, permutation))
            for rule in self.puzzle.rules:
                ok = rule.eval_rule(values)
                if not ok:
                    break
            else:
                cnt += 1
                last_solution = values
        return cnt, last_solution

    def solve(self, possible_values=None):
        """
        check all possible value assignments
        reduce search space if `possible_values` is given
        count the number of assignments that satisfy the puzzle
        also return one of the solutions
        """
        # `possible_values` not given, do full search
        if possible_values is None:
            return self.solve_full_search()

        # generates assignments recursively
        def rec_get_assignments(ind, assignment, used_vals, assignments):
            if ind == len(self.puzzle.variables):
                assignments.append({var: val for var, val in assignment.items()})
            else:
                var = self.puzzle.variables[ind]
                for val in possible_values[var]:
                    if val not in used_vals:
                        assignment[var] = val
                        used_vals.add(val)
                        rec_get_assignments(ind+1, assignment, used_vals, assignments)
                        used_vals.remove(val)
                        del assignment[var]

        # get all possible assignments
        assignments, assignment, used_vals = [], {}, set()
        rec_get_assignments(0, assignment, used_vals, assignments)

        # count how many of the assignments satisfy the puzzle
        cnt, last_solution = 0, None
        for values in assignments:
            for rule in self.puzzle.rules:
                ok = rule.eval_rule(values)
                if not ok:
                    break
            else:
                cnt += 1
                last_solution = values
        return cnt, last_solution


if __name__ == "__main__":
    puzzle = Puzzle(5)
    puzzle.add_rules([
        "B+A=6",
        "E+B=C",
        "E+C+B=8",
    ])
    bfs = BruteForceSolver(puzzle)
    cnt, _ = bfs.solve()
    cnt, _ = bfs.solve(possible_values={
        "A": {1, 2, 3, 4, 5},
        "B": {1, 2, 3},
        "C": {3, 4, 5},
        "D": {1, 2, 3, 4, 5},
        "E": {1, 2, 3},
    })
    print(cnt)
