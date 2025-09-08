import numpy as np

# ---------------- Delta Adjustment Rule ---------------- #
DELTA_RULE = {
    "Gold": 1.75,
    "Ruby": 1.50,
    "Amber": 1.25,
    "Bronze": 1.00
}

# ---------------- Role-based feature engineering ---------------- #
ROLE_FEATURES = {
    "driver": ["rides_completed", "avg_rating", "on_time_ratio", "complaints"],
    "merchant": ["transactions", "disputes", "fulfillment_rate", "revenue_growth"],
    "student": ["assignments_submitted", "attendance", "peer_feedback", "grades"]
}

ROLE_WEIGHTS = {
    "driver": [0.35, 0.30, 0.20, 0.15],
    "merchant": [0.40, -0.20, 0.25, 0.15],
    "student": [0.25, 0.20, 0.25, 0.30]
}

# Extra factors (B, L, D)
EXTRA_WEIGHTS = {"B": 0.2, "L": 0.2, "D": 0.2}

# ---------------- Utility Functions ---------------- #
def percentile_rank(value, population):
    if not population:
        return 0
    less = sum(1 for x in population if x < value)
    equal = sum(1 for x in population if x == value)
    return (less + 0.5 * equal) / len(population)

def normalize_feature(value, feature_name):
    if feature_name in ["rides_completed", "transactions", "assignments_submitted"]:
        return min(value / 100.0, 1.0)
    elif feature_name in ["avg_rating", "peer_feedback"]:
        return value / 5.0
    elif feature_name in ["on_time_ratio", "fulfillment_rate", "attendance"]:
        return value
    elif feature_name in ["complaints", "disputes"]:
        return 1.0 - min(value / 50.0, 1.0)
    elif feature_name in ["revenue_growth", "grades"]:
        return min(value / 100.0, 1.0)
    else:
        return 0.5

# ---------------- Role Score Calculation ---------------- #
def compute_role_score(user_profile):
    role = user_profile["role"]
    features = ROLE_FEATURES.get(role, [])
    weights = ROLE_WEIGHTS.get(role, [])
    if not features or not weights:
        return 50  

    score = 0
    for f, w in zip(features, weights):
        val = normalize_feature(user_profile.get(f, 0), f)
        score += val * w

    return score, weights

def global_cws(user_profile, population_samples):
    role = user_profile["role"]
    raw_score, _ = compute_role_score(user_profile)
    population_scores = [compute_role_score(p)[0] for p in population_samples if p["role"] == role]
    rank = percentile_rank(raw_score, population_scores)
    return 40 + 60 * rank  

# ---------------- Fairness Adjustment ---------------- #
def fairness_adjustment(global_score, accept_rate, target_accept, eta=0.1):
    adj = -eta * (accept_rate - target_accept)
    return np.clip(global_score + adj, 0, 100), adj

# ---------------- Final Credit Score Formula ---------------- #
def compute_final_credit_score(user_profile, population_samples, 
                               accept_rate=0.6, target_accept=0.7, eta=0.1,
                               lambda_r=0.7, delta_base=2.0):
    role = user_profile["role"]

    # Role score and weights
    role_score, role_weights = compute_role_score(user_profile)

    # Extra factors (B, L, D)
    B = user_profile.get("B", 0.5)
    L = user_profile.get("L", 0.5)
    D = user_profile.get("D", 0.5)

    numerator = role_score + EXTRA_WEIGHTS["B"] * B + EXTRA_WEIGHTS["L"] * L + EXTRA_WEIGHTS["D"] * D
    denominator = sum(abs(w) for w in role_weights) + sum(EXTRA_WEIGHTS.values())
    role_component = numerator / denominator if denominator != 0 else 0.5

    # Global score
    global_score = global_cws(user_profile, population_samples)

    # Fairness adjustment
    fairness_score, adj_r = fairness_adjustment(global_score, accept_rate, target_accept, eta)

    # Combine with lambda
    combined_score = lambda_r * role_component * 100 + (1 - lambda_r) * fairness_score

    # Final score before delta
    final_score = np.clip(combined_score + adj_r, 0, 100)

    # Delta adjustment based on tier
    tier = user_profile.get("tier", "Bronze")
    delta_multiplier = DELTA_RULE.get(tier, 1.0)
    delta_adj = delta_multiplier * delta_base

    final_score = np.clip(final_score + delta_adj, 0, 100)

    return {
        "role": role,
        "tier": tier,
        "role_component": role_component * 100,
        "global_cws": global_score,
        "fairness_adj": adj_r,
        "final_score": final_score,
        "delta_adj": delta_adj
    }


# ---------------- Example ---------------- #
if _name_ == "_main_":
    user = {
        "role": "driver",
        "rides_completed": 120,
        "avg_rating": 4.8,
        "on_time_ratio": 0.9,
        "complaints": 3,
        "B": 0.7, "L": 0.6, "D": 0.8,
        "tier": "Gold"
    }
    population = [
        {"role": "driver", "rides_completed": 80, "avg_rating": 4.5, "on_time_ratio": 0.85, "complaints": 5},
        {"role": "driver", "rides_completed": 200, "avg_rating": 4.9, "on_time_ratio": 0.95, "complaints": 1},
    ]

    result = compute_final_credit_score(user, population)
    print(result)
