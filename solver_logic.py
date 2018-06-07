import copy
from collections import defaultdict

from puzzle import Puzzle
from rule import Rule


def reduce_possible_values_by_rule(rule: Rule, possible_values):
    """
    reduce possible value sets according to a given rule
    for each variable in the rule and each value from its possible value set
    checks if it is actually viable to use that value considering all possible ways of other variables in the rule
    if a certain value is not viable, the value is removed from variable's possible value set
    """
    updated_possible_values = copy.deepcopy(possible_values)
    cont = True
    # repeat until not updated
    while cont:
        cont = False
        # fix a variable in the rule to investigate
        for var_fixed in rule.variables:
            # we will save verified possible values here
            var_fixed_new_possible_values = set()
            # fix a value for the variable from it possible value set
            for val_fixed in updated_possible_values[var_fixed]:
                # maintain set of used values (since values cannot be repeated) and chosen values for variables
                used_values, chosen_values = {val_fixed}, {var_fixed: val_fixed}

                # recursive function that looks for any valid variable-value assignment
                # to satisfy the rule with respect to the initial fixed variable-value pair
                def rec(ind):
                    # all variables are assigned, return whether they satisfy the rule
                    if ind == len(rule.variables):
                        return rule.eval_rule(chosen_values)
                    # assign the next variable
                    else:
                        var = rule.variables[ind]
                        # skip the fixed variable
                        if var == var_fixed:
                            return rec(ind + 1)
                        else:
                            # go through all values for var from its possible value set AND that are not already used
                            for val in updated_possible_values[var]:
                                if val not in used_values:
                                    # update used value and chosen value sets
                                    used_values.add(val)
                                    chosen_values[var] = val
                                    # go deeper
                                    ok = rec(ind + 1)
                                    # valid assignment has been found, don't look further
                                    if ok:
                                        return True
                                    # re-update used value and chosen value sets
                                    used_values.remove(val)
                                    del chosen_values[var]
                            # no assignment was successful here
                            return False

                # if assignment was found, add the fixed value to new possible value set for the fixed variable
                if rec(0):
                    var_fixed_new_possible_values.add(val_fixed)

            # break and repeat process if we had a successful update
            if var_fixed_new_possible_values != updated_possible_values[var_fixed]:
                cont = True
                updated_possible_values[var_fixed] = var_fixed_new_possible_values
                break
    # result
    updated = any(possible_values[var] != updated_possible_values[var] for var in possible_values.keys())
    return updated, updated_possible_values


def reduce_possible_values_by_naked_subset_strategy(possible_values):
    """
    reduce possible value sets by "naked subset" strategy
    i.e., if we have exactly N variables VARS of the same possible value sets VALS of size N,
    we don't know which of variable from VARS has which value from VALS,
    but we know that VALS are distributed among VARS in some way,
    hence we know that all other variables (not in VARS) will definitely NOT have values from VALS,
    so we can remove all occurrences of values from VALS from value possibilities of all variables not in VARS.
    """
    updated_possible_values = copy.deepcopy(possible_values)
    cont = True
    # repeat until not updated
    while cont:
        cont = False
        # build value subset to respective variables map
        subset_to_vars = defaultdict(list)
        for var, subset in updated_possible_values.items():
            subset_to_vars[tuple(sorted(list(subset)))].append(var)
        # try the strategy to all subsets
        for subset, vars_with_subset in subset_to_vars.items():
            # reduction happens if subset has the same number of values as the variables that have this subset
            if len(subset) == len(vars_with_subset):
                # set of variables to update
                # those that are outside `vars_with_subset`, but have values from the subset
                vars_to_update = [
                    var for var, vals in updated_possible_values.items()
                    if var not in vars_with_subset and set(vals) & set(subset)
                ]
                # if there are such variables, update their value sets
                for var in vars_to_update:
                    cont = True
                    updated_possible_values[var] -= set(subset)
            # break and repeat process if we had a successful update
            if cont:
                break
    # result
    updated = any(possible_values[var] != updated_possible_values[var] for var in possible_values.keys())
    return updated, updated_possible_values


