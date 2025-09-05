# ml_model_module.py

import math
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error

# ---------------- Example Training Data ---------------- #
# Replace with your full dataset
X = np.array([
    [0.9, 10, 120, 0.95, 0.05, 4.8],
    [0.7, 5, 60, 0.88, 0.1, 4.5],
    [0.95, 15, 200, 0.97, 0.02, 4.9],
    [0.5, 3, 30, 0.85, 0.15, 4.3]
])
y = np.array([700, 400, 850, 250])

# ---------------- Train XGBoost Regressor ---------------- #
ml_model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    objective="reg:squarederror",
    random_state=42
)
ml_model.fit(X, y)

# ---------------- Error Calculation ---------------- #
train_preds = ml_model.predict(X)
rmse = math.sqrt(mean_squared_error(y, train_preds))
error_percent = (rmse / np.mean(y)) * 100

def predict_with_error(features, ml_model=ml_model, rmse=rmse):
    """
    Predict score using ML model and return error margin.
    """
    arr = np.array([features])
    pred = ml_model.predict(arr)[0]
    
    # Relative error estimate
    relative_error = rmse / np.max(y)
    margin = pred * relative_error
    return pred, round(margin, 2)

# Export model and errors
__all__ = ["ml_model", "predict_with_error", "rmse", "error_percent"]
