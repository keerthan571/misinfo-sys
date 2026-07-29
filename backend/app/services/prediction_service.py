class PredictionService:


    def calculate_risk_level(self, probability):

        if probability >= 80:
            return "Very High"

        elif probability >= 60:
            return "High"

        elif probability >= 30:
            return "Medium"

        else:
            return "Low"



    def predict_spread(self, features):


        likes = features.get("likes", 0) or 0
        shares = features.get("shares", 0) or 0
        comments = features.get("comments", 0) or 0
        views = features.get("views", 0) or 0
        bookmarks = features.get("bookmarks", 0) or 0


        spread_score = features.get(
            "spread_score",
            0
        ) or 0


        risk_score = features.get(
            "risk_score",
            0
        ) or 0


        emotion_score = features.get(
            "emotion_score",
            0
        ) or 0


        manipulation_score = features.get(
            "manipulation_score",
            0
        ) or 0



        # -----------------------------
        # Engagement calculation
        # -----------------------------

        engagement_score = 0


        if views > 0:

            engagement_score = (

                (
                    likes +
                    shares +
                    comments +
                    bookmarks
                )
                /
                views

            ) * 100



        engagement_score = min(
            engagement_score,
            100
        )



        # -----------------------------
        # Spread Probability
        # -----------------------------

        spread_probability = (

            (risk_score * 0.40)
            +
            (spread_score * 0.30)
            +
            (emotion_score * 0.10)
            +
            (manipulation_score * 0.10)
            +
            (engagement_score * 0.10)

        )


        spread_probability = round(
            min(
                spread_probability,
                100
            ),
            2
        )



        risk_level = self.calculate_risk_level(
            spread_probability
        )



        # -----------------------------
        # Estimated Reach Prediction
        # -----------------------------

        # If social media views exist,
        # use them as the base.
        # For text-only input,
        # use a default baseline.

        base_views = views if views > 0 else 1000


        growth_multiplier = (
            1 +
            (spread_probability / 100)
        )


        predicted_reach = round(

            base_views *
            growth_multiplier,

            2

        )



        # -----------------------------
        # Explanation
        # -----------------------------

        if shares > likes:

            reason = (

                "High redistribution potential detected "
                "because sharing activity is dominant."

            )


        elif risk_score >= 70:

            reason = (

                "High misinformation risk signals "
                "indicate possible rapid spread."

            )


        elif spread_score >= 50:

            reason = (

                "Content shows multiple spread indicators."

            )


        else:

            reason = (

                "Low spread indicators detected."

            )



        return {


            "status": "success",


            "module": "Spread Prediction",


            "data": {


                "predicted_reach":
                    predicted_reach,


                "spread_probability":
                    spread_probability,


                "risk_level":
                    risk_level,


                "virality_score":
                    round(
                        (
                            spread_score * 0.6
                            +
                            spread_probability * 0.4
                        ),
                        2
                    ),


                "features_used": {


                    "likes": likes,

                    "shares": shares,

                    "comments": comments,

                    "views": views,

                    "bookmarks": bookmarks,

                    "spread_score": spread_score,

                    "risk_score": risk_score,

                    "emotion_score": emotion_score,

                    "manipulation_score": manipulation_score

                }

            },


            "analysis_summary": reason

        }




prediction_service = PredictionService()