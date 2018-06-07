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

    val, op, lhs_str, rhs_str = None, None, None, None

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

    # +/- operation
    elif "+" in rule_str or "-" in rule_str:
        # index of last +/- operator
        ind = len(rule_str) - 1 - [x in ["+", "-"] for x in rule_str][::-1].index(True)
        op = rule_str[ind]
        lhs_str, rhs_str = rule_str[:ind], rule_str[ind+1:]

    # value (number or a single variable)
    elif rule_str.isnumeric():
        val = int(rule_str)
    elif rule_str.isalpha() and len(rule_str) == 1:
        val = rule_str

    # implicit multiplication
    else:
        # first value is variable
        if rule_str[0].isalpha():
            op = "*"
            lhs_str, rhs_str = rule_str[:1], rule_str[1:]
        # first value is number
        else:
            first_letter = [x.isalpha() for x in rule_str].index(True)
            op = "*"
            lhs_str, rhs_str = rule_str[:first_letter], rule_str[first_letter:]

    # format result
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
