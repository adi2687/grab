# level_score_module.py

import math
import numpy as np
from ml_model_module import predict_with_error

# ---------------- Utility Functions ---------------- #
def percentile_rank(value, population):
    if not population: return 0
    less = sum(1 for x in population if x < value)
    equal = sum(1 for x in population if x == value)
    return (less + 0.5*equal)/len(population)

def get_tier(score):
    if score <= 250: return "Bronze"
    elif score <= 500: return "Amber"
    elif score <= 750: return "Ruby"
    else: return "Gold"

def apply_fairness(score, tier, inactivity_days, inconsistent_days):
    penalty = int(100*(1 - math.exp(-inactivity_days/30))) if inactivity_days else 0
    if inconsistent_days: penalty += 30
    tier_factor = {"Bronze":0.5,"Amber":0.75,"Ruby":1.0,"Gold":1.0}
    penalty = int(penalty * tier_factor[tier])
    score_after = max(0, score - penalty)
    bonus = 20 if inactivity_days==0 and inconsistent_days==0 else 0
    score_after = min(1000, score_after + bonus)
    return score_after, penalty, bonus

def compute_days(activity_log, max_inactivity_gap=7):
    inconsistent_days = sum(1 for day in activity_log if not day["active"])
    inactivity_days = 0
    gap = 0
    for day in activity_log:
        if not day["active"]:
            gap += 1
        else:
            if gap > max_inactivity_gap: inactivity_days += gap
            gap = 0
    if gap > max_inactivity_gap: inactivity_days += gap
    return inconsistent_days, inactivity_days

# ---------------- Main Level Score Function ---------------- #
def compute_level_score_backend(user_profile, population_samples, month_active, history_scores=[]):
    features = user_profile["features"]

    # Predict raw ML score with error margin
    R_raw, pred_error = predict_with_error([
        features["login_rate"], 
        features["streak_days"],
        features.get("rides_30d", 0),
        features.get("on_time_rate", 0),
        features.get("cancellation_rate", 0),
        features["rating"]
    ])

    R_raw /= 1000  # normalize
    percentile = percentile_rank(R_raw, population_samples.get("R_raw_values", []))

    base_gain = 1000 * percentile * 0.15
    gain = min(base_gain * (0.5 + 0.05*month_active), 80)

    prev_score = history_scores[-1] if history_scores else 0
    initial_score = prev_score + gain
    tier = get_tier(initial_score)

    activity_log = user_profile.get("activity_log", [])
    inconsistent_days, inactivity_days = compute_days(activity_log)

    score_after, penalty, bonus = apply_fairness(initial_score, tier, inactivity_days, inconsistent_days)

    boost = 0
    if month_active == 1 and user_profile.get("first_time_account", True) and user_profile.get("worked_in_company_before", False):
        boost = 40  # fixed 40 boost

    final_score = min(1000, score_after + boost)

    return {
        "final_score": round(final_score, 2),
        "tier": get_tier(final_score),
        "penalty": penalty,
        "consistency_bonus": bonus,
        "boost": boost,
        "inconsistent_days": inconsistent_days,
        "inactivity_days": inactivity_days,
        "ml_prediction_error_margin": pred_error,
        "reason_log": f"+{round(gain,2)} gain, -{penalty} penalty, +{bonus} consistency, +{boost} boost, ±{pred_error} model error"
    }
