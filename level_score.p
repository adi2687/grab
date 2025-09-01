import math

def percentile_rank(value, population):
    """
    Computes percentile rank of value in a population list.
    Assumes population is non-empty.
    """
    less = sum(1 for x in population if x < value)
    equal = sum(1 for x in population if x == value)
    return (less + 0.5 * equal) / len(population)


def streak_score(streak_days, tau):
    return 1 - math.exp(-streak_days / tau)


def tenure_boost(years_in_company, new_account_flag, previous_account_exists):
    if new_account_flag and not previous_account_exists:
        if years_in_company >= 3:
            return 125
        elif years_in_company >= 1:
            return 100
    return 0


def compute_level_score(role, features, base_score, population_samples,
                        years_in_company=0, new_account_flag=False, previous_account_exists=False):
    """
    role: "driver", "delivery", "merchant"
    features: dict containing relevant metrics for that role
    base_score: FinalCWS_core before adding level_points/tenure
    population_samples: dict with arrays of population data for percentile calculations
    """

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

    # Percentile of R_raw itself across role population
    R_pct = percentile_rank(R_raw, population_samples["R_raw_values"])
    level_points = 50 * R_pct

    # Tenure bonus
    t_boost = tenure_boost(years_in_company, new_account_flag, previous_account_exists)

    # Final score
    final_score = min(1000, max(0, base_score + level_points + t_boost))

    # Tier mapping (G.R.A.B)
    if final_score <= 250:
        tier = "Bronze"
    elif final_score <= 500:
        tier = "Amber"
    elif final_score <= 750:
        tier = "Ruby"
    else:
        tier = "Gold"

    return {
        "R_raw": R_raw,
        "level_points": level_points,
        "tenure_boost": t_boost,
        "final_score": final_score,
        "tier": tier
    }


# Example usage (dummy numbers)
if __name__ == "__main__":
    features_driver = {
        "login_rate": 0.9,
        "streak_days": 10,
        "rides_30d": 120,
        "on_time_rate": 0.95,
        "cancellation_rate": 0.05,
        "rating": 4.8
    }

    # fake population data for percentile calc
    population_samples_driver = {
        "rides_30d": [50, 100, 150, 200],
        "on_time_rate": [0.85, 0.9, 0.95],
        "cancellation_rate": [0.1, 0.07, 0.05],
        "rating": [4.5, 4.7, 4.9],
        "R_raw_values": [0.4, 0.5, 0.6, 0.7]
    }

    result = compute_level_score(
        role="driver",
        features=features_driver,
        base_score=600,
        population_samples=population_samples_driver,
        years_in_company=2,
        new_account_flag=True,
        previous_account_exists=False
    )

    print(result)
