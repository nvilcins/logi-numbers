from collections import defaultdict

from helpers import raw_to_structured_rule, structured_to_raw_rule


class Rule:
    def __init__(self, rule_raw=None, rule_structured=None):
        assert rule_raw is not None or rule_structured is not None
        self.rule = raw_to_structured_rule(rule_raw) if rule_raw is not None else rule_structured
        self.variables, self.variable_counts = None, None
        self.update_rule_variables()

    def __str__(self):
        return "Rule: " + self.get_human_readable_rule()

    def __hash__(self):
        """
        rough hash function to check for obvious duplicates
        """
        return hash(self.get_human_readable_rule())

    def get_human_readable_rule(self):
        return structured_to_raw_rule(self.rule)

    def update_rule_variables(self):
        """
        find the set of variables in the rule and their numbers of occurrences 
        """
        def rec(rule, variables, counts):
            if "value" in rule:
                if isinstance(rule["value"], str):
                    variables.add(rule["value"])
                    counts[rule["value"]] += 1
            else:
                rec(rule["lhs"], variables, counts)
                rec(rule["rhs"], variables, counts)

        self.variables, self.variable_counts = set(), defaultdict(int)
        rec(self.rule, self.variables, self.variable_counts)
        self.variables = sorted(list(self.variables))

    def eval_rule(self, values):
        # sanity check
        assert all(var in values for var in self.variables)

        # calculate value of expression
        def get_val_rec(expression):
            if "value" in expression:
                if isinstance(expression["value"], int):
                    return expression["value"]
                return values[expression["value"]]
            lhs, rhs = get_val_rec(expression["lhs"]), get_val_rec(expression["rhs"])
            if expression["op"] == "+":
                return lhs + rhs
            if expression["op"] == "-":
                return lhs - rhs
            if expression["op"] == "*":
                return lhs * rhs
            if expression["op"] == "/":
                return lhs / rhs if lhs > 0 and lhs % rhs == 0 else None
            if expression["op"] == "=":
                return lhs == rhs
            if expression["op"] == "!=":
                return lhs != rhs
            if expression["op"] == ">":
                return lhs > rhs
            if expression["op"] == "<":
                return lhs < rhs
            if expression["op"] == ">=":
                return lhs >= rhs
            if expression["op"] == "<=":
                return lhs <= rhs

        # get left and right hand side values, check if satisfies the rule
        lhs, rhs = get_val_rec(self.rule["lhs"]), get_val_rec(self.rule["rhs"])
        if lhs is None or rhs is None:
            return False
        if self.rule["op"] == "=>":
            return (lhs and rhs) or (not lhs)
        if self.rule["op"] == "<=>":
            return (lhs and rhs) or (not lhs and not rhs)
        if self.rule["op"] == "=":
            return lhs == rhs
        if self.rule["op"] == ">":
            return lhs > rhs
        if self.rule["op"] == ">=":
            return lhs >= rhs
        if self.rule["op"] == "!=":
            return lhs != rhs

        # fail
        raise Exception("Failed to eval!", self.rule, values)
