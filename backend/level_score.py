from ml_model import ml_model, percentile_rank, get_tier, apply_fairness, compute_days
from user_history import user_history_db
import numpy as np

def compute_level_score_backend(user_id, user_profile, population_samples, month_active):
    history_scores = user_history_db.get(user_id, [])
    
    features = user_profile["features"]
    arr = np.array([[features["login_rate"], features["streak_days"],
                     features.get("rides_30d",0), features.get("on_time_rate",0),
                     features.get("cancellation_rate",0), features["rating"]]])
    
    R_raw = ml_model.predict(arr)[0] / 1000
    percentile = percentile_rank(R_raw, population_samples["R_raw_values"])
    
    base_gain = 1000 * percentile * 0.15
    gain = min(base_gain * (0.5 + 0.05*month_active), 80)
    
    prev_score = history_scores[-1] if history_scores else 0
    initial_score = prev_score + gain
    tier = get_tier(initial_score)
    
    activity_log = user_profile.get("activity_log", [])
    inconsistent_days, inactivity_days = compute_days(activity_log)
    
    score_after, penalty, bonus = apply_fairness(initial_score, tier, inactivity_days, inconsistent_days)
    
    boost = 0
    if month_active==1 and user_profile.get("first_time_account", True) and user_profile.get("worked_in_company_before", False):
        boost = 100 * 0.4
    
    final_score = min(1000, score_after + boost)
    
    # Update user history
    user_history_db[user_id] = history_scores + [final_score]
    
    return {
        "final_score": round(final_score,2),
        "tier": get_tier(final_score),
        "penalty": penalty,
        "consistency_bonus": bonus,
        "boost": boost,
        "inconsistent_days": inconsistent_days,
        "inactivity_days": inactivity_days,
        "reason_log": f"+{round(gain,2)} gain, -{penalty} penalty, +{bonus} consistency, +{boost} boost"
    }
