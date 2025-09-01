import math

def percentile_rank(value, population):
    less = sum(1 for x in population if x < value)
    equal = sum(1 for x in population if x == value)
    return (less + 0.5 * equal) / len(population)

def streak_score(streak_days, tau):
    return 1 - math.exp(-streak_days / tau)

def get_tier(score):
    if score <= 250:
        return "Bronze"
    elif score <= 500:
        return "Amber"
    elif score <= 750:
        return "Ruby"
    else:
        return "Gold"

def compute_level_score(role, features, base_score, population_samples,
                        inactivity_days=0, inconsistent=False):
    if role == "driver":
        L = features["login_rate"]
        S = streak_score(features["streak_days"], 14)
        V = percentile_rank(features["rides_30d"], population_samples["rides_30d"])
        OT = percentile_rank(features["on_time_rate"], population_samples["on_time_rate"])
        CR = 1 - percentile_rank(features["cancellation_rate"], population_samples["cancellation_rate"])
        R = percentile_rank(features["rating"], population_samples["rating"])
        R_raw = 0.10*L + 0.10*S + 0.35*V + 0.20*OT + 0.15*CR + 0.10*R

    elif role == "delivery":
        L = features["login_rate"]
        S = streak_score(features["streak_days"], 14)
        V = percentile_rank(features["deliveries_30d"], population_samples["deliveries_30d"])
        OT = percentile_rank(features["on_time_rate"], population_samples["on_time_rate"])
        FD = 1 - percentile_rank(features["failed_deliveries_rate"], population_samples["failed_deliveries_rate"])
        AJ = percentile_rank(features["job_acceptance_rate"], population_samples["job_acceptance_rate"])
        R = percentile_rank(features["rating"], population_samples["rating"])
        R_raw = 0.10*L + 0.10*S + 0.30*V + 0.20*OT + 0.10*FD + 0.10*AJ + 0.10*R

    elif role == "merchant":
        L = features["login_rate"]
        S = streak_score(features["streak_days"], 21)
        V = percentile_rank(features["goods_sold_30d"], population_samples["goods_sold_30d"])
        F = percentile_rank(features["fulfilment_rate"], population_samples["fulfilment_rate"])
        REF = 1 - percentile_rank(features["refund_rate"], population_samples["refund_rate"])
        AOV = percentile_rank(features["avg_order_value"], population_samples["avg_order_value"])
        R = percentile_rank(features["rating"], population_samples["rating"])
        R_raw = 0.08*L + 0.08*S + 0.34*V + 0.16*F + 0.10*REF + 0.08*AOV + 0.16*R

    else:
        raise ValueError("Invalid role")

    R_pct = percentile_rank(R_raw, population_samples["R_raw_values"])
    level_points = 50 * R_pct
    initial_score = min(1000, max(0, base_score + level_points))
    initial_tier = get_tier(initial_score)

    decay = inactivity_days * 5
    if inconsistent:
        decay += 20

    final_score = max(0, initial_score - decay)
    final_tier = get_tier(final_score)

    return {
        "initial_level_score": initial_score,
        "initial_tier": initial_tier,
        "decay": decay,
        "final_score": final_score,
        "final_tier": final_tier,
        "inactivity_days": inactivity_days,
        "inconsistency": inconsistent
    }
