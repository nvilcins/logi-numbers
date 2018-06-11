def raw_to_structured_rule(rule_str):
    """
    parses raw rule string into structured rule
    example input `rule_str`:
        "A+B>4"
    example result:
        {
          "op": ">",
          "lhs": {
            "op": "+",
            "lhs": {
              "value": "A",
            },
            "rhs": {
              "value": "B",
            }
          },
          "rhs": {
            "value": 4
          }
        }
    """
    # remove spaces and capitalize
    rule_str = rule_str.replace(" ", "").upper()

    val, op, lhs_str, rhs_str, full_str = None, None, None, None, None

    # if-then / if and only if rules
    if "<=>" in rule_str:
        op = "<=>"
        lhs_str, rhs_str = rule_str.split("<=>")
    elif "=>" in rule_str:
        op = "=>"
        lhs_str, rhs_str = rule_str.split("=>")

    # equation / inequality
    elif ">=" in rule_str:
        op = ">="
        lhs_str, rhs_str = rule_str.split(">=")
    elif "<=" in rule_str:
        op = ">="
        rhs_str, lhs_str = rule_str.split("<=")
    elif "!=" in rule_str:
        op = "!="
        rhs_str, lhs_str = rule_str.split("!=")
    elif "=" in rule_str:
        op = "="
        lhs_str, rhs_str = rule_str.split("=")
    elif ">" in rule_str:
        op = ">"
        lhs_str, rhs_str = rule_str.split(">")
    elif "<" in rule_str:
        op = ">"
        rhs_str, lhs_str = rule_str.split("<")

    # value (number or a single variable)
    elif rule_str.isnumeric():
        val = int(rule_str)
    elif rule_str.isalpha() and len(rule_str) == 1:
        val = rule_str

    # implicit multiplication
    elif rule_str.isalnum():
        # first value is variable
        if rule_str[0].isalpha():
            op = "*"
            lhs_str, rhs_str = rule_str[:1], rule_str[1:]
        # first value is number
        else:
            first_letter = [x.isalpha() for x in rule_str].index(True)
            op = "*"
            lhs_str, rhs_str = rule_str[:first_letter], rule_str[first_letter:]

    # parse complex expression (containing brackets and/or explicit operations)
    else:
        # split expression into sub-expressions, that are connected with +/-/*//
        sub_expressions, ops, op_inds = [], [], []
        # is first sub-expression with minus sign
        neg = rule_str[0] == "-"
        ind = 1 if neg else 0
        while ind < len(rule_str):
            # handle sub-expression in brackets (e.g., "(A+B)")
            if rule_str[ind] == "(":
                sub_expression = ""
                x = 0
                for ch in rule_str[ind:]:
                    sub_expression += ch
                    if ch == ")":
                        x += 1
                    if ch == "(":
                        x -= 1
                    ind += 1
                    if x == 0:
                        break
                sub_expressions.append(sub_expression[1:-1])
            # handle alphanumeric block (e.g., "12AC")
            elif rule_str[ind].isalnum():
                sub_expression = ""
                while ind < len(rule_str) and rule_str[ind].isalnum():
                    sub_expression += rule_str[ind]
                    ind += 1
                sub_expressions.append(sub_expression)
            # if none of the above, get the operation
            elif rule_str[ind] in ["+", "-", "*", "/"]:
                ops.append(rule_str[ind])
                op_inds.append(ind)
                ind += 1

        # single sub-expression - recurse on it
        if len(sub_expressions) == 1:
            full_str = sub_expressions[0]
        # otherwise find the right-most, least-priority operator and split the expression there
        else:
            ind = None
            # first handle +/-
            if "+" in ops or "-" in ops:
                ind = len(ops) - 1 - [op in ["+", "-"] for op in ops][::-1].index(True)
            # if no +/-, get *//
            elif "*" in ops or "/" in ops:
                ind = len(ops) - 1 - [op in ["*", "/"] for op in ops][::-1].index(True)
            # get the op and split rule string at the op
            op = ops[ind]
            lhs_str = rule_str[:op_inds[ind]]
            rhs_str = rule_str[op_inds[ind]+1:]

        if neg:
            # "-X" => "0-X"
            if full_str is not None:
                op = "-"
                lhs_str = "0"
                rhs_str = full_str
                full_str = None
            # "-X+..." => "0-X+..."
            elif lhs_str is not None:
                lhs_str = "0" + lhs_str

    # format result
    if full_str is not None:
        return raw_to_structured_rule(full_str)
    if val is not None:
        return {
            "value": val,
        }
    elif op is not None:
        return {
            "op": op,
            "lhs": raw_to_structured_rule(lhs_str),
            "rhs": raw_to_structured_rule(rhs_str),
        }
    else:
        raise Exception("Failed to parse!", rule_str)


def structured_to_raw_rule(rule):
    """
    parses structured rul into raw rule string
    example input `rule`:
        {
          "op": ">",
          "lhs": {
            "op": "+",
            "lhs": {
              "value": "A",
            },
            "rhs": {
              "value": "B",
            }
          },
          "rhs": {
            "value": 4
          }
        }
    example result:
        "A+B>4"
    """
    if "value" in rule:
        return str(rule["value"])
    template = "{lhs} {op} {rhs}"
    if "value" not in rule["lhs"] and "value" not in rule["rhs"]:
        template = "({lhs}) {op} ({rhs})"
    elif "value" not in rule["lhs"]:
        template = "({lhs}) {op} {rhs}"
    elif "value" not in rule["rhs"]:
        template = "{lhs} {op} ({rhs})"
    return template.format(
        op=rule["op"],
        lhs=structured_to_raw_rule(rule["lhs"]),
        rhs=structured_to_raw_rule(rule["rhs"]),
    )


if __name__ == "__main__":
    import json
    rule_raw = "A+B>4"
    rule_structured = raw_to_structured_rule(rule_raw)
    print(json.dumps(rule_structured, indent=2))
    rule_raw = structured_to_raw_rule(rule_structured)
    rule_structured = {
        "op": ">",
        "lhs": {
            "op": "+",
            "lhs": {
                "value": "A",
            },
            "rhs": {
                "value": "B",
            },
        },
        "rhs": {
            "value": 4,
      },
    }
    print(rule_raw)
    rule_raw = "A+(BC-D)+D*E/F=F/G"
    rule_raw = "(F*((A+B)-(D+E)))/H=2"
    rule_raw = "-A+D=2"
    rule_structured = raw_to_structured_rule(rule_raw)
    print(json.dumps(rule_structured, indent=2))
