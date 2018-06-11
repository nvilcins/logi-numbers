from collections import defaultdict
import sympy

from helpers import raw_to_structured_rule, structured_to_raw_rule


class Rule:
    def __init__(self, rule_raw=None, rule_structured=None, is_variable_expression=False):
        assert rule_raw is not None or rule_structured is not None
        self.rule = raw_to_structured_rule(rule_raw) if rule_raw is not None else rule_structured
        # flag for variable expressions
        # used to maintain the form "X=..." as opposed to "...=0"
        self.is_variable_expression = is_variable_expression
        if self.is_variable_expression:
            assert "value" in self.rule["lhs"] and self.rule["lhs"]["value"].isalpha()
        self.variables, self.variable_counts = None, None
        self.update_rule_variables()
        # simplify after initialization
        self.simplify()

    def __str__(self):
        return "<Rule: {simplified}>" .format(simplified=self.get_simplified_str())

    def __hash__(self):
        """
        rough hash function to check for obvious duplicates
        """
        return hash(self.get_simplified_str())

    def is_ok(self):
        """
        couple of checks to avoid weird epressions
        """
        # check characteristics of overly complex expression
        simplified = self.get_simplified_str()
        if any(bad in simplified for bad in ["**", "EXP", "ZOO"]):
            return False
        # for logical operator rules check if both sides are ok
        if self.rule["op"] in ["=>", "<=>"]:
            rule_lhs = Rule(rule_structured=self.rule["lhs"])
            rule_rhs = Rule(rule_structured=self.rule["rhs"])
            return rule_lhs.is_ok() and rule_rhs.is_ok()
        else:
            # check if rule contains any variable
            if not self.variables:
                return False
        # is ok if didn't fail
        return True

    def get_simplified_str(self):
        """
        get the simplified version of the rule as string
        """
        # simplify an expression ("A+A-1" => "2A-1")
        def simplify_expression(expression):
            raw_tmp = structured_to_raw_rule(expression)
            raw_simple = str(sympy.expand(raw_tmp.lower())).upper()
            if raw_simple[:1] == "-":
                raw_simple = "0" + raw_simple
            return raw_simple.replace(" ", "").upper()

        # simplify a relation ("A+A-1>2" => "2A-3>0")
        def simplify_relation(relation):
            raw_simple = simplify_expression({
                "op": "-",
                "lhs": relation["lhs"],
                "rhs": relation["rhs"],
            })
            return raw_simple + relation["op"] + "0"

        # maintain lhs for variable expressions
        if self.is_variable_expression:
            simplified = "{var}={expr}".format(
                var=self.rule["lhs"]["value"],
                expr=simplify_expression(self.rule["rhs"]),
            )
        # handle logical operator rules
        elif self.rule["op"] in ["=>", "<=>"]:
            simplified = "{lhs}{op}{rhs}".format(
                lhs=simplify_relation(self.rule["lhs"]),
                op=self.rule["op"],
                rhs=simplify_relation(self.rule["rhs"]),
            )
        # all other rules
        else:
            simplified = "{rel}".format(
                rel=simplify_relation(self.rule),
            )

        return simplified

    def simplify(self):
        """
        simplify the rule
        """
        if not self.is_ok():
            return
        # get simplified string
        simplified = self.get_simplified_str()
        # initialize as new rule
        self.rule = raw_to_structured_rule(simplified)
        # update meta variables
        self.update_rule_variables()

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
            if lhs is None or rhs is None:
                return None
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
