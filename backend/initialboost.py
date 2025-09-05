import pandas as pd

# ---------------- Example Dataset ---------------- #
data = {
    "UserID": [1, 2, 3, 4],
    "SocialEngagement": [70, 20, 50, 10],      # out of 100
    "FinancialEngagement": [80, 40, 60, 30],   # out of 100
    "GigWorkerEngagement": [50, 10, 0, 70],    # out of 100
    "JobEngagement": [90, 60, 40, 20]          # out of 100
}
df = pd.DataFrame(data)

# ---------------- Parameters ---------------- #
MAX_INITIAL_BOOST = 20  # max possible boost
ERROR_THRESHOLD = 5     # if deviation > 5, apply correction

# ---------------- Functions ---------------- #
def normalize_preferences(preference_factors):
    """Normalize preference factors so they sum to 1."""
    total = sum(preference_factors.values())
    return {k: v / total for k, v in preference_factors.items()}

def calculate_initial_boosts(df, preference_factors):
    """Calculate initial boost (0–30) and error factor for each user."""
    # Normalize company preferences
    weights = normalize_preferences(preference_factors)

    # Calculate Initial Boost for each user
    def compute_boost(row):
        score = 0
        for factor, weight in weights.items():
            score += row[factor] * weight
        return round((score / 100) * MAX_INITIAL_BOOST, 2)

    df["InitialBoost"] = df.apply(compute_boost, axis=1)

    # Error Factor = deviation from mean boost
    mean_boost = df["InitialBoost"].mean()
    df["ErrorFactor"] = df["InitialBoost"].apply(lambda x: round(abs(x - mean_boost), 2))

    # ---------------- Error Handling ---------------- #
    # If any user exceeds threshold → apply correction
    if df["ErrorFactor"].max() > ERROR_THRESHOLD:
        print("⚠️ Error factor exceeded threshold! Applying correction...")

        # Technique 1: Normalization to shrink spread
        min_boost, max_boost = df["InitialBoost"].min(), df["InitialBoost"].max()
        df["InitialBoost"] = df["InitialBoost"].apply(
            lambda x: round(((x - min_boost) / (max_boost - min_boost)) * MAX_INITIAL_BOOST, 2)
        )

        # Recalculate error factors after correction
        mean_boost = df["InitialBoost"].mean()
        df["ErrorFactor"] = df["InitialBoost"].apply(lambda x: round(abs(x - mean_boost), 2))

    return df[["UserID", "InitialBoost", "ErrorFactor"]]

# ---------------- Example Run ---------------- #
company_preferences = {
    "SocialEngagement": 0.2,
    "FinancialEngagement": 1.0,
    "GigWorkerEngagement": 0.5,
    "JobEngagement": 0.7
}

results = calculate_initial_boosts(df, company_preferences)
print(results)
