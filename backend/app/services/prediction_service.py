class PredictionService:
    def __init__(self):
        pass

    def predict_spread(self, post_features: dict):
        """
        Predicts how far a post will spread based on initial engagement.
        Students can use Random Forest or Linear Regression here.
        """
        # Dummy prediction logic
        initial_likes = post_features.get('initial_likes', 0)
        account_age_days = post_features.get('account_age_days', 10)
        
        # Simple heuristic for dummy prediction
        predicted_reach = initial_likes * (account_age_days / 10) + 100
        
        return {
            "features_used": post_features,
            "predicted_reach": round(predicted_reach, 2),
            "risk_level": "High" if predicted_reach > 1000 else "Low"
        }

prediction_service = PredictionService()
