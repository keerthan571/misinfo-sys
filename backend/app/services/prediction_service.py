class PredictionService:

    def calculate_risk_level(self,probability):
        if probability>=80:
            return "Very High"
        elif probability>=60:
            return "High"
        elif probability>=30:
            return "Medium"
        return "Low"

    def predict_spread(self,features):

        likes=features.get("likes",0) or 0
        shares=features.get("shares",0) or 0
        comments=features.get("comments",0) or 0
        views=features.get("views",0) or 0
        bookmarks=features.get("bookmarks",0) or 0

        spread_score=features.get("spread_score",0) or 0
        risk_score=features.get("risk_score",0) or 0

        total_engagement=(
            likes+
            shares+
            comments+
            bookmarks
        )

        if views>0:
            engagement_score=(
                total_engagement/views
            )*100
        else:
            engagement_score=min(
                total_engagement/100,
                100
            )

        engagement_score=round(
            min(
                engagement_score,
                100
            ),
            2
        )

        spread_probability=(
            risk_score*0.35+
            spread_score*0.35+
            engagement_score*0.20+
            min(bookmarks/100,10)
        )

        spread_probability=round(
            min(
                spread_probability,
                100
            ),
            2
        )

        risk_level=self.calculate_risk_level(
            spread_probability
        )

        if views>0:
            predicted_reach=views*(
                1+
                spread_probability/100
            )
        else:
            predicted_reach=total_engagement*(
                5+
                spread_probability/20
            )

        predicted_reach=round(
            predicted_reach,
            2
        )

        if shares>likes:
            summary="High redistribution potential detected because sharing activity is dominant."
        elif risk_score>=70:
            summary="High misinformation risk signals detected."
        elif spread_score>=50:
            summary="Multiple spread indicators detected."
        else:
            summary="Low spread indicators detected."

        return {
            "status":"success",
            "module":"Spread Prediction",
            "data":{
                "predicted_reach":predicted_reach,
                "spread_probability":spread_probability,
                "risk_level":risk_level,
                "virality_score":round(
                    (
                        spread_score*0.6
                    )+
                    (
                        spread_probability*0.4
                    ),
                    2
                ),
                "features_used":{
                    "likes":likes,
                    "shares":shares,
                    "comments":comments,
                    "views":views,
                    "bookmarks":bookmarks,
                    "spread_score":spread_score,
                    "risk_score":risk_score,
                    "engagement_score":engagement_score
                }
            },
            "analysis_summary":summary
        }


prediction_service=PredictionService()