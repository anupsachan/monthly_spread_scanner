def rule_1_call(prev, curr):
    if prev["Close"] < prev["Open"] and curr["Open"] < prev["Close"]:
        return "R1-CALL"
    return None


def rule_2_put(prev, curr):
    if prev["Close"] > prev["Open"] and curr["Open"] > prev["Close"]:
        return "R2-PUT"
    return None


RULES = [
    rule_1_call,
    rule_2_put
]