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

def update_level_score(role, features, population_samples,
                       prev_level_score=0,
                       inactivity_days=0,
                       inconsistent=False,
                       months_active=1,
                       growth_rate=0.3,
                       max_monthly_gain=150):
    """
    Update level score month by month.
    Starts from 0 at account creation, increases with activity,
    decreases with inactivity or inconsistency.
    """

    # ---- Step 1: Calculate R_raw by role ----
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

    # ---- Step 2: Calculate potential monthly gain ----
    R_pct = percentile_rank(R_raw, population_samples["R_raw_values"])
    monthly_gain = 1000 * R_pct * growth_rate
    monthly_gain = min(monthly_gain, max_monthly_gain)  # cap growth

    # ---- Step 3: Apply streak reward ----
    streak_bonus = 0
    if months_active % 3 == 0 and inactivity_days == 0 and not inconsistent:
        streak_bonus = 20

    # ---- Step 4: Update score ----
    new_score = prev_level_score + monthly_gain + streak_bonus

    # ---- Step 5: Apply penalties ----
    penalty = 0
    if inactivity_days > 0:
        penalty += int(100 * (1 - math.exp(-inactivity_days / 30)))  # exponential penalty
    if inconsistent:
        penalty += 30
    new_score -= penalty

    # ---- Step 6: Clamp score between 0–1000 ----
    new_score = max(0, min(1000, new_score))

    # ---- Step 7: Tier ----
    tier = get_tier(new_score)

    return {
        "prev_level_score": round(prev_level_score, 2),
        "monthly_gain": round(monthly_gain, 2),
        "streak_bonus": streak_bonus,
        "penalty": penalty,
        "final_level_score": round(new_score, 2),
        "tier": tier,
        "log": f"+{monthly_gain} gain, +{streak_bonus} bonus, -{penalty} penalty"
    }
