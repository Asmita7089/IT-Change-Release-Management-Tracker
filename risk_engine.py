def calculate_risk(impact, likelihood):
    score = impact * likelihood

    if score <= 4:
        level = "Low"
    elif score <= 9:
        level = "Medium"
    else:
        level = "High"

    return score, level