import string
from rule import Rule


class Puzzle:
    def __init__(self, n):
        self.n = n
        self.variables = string.ascii_uppercase[:n]
        self.rules = []

    def __str__(self):
        return "<Puzzle: {n}, [\n  {rules}\n]>".format(
            n=self.n,
            rules=",\n  ".join(rule.__str__() for rule in self.rules)
        )

    def add_rule(self, rule_str=None, rule_structured=None):
        if rule_str is not None:
            self.rules.append(Rule(rule_raw=rule_str))
        else:
            self.rules.append(Rule(rule_structured=rule_structured))

    def add_rules(self, rules_str=None, rules_structured=None):
        if rules_str is not None:
            for rule_str in rules_str:
                self.add_rule(rule_str=rule_str)
        else:
            for rule_structured in rules_structured:
                self.add_rule(rule_structured=rule_structured)
