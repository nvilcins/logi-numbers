import random
import string

from puzzle import Puzzle
from rule import Rule
from solver_brute import BruteForceSolver
from solver_logic import LogicBasedSolver


class BasicGenerator:
    def __init__(self, n, seed=None, verbose=False):
        self.n = n
        self.variables = string.ascii_uppercase[:self.n]
        self.values = None
        if seed is not None:
            random.seed(seed)
        self.verbose = verbose

    def get_random_rule(self):
        """
        generate a random rule
        currently only a basic template
        """
        var1 = self.variables[random.randint(0, self.n - 1)]
        var2 = self.variables[random.randint(0, self.n - 1)]
        op1 = ["+", "-", "*", ][random.randint(0, 2)]
        lhs = {
            "op": op1,
            "lhs": {
                "value": var1,
            },
            "rhs": {
                "value": var2,
            },
        }
        val = random.randint(1, 10)
        rhs = {
            "value": val,
        }
        op0 = [">", "<", "=", "!=", ][random.randint(0, 3)]
        if op0 == "<":
            op0 = ">"
            lhs, rhs = rhs, lhs
        return Rule(rule_structured={
            "op": op0,
            "lhs": lhs,
            "rhs": rhs,
        })

    def reduce_until_unique(self, puzzle):
        """
        generate and add new random rules until we have a unique solution
        """
        bfs = BruteForceSolver(puzzle)
        cnt = bfs.solve()
        while True:
            # add new random rule
            puzzle.rules.append(self.get_random_rule())
            # get the new number of solutions
            cnt_new = bfs.solve()
            # unique solution - we are done
            if cnt_new == 1:
                break
            # either no solution or no reduction - drop the new rule
            elif cnt_new == 0 or cnt_new == cnt:
                del puzzle.rules[-1]
            # solution count reduced - update count and proceed
            else:
                cnt = cnt_new

    def drop_redundant_rules(self, puzzle):
        """
        drop redundant rules one by one
        (those that don't reduce solution count within the context of the other rules)
        """
        bfs = BruteForceSolver(puzzle)
        updated = True
        while updated:
            updated = False
            # rules backup
            rules_prev = puzzle.rules
            # go through all rules and try to drop it
            for i in range(len(puzzle.rules)):
                # drop the rule
                puzzle.rules = puzzle.rules[:i] + puzzle.rules[i+1:]
                # still unique solution - dropped rules was redundant
                if bfs.solve() == 1:
                    updated = True
                    break
            # no rule was redundant - apply the backup
            else:
                puzzle.rules = rules_prev

    def generate(self):
        # try generating forever, until successful
        while True:
            if self.verbose:
                print("generating puzzle..")
            # generate puzzle
            puzzle = Puzzle(self.n)
            self.reduce_until_unique(puzzle)
            self.drop_redundant_rules(puzzle)
            if self.verbose:
                print("puzzle generated")
                print(puzzle)
            # check if it is solvable by logic
            lbs = LogicBasedSolver(puzzle)
            if lbs.solve(4):
                if self.verbose:
                    print("puzzle successful")
                return puzzle
            elif self.verbose:
                print("puzzle unsuccessful")

if __name__ == "__main__":
    bg = BasicGenerator(7, seed=2019, verbose=True)
    puzzle = bg.generate()
    print(puzzle)
