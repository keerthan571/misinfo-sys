import numpy as np
from sklearn.linear_model import LinearRegression


class PredictionService:
    """
    Predicts how far misinformation may spread
    using engagement-based machine learning analysis.
    """

    def __init__(self):

        # Features:
        # [likes, shares, comments, followers, account_age_days]
        self.X = np.array([
            [100, 30, 20, 500, 30],
            [200, 50, 40, 1200, 60],
            [300, 80, 60, 2000, 120],
            [400, 100, 75, 3500, 180],
            [500, 150, 120, 5000, 365],
            [700, 250, 180, 8000, 730]
        ])

        # Expected reach values
        self.y = np.array([
            1000,
            2500,
            4000,
            6500,
            9000,
            15000
        ])

        # Train model
        self.model = LinearRegression()
        self.model.fit(self.X, self.y)

    def calculate_risk_level(self, predicted_reach):

        if predicted_reach > 50000:
            return "Critical"

        elif predicted_reach > 10000:
            return "High"

        elif predicted_reach > 1000:
            return "Moderate"

        return "Low"

    def generate_reasons(self, likes, shares, followers):

        reasons = []

        if followers > 5000:
            reasons.append("Large follower base detected")

        if shares > 100:
            reasons.append("High share activity detected")

        if likes > 300:
            reasons.append("Strong audience engagement")

        if len(reasons) == 0:
            reasons.append("Limited engagement indicators")

        return reasons

    def calculate_confidence(self, shares):

        confidence = min(
            95,
            round(60 + (shares / 10), 2)
        )

        return confidence

    def predict_spread(self, post_features: dict):

        # Extract features
        likes = post_features.get("initial_likes", 0)
        shares = post_features.get("initial_shares", 0)
        comments = post_features.get("comments", 0)
        followers = post_features.get("follower_count", 0)
        account_age_days = post_features.get(
            "account_age_days",
            365
        )

        # Prepare model input
        input_data = np.array([
            [
                likes,
                shares,
                comments,
                followers,
                account_age_days
            ]
        ])

        # Predict reach
        predicted_reach = self.model.predict(input_data)[0]

        # Risk level
        risk_level = self.calculate_risk_level(
            predicted_reach
        )

        # Virality score
        virality_score = min(
            round((predicted_reach / 15000) * 100, 2),
            100
        )

        # Confidence score
        confidence = self.calculate_confidence(
            shares
        )

        # Explainability
        reasons = self.generate_reasons(
            likes,
            shares,
            followers
        )

        return {
            "status": "success",
            "module": "Spread Prediction",

            "prediction": {
                "predicted_reach": round(
                    predicted_reach,
                    2
                ),

                "risk_level": risk_level,

                "confidence": confidence,

                "virality_score": virality_score,

                "reasons": reasons
            },

            "input_features": {
                "likes": likes,
                "shares": shares,
                "comments": comments,
                "followers": followers,
                "account_age_days": account_age_days
            }
        }


prediction_service = PredictionService()