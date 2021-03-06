import random
import string

from puzzle import Puzzle
from rule import Rule
from solver_brute import BruteForceSolver
from solver_logic import LogicBasedSolver


WEIGHT_PRESETS = {
    "easy": {
        "var_num": [5, 1],  # choice between variable and numerical value
        "val_exp": [3, 1],  # choice between value (variable/number) and expression
        "add_mul": [3, 1],  # choice between addition (or subtraction) and multiplication
        "eq_ineq": [1, 0],  # choice between equalities (=) and inequalities (!=, >, <)
        "logic_eq": [0, 1],  # choice between logical expressions (if-then/iff) and equation/inequality
    },
    "medium": {
        "var_num": [5, 1],
        "val_exp": [4, 2],
        "add_mul": [4, 2],
        "eq_ineq": [3, 1],
        "logic_eq": [0, 1],
    },
    "hard": {
        "var_num": [5, 1],
        "val_exp": [4, 2],
        "add_mul": [4, 2],
        "eq_ineq": [3, 1],
        "logic_eq": [2, 10],
    },
}

# initialize RNG object so that sympy doesn't mess with our seed
rng = random.Random()


# uniformly random number from interval
def ri(a, b):
    return rng.randint(a, b)


# uniformly random element from array a
def sample(a):
    return a[ri(0, len(a)-1)]


# random array index according to (integer) weights
def choice(weights):
    x = ri(1, sum(weights))
    s = 0
    for i, w in enumerate(weights):
        s += w
        if s >= x:
            return i


class BasicGenerator:
    def __init__(self, n, seed=None, verbose=False, custom_weights=None):
        self.n = n
        self.variables = string.ascii_uppercase[:self.n]
        self.values = None
        if seed is not None:
            rng.seed(seed)
        self.verbose = verbose
        self.number_range = [1, self.n + 2]
        # weights for random sampling
        self.weights = WEIGHT_PRESETS["easy"] if custom_weights is None else custom_weights

    def get_random_rule(self):
        """
        generate random rule according to weight definition
        """
        # get random expression
        # can specify a subset of allowed operations `ops`
        def rec_get_expression(ops=None):
            # decide whether to get a value (variable or number)
            if choice(self.weights["val_exp"]) == 0:
                # decide whether to get a variable
                if choice(self.weights["var_num"]) == 0:
                    value = sample(self.variables)
                # get number
                else:
                    value = ri(*self.number_range)
                return {
                    "value": value
                }
            # get deeper expression
            else:
                # choose operation
                if ops is not None:
                    op = sample(ops)
                elif choice(self.weights["add_mul"]) == 0:
                    op = sample(["+", "-"] if ops is None else ops)
                else:
                    op = "*"
                # if we have multiplication here, only allow multiplication further to avoid bracketing
                ops_next = ["*"] if op == "*" else None
                return {
                    "op": op,
                    "lhs": rec_get_expression(ops=ops_next),
                    "rhs": rec_get_expression(ops=ops_next),
                }

        # get random relation (>, <, =, or !=)
        def get_relation():
            # choose between equalities and inequalities
            if choice(self.weights["eq_ineq"]) == 0:
                op = "="
            else:
                op = sample([">", ">=", "!="])
            return {
                "op": op,
                "lhs": rec_get_expression(),
                "rhs": rec_get_expression(),
            }

        # decide whether to use logical operator
        if choice(self.weights["logic_eq"]) == 0:
            # generate logical operator with random expressions on both sides
            rule_structured = {
                "op": sample(["=>", "<=>"]),
                "lhs": get_relation(),
                "rhs": get_relation(),
            }
        else:
            # generate random relation
            rule_structured = get_relation()

        r = Rule(rule_structured=rule_structured)
        return r

    def get_random_rule_simple(self):
        """
        generate a simple random rule
        variable (+/-/*) variable (>/</=/!=) number
        """
        var1 = self.variables[ri(0, self.n - 1)]
        var2 = self.variables[ri(0, self.n - 1)]
        op1 = ["+", "-", "*", ][ri(0, 2)]
        lhs = {
            "op": op1,
            "lhs": {
                "value": var1,
            },
            "rhs": {
                "value": var2,
            },
        }
        val = ri(1, 10)
        rhs = {
            "value": val,
        }
        op0 = [">", "<", "=", "!=", ][ri(0, 3)]
        if op0 == "<":
            op0 = ">"
            lhs, rhs = rhs, lhs
        return Rule(rule_structured={
            "op": op0,
            "lhs": lhs,
            "rhs": rhs,
        })

    def get_solution_count(self, puzzle):
        """
        get the number of solutions to given (partial) puzzle
        """
        # first do 3 steps of logical solver, to (hopefully) greatly reduce search space
        lbs = LogicBasedSolver(puzzle)
        _, possible_values = lbs.solve(max_steps=2)
        # then apply brute force to check all possible assignments (after logical reductions)
        bfs = BruteForceSolver(puzzle)
        cnt, _ = bfs.solve(possible_values=possible_values)
        # return the number of solutions
        return cnt

    def reduce_until_unique(self, puzzle):
        """
        generate and add new random rules until we have a unique solution
        """
        cnt = self.get_solution_count(puzzle)
        while True:
            # add new random rule
            random_rule = self.get_random_rule()
            # skip rule if not ok or if it is in form "A=1"
            if not random_rule.is_ok() or (len(random_rule.variables) == 1 and random_rule.rule["op"] == "="):
                continue
            puzzle.rules.append(random_rule)
            # get the new number of solutions
            cnt_new = self.get_solution_count(puzzle)
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
                cnt = self.get_solution_count(puzzle)
                if cnt == 1:
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
            ok, _ = lbs.solve(4)
            if ok:
                if self.verbose:
                    print("puzzle successful")
                return puzzle
            elif self.verbose:
                print("puzzle unsuccessful")

if __name__ == "__main__":
    # bg = BasicGenerator(7, seed=2019, verbose=True)
    # puzzle = bg.generate()
    # print(puzzle)
    bg = BasicGenerator(6, seed=2019, verbose=True, custom_weights=WEIGHT_PRESETS["easy"])
    for i in range(10):
        puzzle = bg.generate()
        print(puzzle)