def reduce_possible_values_by_hidden_subset_strategy(possible_values):
    """
    reduce possible value sets by "hidden subset" strategy
    i.e., if we have a set of N values VALS such that these values occur in exactly N variables VARS as possible values
    we know for sure that values from VALS are distributed among VARS in some way,
    hence we know that all other values from current possible value sets for variables in VARS
    will definitely NOT be assigned to them (variables in VARS),
    so we can remove all occurrences of values not from VALS from all variables in VARS.
    """
    updated_possible_values = copy.deepcopy(possible_values)
    cont = True
    # repeat until not updated
    while cont:
        cont = False
        # {value -> all variables that contain value in possible value set}
        val_to_vars = defaultdict(list)
        for var, vals in updated_possible_values.items():
            for val in vals:
                val_to_vars[val].append(var)
        # {variable set -> all values that are contained in exactly the variable set}
        var_subset_to_vals = defaultdict(list)
        for val, vars in val_to_vars.items():
            var_subset_to_vals[tuple(sorted(vars))].append(val)
        # try the strategy to the variable subsets
        for vars, vals in var_subset_to_vals.items():
            # if the subset of N variables matches exactly N values, try reduction
            if len(vars) == len(vals):
                # we update all the variables from `vars` that have more than just `vals` as possible value sets
                vars_to_update = [
                    var for var in vars
                    if set(updated_possible_values[var]) - set(vals)
                ]
                # set their possible values sets to `vals` (i.e., remove everything else)
                for var in vars_to_update:
                    cont = True
                    updated_possible_values[var] = set(vals)
            # break and repeat process if we had a successful update
            if cont:
                break
    # result
    updated = any(possible_values[var] != updated_possible_values[var] for var in possible_values.keys())
    return updated, updated_possible_values


def express_variable_from_rule(rule: Rule, variable):
    """
    try to express variable `variable` as an expression using the given rule
    e.g.: ( A+B=C , A ) => A=C-B )
    """
    # check current constraints for doing this
    if rule.rule["op"] != "=":
        raise Exception("should be =", rule)
    if rule.variable_counts[variable] != 1:
        raise Exception("should only be one occurrence", rule)

    opposite_ops = {
        "+": "-",
        "-": "+",
        "*": "/",
        "/": "*",
    }

    # checks if variable `var` is present in given expression
    def expression_has_var(expression, var):
        if "value" in expression:
            return expression.get("value") == var
        else:
            return expression_has_var(expression["lhs"], var) or expression_has_var(expression["rhs"], var)

    # given "expression_reducable = expression_result" with variable `var` in `expression_reducable`
    # obtain either "var = expression_result"
    # or reduced "expression_reducable = expression_result" with variable `var` in `expression_reducable`
    # (reduced in the sense of depth of `expression_reducable`
    def rec(expression_reducable, expression_result, var):
        # we have reached the last level: expression_reducable = {"value": var}
        if "value" in expression_reducable:
            return expression_reducable, expression_result
        else:
            lhs_has_var = expression_has_var(expression_reducable["lhs"], var)
            # if expression_reducable's LHS has var, apply RHS to expression_result with inverted operation
            # e.g.: LHS + RHS = res => LHS = res - RHS
            if lhs_has_var:
                new_expression_reducable = expression_reducable["lhs"]
                new_expression_result = {
                    "op": opposite_ops[expression_reducable["op"]],
                    "lhs": expression_result,
                    "rhs": expression_reducable["rhs"],
                }
            # expression_reducable's RHS has var
            else:
                # if operation is + or *, apply LHS to expression_result with inverted operation
                # e.g.: LHS + RHS = res => RHS = res - LHS
                if expression_reducable["op"] in ["+", "*"]:
                    new_expression_reducable = expression_reducable["rhs"]
                    new_expression_result = {
                        "op": opposite_ops[expression_reducable["op"]],
                        "lhs": expression_result,
                        "rhs": expression_reducable["lhs"],
                    }
                # if operation is - or /, apply expression_result to LHS with same operation
                # and move RHS (with var) to the other side (virtually, since w)
                # e.g.: LHS - RHS = res => LHS - res = RHS => RHS = LHS - res
                else:
                    new_expression_reducable = expression_reducable["rhs"]
                    new_expression_result = {
                        "op": expression_reducable["op"],
                        "lhs": expression_reducable["lhs"],
                        "rhs": expression_result,
                    }
            # go deeper
            return rec(new_expression_reducable, new_expression_result, var)

    new_rule = Rule(rule_structured=copy.deepcopy(rule.rule))
    # swap lhs and rhs to guarantee given variable on the left hand side
    if expression_has_var(new_rule.rule["rhs"], variable):
        new_rule.rule["lhs"], new_rule.rule["rhs"] = new_rule.rule["rhs"], new_rule.rule["lhs"]
    # update rule's lhs and rhs
    new_rule.rule["lhs"], new_rule.rule["rhs"] = rec(new_rule.rule["lhs"], new_rule.rule["rhs"], variable)
    # result
    return new_rule


