from flask import Flask, request, jsonify
from level_score import compute_level_score_backend

app = Flask(__name__)

@app.route("/check_score", methods=["POST"])
def check_score():
    data = request.json
    user_id = data.get("user_id")
    user_profile = data.get("user_profile")
    month_active = data.get("month_active", 1)
    population_samples = data.get("population_samples", {"R_raw_values": [0.4,0.5,0.6,0.7]})
    
    if not user_id or not user_profile:
        return jsonify({"error": "user_id and user_profile are required"}), 400
    
    result = compute_level_score_backend(user_id, user_profile, population_samples, month_active)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
