import numpy as np
from sklearn.linear_model import LinearRegression


class PredictionService:
    def __init__(self):

        # Sample training data
        self.X = np.array([
            [100, 30],
            [200, 50],
            [300, 80],
            [400, 100],
            [500, 150]
        ])

        self.y = np.array([
            1000,
            2500,
            4000,
            6000,
            9000
        ])

        # Train model
        self.model = LinearRegression()
        self.model.fit(self.X, self.y)

    def predict_spread(self, post_features: dict):

        initial_likes = post_features.get("initial_likes", 0)
        initial_shares = post_features.get("initial_shares", 0)

        input_data = np.array([[initial_likes, initial_shares]])

        predicted_reach = self.model.predict(input_data)[0]

        return {
            "features_used": post_features,
            "predicted_reach": round(predicted_reach, 2),
            "risk_level": "High" if predicted_reach > 5000 else "Low"
        }


prediction_service = PredictionService()