def apply_variable_expression(rule: Rule, var_expression: Rule):
    """
    given a rule `rule` and a variable `var` expression `var_expression`
    replace all occurrences of `var` in `rule` with its expression from `var_expressions`
    e.g.: ( A+B=C , B=D+1 ) => A+D+1=C
    """
    # recursive replace function
    def replace_var_rec(expression, replace_var, replace_with):
        if "value" in expression:
            if expression["value"] == replace_var:
                return replace_with
            else:
                return expression
        else:
            return {
                "op": expression["op"],
                "lhs": replace_var_rec(expression["lhs"], replace_var, replace_with),
                "rhs": replace_var_rec(expression["rhs"], replace_var, replace_with),
            }

    # copy the rule, replace recursively, return new rule
    rule_structured = copy.deepcopy(rule.rule)
    replace_var, replace_with = var_expression.rule["lhs"]["value"], var_expression.rule["rhs"]
    rule_structured = replace_var_rec(rule_structured, replace_var, replace_with)
    return Rule(rule_structured=rule_structured)


class LogicBasedSolver:
    def __init__(self, puzzle: Puzzle, verbose=False):
        self.puzzle = puzzle
        self.verbose = verbose
        self.possible_values = {
            variable: set(range(1, self.puzzle.n+1))
            for variable in self.puzzle.variables
        }
        self.rules = []
        self.rule_hashes = set()
        for rule in self.puzzle.rules:
            self.add_new_rule(rule)
        self.variable_expressions = {
            variable: set()
            for variable in self.puzzle.variables
        }

    def add_new_rule(self, rule: Rule):
        """
        add new rule if it is not already present
        """
        h = rule.__hash__()
        if h not in self.rule_hashes:
            self.rules.append(rule)
            self.rule_hashes.add(h)

    def solve(self, max_steps=None):
        steps = 0
        while True:
            steps += 1
            self.reduce_possible_values()
            if all(len(vals) == 1 for vals in self.possible_values.values()):
                print("we are done")
                print(self.possible_values)
                return True
            if max_steps is not None and steps == max_steps:
                print("fail")
                return False
            self.try_expressing_variables()
            self.try_applying_variable_expressions()
            # print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # print(self.possible_values)
            # print(len(self.rules), len(self.variable_expressions))

    def reduce_possible_values(self):
        """
        reduce possible value sets by various methods
        """
        cont = True
        # try until not updated
        while cont:
            cont = False
            # try reducing by rules
            for rule in self.rules:
                updated, updated_possible_values = reduce_possible_values_by_rule(rule, self.possible_values)
                if updated:
                    if self.verbose:
                        print("reduced by rule:", rule, ",", self.possible_values, "==>", updated_possible_values)
                    self.possible_values = updated_possible_values
                    cont = True
                    break
            # try reducing by naked subset strategy
            updated, updated_possible_values = reduce_possible_values_by_naked_subset_strategy(self.possible_values)
            if updated:
                if self.verbose:
                    print("reduced by naked subset strategy:", self.possible_values, "==>", updated_possible_values)
                self.possible_values = updated_possible_values
                cont = True
            # try reducing by hidden subset strategy
            updated, updated_possible_values = reduce_possible_values_by_hidden_subset_strategy(self.possible_values)
            if updated:
                if self.verbose:
                    print("reduced by hidden subset strategy:", self.possible_values, "==>", updated_possible_values)
                self.possible_values = updated_possible_values
                cont = True

    def try_expressing_variables(self):
        """
        go through all rules and try to express each variable
        """
        for rule in self.rules:
            if rule.rule["op"] != "=":
                continue
            for var, cnt in rule.variable_counts.items():
                if cnt != 1:
                    continue
                new_expression = express_variable_from_rule(rule, var)
                if new_expression is not None:
                    if self.verbose:
                        print("new variable expression:", rule, ",", var, "==>", new_expression)
                    self.variable_expressions[var].add(new_expression)

    def try_applying_variable_expressions(self):
        """
        go through all rules and try to apply each variable expression to generate new rules
        :return: 
        """
        new_rules = []
        for rule in self.rules:
            for var in rule.variables:
                for var_expression in self.variable_expressions[var]:
                    new_rule = apply_variable_expression(rule, var_expression)
                    if self.verbose:
                        print("new rule:", rule, ",", var_expression, "==>", new_rule)
                    new_rules.append(new_rule)
        for new_rule in new_rules:
            self.add_new_rule(new_rule)


if __name__ == "__main__":
    # puzzle = Puzzle(7)
    # puzzle.add_rules([
    #     "B+G=D",
    #     "B+C=A",
    #     "C+E+G=F",
    #     "D<A=>C=2",
    #     "D>A=>E=2",
    # ])
    # puzzle = Puzzle(6)
    # puzzle.add_rules([
    #     "D + 2 = E",
    #     "F + 1 = B",
    #     "B + 2 = C",
    #     "D + F < A"
    # ])
    puzzle = Puzzle(6)
    puzzle.add_rules([
        "D - E = A",
        "2B = F + 7",
        "D + A = C",
    ])
    lbs = LogicBasedSolver(puzzle, verbose=True)
    lbs.solve(4)
