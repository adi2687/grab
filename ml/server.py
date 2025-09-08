from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from level_score import compute_level_score_backend
from spam_detection import apply_spam_penalty
from initial_boosts import get_boost_for_user
import numpy as np 
def to_serializable(obj):
    if isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    return obj
app = FastAPI(title="Grab ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserFeatures(BaseModel):
    user_id: str
    role: str = "driver"
    features: Dict[str, Any]
    activity_log: List[Dict[str, Any]] = []
    history_scores: List[float] = []

class BoostRequest(BaseModel):
    user_id: str
    engagement_metrics: Dict[str, float]

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/calculate-score")
async def calculate_score(user_data: UserFeatures):
    try:
        score_dict = compute_level_score_backend(
            user_profile={
                "user_id": user_data.user_id,
                "role": user_data.role,
                "features": user_data.features,
                "activity_log": user_data.activity_log
            },
            population_samples={"R_raw_values": []},
            month_active=30,
            history_scores=user_data.history_scores
        )

        final_score, credit_score = apply_spam_penalty(
            final_score=float(score_dict["final_score"]),
            credit_score=float(score_dict["final_score"]) * 0.9,
            hybrid_score=float(score_dict["spam_score"]),
        )

        score_dict.update({
            "user_id": user_data.user_id,
            "final_score": final_score,
            "credit_score": credit_score,
            "status": "success"
        })

        # 🔥 sanitize before returning
        return to_serializable(score_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-initial-boost")
async def get_initial_boost(request: BoostRequest):
    try:
        boost = get_boost_for_user(request.user_id)
        return {
            "user_id": request.user_id,
            "initial_boost": boost,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
