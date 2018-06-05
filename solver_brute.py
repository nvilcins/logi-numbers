from itertools import permutations
from puzzle import Puzzle


def eval_rule(rule, values):

    # check if-then / iff rule
    if rule["op"] in ["=>", "<=>"]:
        lhs_ok, rhs_ok = eval_rule(rule["lhs"], values), eval_rule(rule["rhs"], values)
        if rule["op"] == "=>":
            return (lhs_ok and rhs_ok) or (not lhs_ok)
        if rule["op"] == "<=>":
            return (lhs_ok and rhs_ok) or (not lhs_ok and not rhs_ok)

    # calculate value of expression
    def get_val_rec(r):
        if "value" in r:
            if isinstance(r["value"], int):
                return r["value"]
            return values[r["value"]]
        lhs, rhs = get_val_rec(r["lhs"]), get_val_rec(r["rhs"])
        if r["op"] == "+":
            return lhs + rhs
        if r["op"] == "-":
            return lhs - rhs
        if r["op"] == "*":
            return lhs * rhs

    # get left and right hand side values, check if satisfies the rule
    lhs, rhs = get_val_rec(rule["lhs"]), get_val_rec(rule["rhs"])
    if rule["op"] == "=":
        return lhs == rhs
    if rule["op"] == ">":
        return lhs > rhs
    if rule["op"] == ">=":
        return lhs >= rhs
    if rule["op"] == "!=":
        return lhs != rhs

    # fail
    raise Exception("Failed to eval!", rule, values)


class BruteForceSolver:
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle

    def solve(self):
        cnt = 0
        for permutation in permutations(list(range(1, self.puzzle.n+1))):
            values = dict(zip(self.puzzle.variables, permutation))
            for rule in self.puzzle.rules:
                ok = eval_rule(rule, values)
                if not ok:
                    break
            else:
                # print(values)
                cnt += 1
        return cnt
