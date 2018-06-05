import string
from helpers import raw_to_structured_rule


class Puzzle:
    def __init__(self, n):
        self.n = n
        self.variables = string.ascii_uppercase[:n]
        self.rules = []

    def add_rule(self, rule_str):
        self.rules.append(raw_to_structured_rule(rule_str))

    def add_rules(self, rules_str):
        for rule_str in rules_str:
            self.add_rule(rule_str)
