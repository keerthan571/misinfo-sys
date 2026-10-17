import math


class PredictionService:

    def calculate_risk_level(self, probability):
        if probability >= 80:
            return "Very High"
        elif probability >= 60:
            return "High"
        elif probability >= 30:
            return "Medium"
        return "Low"

    @staticmethod
    def _number(value, default=0.0):
        """Convert a value to a finite, non-negative number."""
        try:
            number = float(value)
            if not math.isfinite(number) or number < 0:
                return default
            return number
        except (TypeError, ValueError):
            return default

    def predict_spread(self, features):

        # ---------------------------------------------------------
        # INPUTS AND TIME METADATA
        # ---------------------------------------------------------

        platform = str(features.get("platform", "")).lower()

        prediction_days = features.get("prediction_days", 7)
        try:
            prediction_days = int(prediction_days)
        except (TypeError, ValueError):
            prediction_days = 7

        prediction_days = max(1, min(prediction_days, 36500))

        post_age_hours = self._number(
            features.get("post_age_hours"), 0
        )

        post_age_days = post_age_hours / 24

        # ---------------------------------------------------------
        # ENGAGEMENT METRICS
        # ---------------------------------------------------------

        likes = self._number(features.get("likes"))
        comments = self._number(features.get("comments"))
        shares = self._number(features.get("shares"))
        views = self._number(features.get("views"))
        reposts = self._number(features.get("reposts"))
        bookmarks = self._number(features.get("bookmarks"))
        replies = self._number(features.get("replies"))
        reactions = self._number(features.get("reactions"))
        saves = self._number(features.get("saves"))

        calculation_comments = comments
        calculation_shares = shares
        calculation_saves = saves

        # X / Twitter
        if "twitter" in platform or platform == "x":
            calculation_comments = replies
            calculation_shares = reposts
            calculation_saves = bookmarks

        # Facebook
        elif "facebook" in platform:
            likes = reactions if reactions > 0 else likes
            calculation_comments = comments
            calculation_shares = shares

        # Instagram
        elif "instagram" in platform:
            calculation_comments = comments
            calculation_shares = shares
            calculation_saves = saves if saves > 0 else bookmarks

        # ---------------------------------------------------------
        # EXISTING SCORES
        # ---------------------------------------------------------

        spread_score = self._number(features.get("spread_score"))
        risk_score = self._number(features.get("risk_score"))

        spread_score = min(spread_score, 100)
        risk_score = min(risk_score, 100)

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
                total_engagement / views
            ) * 100
        else:
            engagement_score = min(total_engagement / 100, 100)

        engagement_score = round(
            min(engagement_score, 100), 2
        )

        # ---------------------------------------------------------
        # BASE SPREAD POTENTIAL
        # ---------------------------------------------------------

        base_probability = (
            risk_score * 0.35
            + spread_score * 0.35
            + engagement_score * 0.30
        )

        base_probability = max(
            0, min(base_probability, 100)
        )

        # ---------------------------------------------------------
        # TIME-AWARE HEURISTIC
        # ---------------------------------------------------------
        #
        # Longer horizons allow more time for additional spread.
        # Older posts receive a lower momentum adjustment.
        #
        # These are heuristic adjustments, not learned parameters.
        # ---------------------------------------------------------

        horizon_factor = (
            math.log1p(prediction_days)
            / math.log1p(7)
        )

        age_factor = 1 / (
            1 + (post_age_days / 30)
        )

        horizon_probability = base_probability * (
            1 + 0.15 * math.log1p(prediction_days)
        ) * age_factor

        horizon_probability = round(
            max(0, min(horizon_probability, 100)), 2
        )

        # ---------------------------------------------------------
        # REACH ESTIMATE
        # ---------------------------------------------------------
        #
        # This is a heuristic projection, not a trained forecast.
        # If views are available, use them as the current reach proxy.
        # Otherwise, estimate a proxy from engagement.
        # ---------------------------------------------------------

        if views > 0:
            current_reach_proxy = views
        else:
            current_reach_proxy = total_engagement * 5

        growth_fraction = (
            horizon_probability / 100
        ) * horizon_factor

        predicted_reach = round(
            current_reach_proxy * (1 + growth_fraction),
            2
        )

        # ---------------------------------------------------------
        # HORIZON PROJECTION CURVE
        # ---------------------------------------------------------
        #
        # Points are generated for visualization.
        # They are mathematical interpolations of this heuristic,
        # not independently observed future measurements.
        # ---------------------------------------------------------

        point_count = min(prediction_days, 30)

        projection_curve = []

        for index in range(point_count + 1):
            day = round(
                prediction_days * index / point_count
            )

            progress = day / prediction_days

            # Smooth interpolation between current proxy and estimate.
            estimated_reach = current_reach_proxy * (
                1 + growth_fraction * progress
            )

            projection_curve.append({
                "day": day,
                "estimated_reach": round(estimated_reach, 2),
            })

        # ---------------------------------------------------------
        # VIRALITY SCORE AND RISK LEVEL
        # ---------------------------------------------------------

        virality_score = round(spread_score, 2)

        risk_level = self.calculate_risk_level(
            horizon_probability
        )

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        if calculation_shares > likes:
            summary = (
                "Sharing activity is higher than likes, indicating "
                "a redistribution signal. Future spread is uncertain."
            )
        elif risk_score >= 70:
            summary = (
                "High misinformation-risk signals were detected. "
                "Misinformation risk is separate from actual future reach."
            )
        elif spread_score >= 50:
            summary = (
                "Multiple spread indicators were detected. "
                "The future reach estimate is heuristic."
            )
        else:
            summary = (
                "Current spread indicators are relatively low. "
                "Actual future engagement may differ from this estimate."
            )

        # ---------------------------------------------------------
        # FEATURES USED
        # ---------------------------------------------------------

        features_used = {
            "likes": self._number(features.get("likes")),
            "comments": self._number(features.get("comments")),
            "reactions": self._number(features.get("reactions")),
            "replies": self._number(features.get("replies")),
            "reposts": self._number(features.get("reposts")),
            "shares": self._number(features.get("shares")),
            "bookmarks": self._number(features.get("bookmarks")),
            "saves": self._number(features.get("saves")),
            "views": views,
            "spread_score": round(spread_score, 2),
            "risk_score": round(risk_score, 2),
            "engagement_score": engagement_score,
            "total_engagement": round(total_engagement, 2),
            "post_age_hours": round(post_age_hours, 2),
            "post_age_days": round(post_age_days, 2),
            "prediction_days": prediction_days,
        }

        # ---------------------------------------------------------
        # FINAL RESULT
        # ---------------------------------------------------------

        return {
            "status": "success",
            "module": "Spread Prediction",
            "data": {
                "predicted_reach": predicted_reach,
                "current_reach_proxy": round(
                    current_reach_proxy, 2
                ),
                "spread_probability": horizon_probability,
                "base_spread_probability": round(
                    base_probability, 2
                ),
                "risk_level": risk_level,
                "virality_score": virality_score,
                "prediction_days": prediction_days,
                "post_age_hours": round(post_age_hours, 2),
                "projection_curve": projection_curve,
                "forecast_type": "heuristic",
                "forecast_warning": (
                    "This is a heuristic estimate, not a validated "
                    "machine-learning forecast. The projection curve "
                    "is illustrative and actual future reach may differ."
                ),
                "features_used": features_used,
            },
            "analysis_summary": summary,
        }


prediction_service = PredictionService()
