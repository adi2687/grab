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

def apply_fairness(score, tier, inactivity_days, inconsistent_days, was_active=True):
    """Apply fairness rules: scaled penalties + consistency bonus."""
    # Base penalties
    penalty = 0
    if inactivity_days > 0:
        penalty += int(100 * (1 - math.exp(-inactivity_days / 30)))
    if inconsistent_days > 0:
        penalty += 30

    # Scale penalties by tier fairness
    tier_penalty_factor = {
        "Bronze": 0.5,
        "Amber": 0.75,
        "Ruby": 1.0,
        "Gold": 1.0
    }
    penalty = int(penalty * tier_penalty_factor[tier])

    # Apply penalty
    score_after_penalty = max(0, score - penalty)

    # Consistency bonus
    consistency_bonus = 0
    if was_active and inconsistent_days == 0 and inactivity_days == 0:
        consistency_bonus = 20
        score_after_penalty = min(1000, score_after_penalty + consistency_bonus)

    return score_after_penalty, penalty, consistency_bonus

def update_level_score(role, features, population_samples,
                       prev_level_score=0,
                       inactivity_days=0,
                       inconsistent_days=0,
                       months_active=1,
                       growth_rate=0.3,
                       max_monthly_gain=150,
                       first_time_account=True,
                       worked_in_company_before=False,
                       weight_boost=0.4):
    """
    Updates user level score month by month with fairness.
    """

    # ---- Step 1: Calculate R_raw by role ----
    if role == "driver":
        L = features["login_rate"]
        S = streak_score(features["streak_days"], 14)
        V = min(percentile_rank(features["rides_30d"], population_samples["rides_30d"]), 0.8)  # volume cap
        OT = percentile_rank(features["on_time_rate"], population_samples["on_time_rate"])
        CR = 1 - percentile_rank(features["cancellation_rate"], population_samples["cancellation_rate"])
        R = percentile_rank(features["rating"], population_samples["rating"])
        R_raw = 0.10*L + 0.10*S + 0.35*V + 0.20*OT + 0.15*CR + 0.10*R

    elif role == "delivery":
        L = features["login_rate"]
        S = streak_score(features["streak_days"], 14)
        V = min(percentile_rank(features["deliveries_30d"], population_samples["deliveries_30d"]), 0.8)
        OT = percentile_rank(features["on_time_rate"], population_samples["on_time_rate"])
        FD = 1 - percentile_rank(features["failed_deliveries_rate"], population_samples["failed_deliveries_rate"])
        AJ = percentile_rank(features["job_acceptance_rate"], population_samples["job_acceptance_rate"])
        R = percentile_rank(features["rating"], population_samples["rating"])
        R_raw = 0.10*L + 0.10*S + 0.30*V + 0.20*OT + 0.10*FD + 0.10*AJ + 0.10*R

    elif role == "merchant":
        L = features["login_rate"]
        S = streak_score(features["streak_days"], 21)
        V = min(percentile_rank(features["goods_sold_30d"], population_samples["goods_sold_30d"]), 0.8)
        F = percentile_rank(features["fulfilment_rate"], population_samples["fulfilment_rate"])
        REF = 1 - percentile_rank(features["refund_rate"], population_samples["refund_rate"])
        AOV = percentile_rank(features["avg_order_value"], population_samples["avg_order_value"])
        R = percentile_rank(features["rating"], population_samples["rating"])
        R_raw = 0.08*L + 0.08*S + 0.34*V + 0.16*F + 0.10*REF + 0.08*AOV + 0.16*R

    else:
        raise ValueError("Invalid role")

    # ---- Step 2: Monthly gain ----
    R_pct = percentile_rank(R_raw, population_samples["R_raw_values"])
    monthly_gain = 1000 * R_pct * growth_rate
    monthly_gain = min(monthly_gain, max_monthly_gain)

    # ---- Step 3: Initial score ----
    initial_score = prev_level_score + monthly_gain
    initial_tier = get_tier(initial_score)

    # ---- Step 4: Apply fairness (penalty + consistency bonus) ----
    score_after_penalty, penalty, consistency_bonus = apply_fairness(
        initial_score, initial_tier, inactivity_days, inconsistent_days, was_active=True
    )

    # ---- Step 5: One-time initial boost ----
    boost_applied = 0
    boost_used = False
    if months_active == 1 and first_time_account and worked_in_company_before:
        raw_boost = 100
        boost_applied = raw_boost * weight_boost
        boost_used = True

    # ---- Step 6: Final score ----
    final_score = min(1000, score_after_penalty + boost_applied)
    final_tier = get_tier(final_score)

    # ---- Step 7: Output ----
    return {
        "inconsistent_days": inconsistent_days,
        "initial_score": round(initial_score, 2),
        "penalty": penalty,
        "score_after_penalty": round(score_after_penalty, 2),
        "consistency_bonus": consistency_bonus,
        "boost_applied": boost_applied,
        "boost_used": boost_used,
        "final_score": round(final_score, 2),
        "final_tier": final_tier,
        "reason_log": f"+{round(monthly_gain,2)} gain, -{penalty} penalty, "
                      f"+{consistency_bonus} consistency, +{boost_applied} boost"
    }
