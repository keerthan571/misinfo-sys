import numpy as np
from sklearn.linear_model import LinearRegression


class PredictionService:
    """
    Predicts how far misinformation may spread
    using engagement-based machine learning analysis.
    """

    def __init__(self):

        # Training dataset
        # Features:
        # [likes, shares, comments, follower_count]
        self.X = np.array([
            [100, 30, 20, 500],
            [200, 50, 40, 1200],
            [300, 80, 60, 2000],
            [400, 100, 75, 3500],
            [500, 150, 120, 5000],
            [700, 250, 180, 8000]
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

        # Train Linear Regression model
        self.model = LinearRegression()
        self.model.fit(self.X, self.y)

    def calculate_risk_level(self, predicted_reach):

        if predicted_reach > 12000:
            return "Very High"

        elif predicted_reach > 7000:
            return "High"

        elif predicted_reach > 3000:
            return "Medium"

        return "Low"

    def predict_spread(self, post_features: dict):

        # Extract features
        likes = post_features.get("initial_likes", 0)
        shares = post_features.get("initial_shares", 0)
        comments = post_features.get("comments", 0)
        followers = post_features.get("follower_count", 0)

        # Prepare input
        input_data = np.array([
            [likes, shares, comments, followers]
        ])

        # Predict reach
        predicted_reach = self.model.predict(input_data)[0]

        # Risk analysis
        risk_level = self.calculate_risk_level(predicted_reach)

        # Virality score
        virality_score = min(
            round((predicted_reach / 15000) * 100, 2),
            100
        )

        # Explainable AI summary
        summary = (
            "This post shows strong virality potential due to "
            "high engagement and audience reach."
            if predicted_reach > 7000
            else
            "This post currently shows moderate or limited spread potential."
        )

        return {
            "status": "success",
            "module": "Spread Prediction",

            "data": {
                "features_used": {
                    "likes": likes,
                    "shares": shares,
                    "comments": comments,
                    "followers": followers
                },

                "predicted_reach": round(predicted_reach, 2),

                "risk_level": risk_level,

                "virality_score": virality_score,

                "engagement_breakdown": {
                    "likes": likes,
                    "shares": shares,
                    "comments": comments
                }
            },

            "analysis_summary": summary
        }


prediction_service = PredictionService()