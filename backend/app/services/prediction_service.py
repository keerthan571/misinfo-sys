class PredictionService:
    
    def calculate_risk_level(
        self,
        probability
    ):

        if probability >= 80:
            return "Very High"

        elif probability >= 60:
            return "High"

        elif probability >= 30:
            return "Medium"

        return "Low"


    def predict_spread(
        self,
        features
    ):

        # ---------------------------------------------------------
        # PLATFORM
        # ---------------------------------------------------------

        platform = str(
            features.get(
                "platform",
                ""
            )
        ).lower()


        # ---------------------------------------------------------
        # RAW ENGAGEMENT VALUES
        # ---------------------------------------------------------
        # These are the values actually received from the
        # Engagement Verification page / backend.
        # ---------------------------------------------------------

        likes = features.get(
            "likes",
            0
        ) or 0

        comments = features.get(
            "comments",
            0
        ) or 0

        shares = features.get(
            "shares",
            0
        ) or 0

        views = features.get(
            "views",
            0
        ) or 0

        reposts = features.get(
            "reposts",
            0
        ) or 0

        bookmarks = features.get(
            "bookmarks",
            0
        ) or 0

        replies = features.get(
            "replies",
            0
        ) or 0

        reactions = features.get(
            "reactions",
            0
        ) or 0

        saves = features.get(
            "saves",
            0
        ) or 0


        # ---------------------------------------------------------
        # PLATFORM-SPECIFIC NORMALIZATION
        # ---------------------------------------------------------
        #
        # This does NOT create new engagement values.
        # It only decides which received values participate
        # in the common spread calculation.
        # ---------------------------------------------------------

        calculation_comments = comments
        calculation_shares = shares
        calculation_saves = saves


        # Twitter / X
        if (
            "twitter" in platform
            or platform == "x"
        ):

            calculation_comments = replies
            calculation_shares = reposts
            calculation_saves = bookmarks


        # Facebook
        elif "facebook" in platform:

            # Facebook reactions act as the main
            # positive engagement signal.
            likes = (
                reactions
                if reactions > 0
                else likes
            )

            calculation_comments = comments
            calculation_shares = shares


        # Instagram
        elif "instagram" in platform:

            calculation_comments = comments
            calculation_shares = shares

            calculation_saves = (
                saves
                if saves > 0
                else bookmarks
            )


        # ---------------------------------------------------------
        # SPREAD SCORE
        # ---------------------------------------------------------

        spread_score = features.get(
            "spread_score",
            0
        ) or 0


        # ---------------------------------------------------------
        # NLP RISK SCORE
        # ---------------------------------------------------------

        risk_score = features.get(
            "risk_score",
            0
        ) or 0


        # ---------------------------------------------------------
        # TOTAL ENGAGEMENT
        # ---------------------------------------------------------
        #
        # Only metrics relevant to the platform calculation
        # are included.
        # ---------------------------------------------------------

        total_engagement = (
            likes
            + calculation_comments
            + calculation_shares
            + calculation_saves
        )


        # ---------------------------------------------------------
        # ENGAGEMENT SCORE
        # ---------------------------------------------------------

        if views > 0:

            engagement_score = (
                total_engagement /
                views
            ) * 100

        else:

            engagement_score = min(
                total_engagement / 100,
                100
            )


        engagement_score = round(
            min(
                engagement_score,
                100
            ),
            2
        )


        # ---------------------------------------------------------
        # SPREAD PROBABILITY
        # ---------------------------------------------------------

        spread_probability = (
            risk_score * 0.35
            + spread_score * 0.35
            + engagement_score * 0.30
        )


        spread_probability = round(
            min(
                spread_probability,
                100
            ),
            2
        )


        # ---------------------------------------------------------
        # RISK LEVEL
        # ---------------------------------------------------------

        risk_level = self.calculate_risk_level(
            spread_probability
        )


        # ---------------------------------------------------------
        # PREDICTED REACH
        # ---------------------------------------------------------

        if views > 0:

            predicted_reach = views * (
                1
                + spread_probability / 100
            )

        else:

            predicted_reach = total_engagement * (
                5
                + spread_probability / 20
            )


        predicted_reach = round(
            predicted_reach,
            2
        )


        # ---------------------------------------------------------
        # VIRALITY SCORE
        # ---------------------------------------------------------

        virality_score = round(
            min(
                spread_score,
                100
            ),
            2
        )


        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        if calculation_shares > likes:

            summary = (
                "High redistribution potential detected "
                "because sharing activity is dominant."
            )

        elif risk_score >= 70:

            summary = (
                "High misinformation risk signals detected."
            )

        elif spread_score >= 50:

            summary = (
                "Multiple spread indicators detected."
            )

        else:

            summary = (
                "Low spread indicators detected."
            )


        # ---------------------------------------------------------
        # FEATURES USED
        # ---------------------------------------------------------
        #
        # Keep the actual platform metrics visible.
        # This is important for debugging and verification.
        # ---------------------------------------------------------

        features_used = {}

        metric_keys = [
            "likes",
            "comments",
            "reactions",
            "replies",
            "reposts",
            "shares",
            "bookmarks",
            "saves",
            "views"
        ]


        for key in metric_keys:

            if key in features:

                features_used[key] = (
                    features.get(key) or 0
                )


        # Add calculated values
        features_used.update({

            "spread_score":
                spread_score,

            "risk_score":
                risk_score,

            "engagement_score":
                engagement_score

        })


        # ---------------------------------------------------------
        # FINAL RESULT
        # ---------------------------------------------------------

        return {

            "status":
                "success",

            "module":
                "Spread Prediction",

            "data": {

                "predicted_reach":
                    predicted_reach,

                "spread_probability":
                    spread_probability,

                "risk_level":
                    risk_level,

                "virality_score":
                    virality_score,

                "features_used":
                    features_used

            },

            "analysis_summary":
                summary

        }


prediction_service = PredictionService()