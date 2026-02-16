def rule_1_call(prev, curr):
    """Bullish: Prev bearish, current opens below prev close."""
    if prev["Close"] < prev["Open"] and curr["Open"] < prev["Close"]:
        return "R1-CALL"
    return None

def rule_2_put(prev, curr):
    """Bearish: Prev bullish, current opens above prev close."""
    if prev["Close"] > prev["Open"] and curr["Open"] > prev["Close"]:
        return "R2-PUT"
    return None

RULES = [rule_1_call, rule_2_put]