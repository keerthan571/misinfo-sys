class SpreadFactorService:
    
    def analyze(
        self,
        engagement,
        content_analysis=None,
        platform=None
    ):

        # ---------------------------------------------------------
        # NORMALIZE INPUTS
        # ---------------------------------------------------------

        engagement = (
            engagement
            if isinstance(engagement, dict)
            else {}
        )

        platform_name = str(
            platform or ""
        ).lower().strip()

        # ---------------------------------------------------------
        # RAW ENGAGEMENT METRICS
        #
        # Keep the actual extracted metric names.
        # Do NOT expect "reactions" or "saves" when the backend
        # actually provides "likes" or "bookmarks".
        # ---------------------------------------------------------

        likes = engagement.get(
            "likes",
            0
        ) or 0

        comments = engagement.get(
            "comments",
            0
        ) or 0

        replies = engagement.get(
            "replies",
            0
        ) or 0

        shares = engagement.get(
            "shares",
            0
        ) or 0

        reposts = engagement.get(
            "reposts",
            0
        ) or 0

        bookmarks = engagement.get(
            "bookmarks",
            0
        ) or 0

        views = engagement.get(
            "views",
            0
        ) or 0

        followers = engagement.get(
            "followers",
            0
        ) or 0

        # Make sure numerical values are safe.
        try:
            likes = float(likes)
        except (TypeError, ValueError):
            likes = 0

        try:
            comments = float(comments)
        except (TypeError, ValueError):
            comments = 0

        try:
            replies = float(replies)
        except (TypeError, ValueError):
            replies = 0

        try:
            shares = float(shares)
        except (TypeError, ValueError):
            shares = 0

        try:
            reposts = float(reposts)
        except (TypeError, ValueError):
            reposts = 0

        try:
            bookmarks = float(bookmarks)
        except (TypeError, ValueError):
            bookmarks = 0

        try:
            views = float(views)
        except (TypeError, ValueError):
            views = 0

        try:
            followers = float(followers)
        except (TypeError, ValueError):
            followers = 0

        # ---------------------------------------------------------
        # PLATFORM-SPECIFIC INTERNAL METRICS
        #
        # These preserve the meaning of each platform.
        #
        # Instagram:
        #   likes, comments, shares, bookmarks, views
        #
        # Facebook:
        #   likes, comments, shares, bookmarks, views
        #
        # Twitter / X:
        #   likes, replies, reposts, bookmarks, views
        # ---------------------------------------------------------

        if "twitter" in platform_name or platform_name == "x":

            # For X:
            # replies = discussion activity
            # reposts = redistribution activity

            discussion_count = replies

            redistribution_count = reposts

        else:

            # Instagram / Facebook
            discussion_count = comments

            redistribution_count = shares

        # ---------------------------------------------------------
        # TOTAL ENGAGEMENT
        #
        # Use the metrics actually extracted.
        #
        # Replies and comments represent discussion.
        # Reposts and shares represent redistribution.
        # Bookmarks represent saving activity.
        #
        # Avoid double-counting platform aliases.
        # ---------------------------------------------------------

        if "twitter" in platform_name or platform_name == "x":

            total_engagement = (
                likes +
                replies +
                reposts +
                bookmarks
            )

        else:

            total_engagement = (
                likes +
                comments +
                shares +
                bookmarks
            )

        # ---------------------------------------------------------
        # ENGAGEMENT RATE
        # ---------------------------------------------------------

        if views > 0:

            engagement_rate = round(
                (
                    total_engagement /
                    views
                ) * 100,
                2
            )

            share_ratio = round(
                (
                    redistribution_count /
                    views
                ) * 100,
                2
            )

        else:

            engagement_rate = 0

            share_ratio = 0

        # ---------------------------------------------------------
        # FACTORS / WARNINGS
        # ---------------------------------------------------------

        factors = []

        warnings = []

        risk_factors = []

        # ---------------------------------------------------------
        # REDISTRIBUTION SIGNAL
        # ---------------------------------------------------------

        if redistribution_count > 0:

            factors.append(
                {
                    "factor":
                        "Content redistribution detected",
                    "impact":
                        "High"
                }
            )

        # ---------------------------------------------------------
        # DISCUSSION SIGNAL
        # ---------------------------------------------------------

        if discussion_count > likes:

            factors.append(
                {
                    "factor":
                        "High discussion activity",
                    "impact":
                        "Medium"
                }
            )

        # ---------------------------------------------------------
        # BOOKMARK / SAVE SIGNAL
        # ---------------------------------------------------------

        if bookmarks > 0:

            factors.append(
                {
                    "factor":
                        "Users saving content",
                    "impact":
                        "Medium"
                }
            )

        # ---------------------------------------------------------
        # PLATFORM INFLUENCE
        # ---------------------------------------------------------

        influence = "Low"

        if "instagram" in platform_name:

            influence = "High"

            if followers:

                factors.append(
                    {
                        "factor":
                            f"Instagram account influence "
                            f"({int(followers):,} followers)",
                        "impact":
                            "High"
                    }
                )

        elif "facebook" in platform_name:

            influence = "High"

        elif (
            "twitter" in platform_name
            or platform_name == "x"
        ):

            influence = "High"

            if reposts > 0:

                factors.append(
                    {
                        "factor":
                            "Twitter repost activity "
                            "increasing distribution",
                        "impact":
                            "High"
                    }
                )

        # ---------------------------------------------------------
        # NLP RISK SCORE
        # ---------------------------------------------------------

        risk_score = 0

        if content_analysis:

            risk_score = content_analysis.get(
                "risk_score",
                0
            ) or 0

            try:
                risk_score = float(
                    risk_score
                )
            except (
                TypeError,
                ValueError
            ):
                risk_score = 0

            if risk_score >= 70:

                risk_factors.append(
                    "High NLP misinformation risk"
                )

                factors.append(
                    {
                        "factor":
                            "High misinformation risk",
                        "impact":
                            "High"
                    }
                )

        # ---------------------------------------------------------
        # WARNINGS
        # ---------------------------------------------------------

        if views == 0:

            warnings.append(
                "View count unavailable"
            )

        if redistribution_count == 0:

            warnings.append(
                "No redistribution signal detected"
            )

        # ---------------------------------------------------------
        # SPREAD SCORE
        # ---------------------------------------------------------

        spread_score = 0

        # =========================================================
        # TWITTER / X FORMULA
        # =========================================================

        if (
            "twitter" in platform_name
            or platform_name == "x"
        ):

            view_score = min(
                (
                    views /
                    100000
                ) * 40,
                40
            )

            repost_score = min(
                (
                    reposts /
                    max(views, 1)
                ) * 10000,
                25
            )

            engagement_score = min(
                engagement_rate * 2,
                25
            )

            discussion_score = min(
                (
                    replies /
                    max(views, 1)
                ) * 10000,
                10
            )

            spread_score = (
                view_score +
                repost_score +
                engagement_score +
                discussion_score
            )

        # =========================================================
        # FACEBOOK / INSTAGRAM FORMULA
        # =========================================================

        else:

            if views > 0:

                spread_score += min(
                    share_ratio * 5,
                    40
                )

                spread_score += min(
                    engagement_rate * 2,
                    40
                )

            else:

                spread_score += min(
                    (
                        likes * 0.4 +
                        redistribution_count * 1.5 +
                        discussion_count * 0.8 +
                        bookmarks * 1.2
                    ) / 100,
                    70
                )

        # ---------------------------------------------------------
        # RISK CONTRIBUTION
        # ---------------------------------------------------------

        spread_score += min(
            risk_score * 0.1,
            10
        )

        # ---------------------------------------------------------
        # INSTAGRAM FOLLOWER CONTRIBUTION
        # ---------------------------------------------------------

        if "instagram" in platform_name:

            follower_score = min(
                (
                    followers /
                    1000000
                ) * 100,
                100
            )

            spread_score += min(
                follower_score * 0.2,
                20
            )

        # ---------------------------------------------------------
        # FINAL SCORE
        # ---------------------------------------------------------

        spread_score = round(
            min(
                spread_score,
                100
            ),
            2
        )

        # ---------------------------------------------------------
        # RETURN
        # ---------------------------------------------------------

        return {

            "metrics": {

                "likes":
                    likes,

                "comments":
                    comments,

                "replies":
                    replies,

                "shares":
                    shares,

                "reposts":
                    reposts,

                "bookmarks":
                    bookmarks,

                "views":
                    views,

                "followers":
                    followers,

                "engagement_rate":
                    engagement_rate,

                "share_ratio":
                    share_ratio,

                "spread_score":
                    spread_score

            },

            "factors":
                factors,

            "warnings":
                warnings,

            "risk_factors":
                risk_factors,

            "platform_influence":
                influence,

            "summary":
                self.generate_summary(
                    spread_score
                )

        }

    # -------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------

    def generate_summary(
        self,
        score
    ):

        if score >= 70:

            return (
                "High spread potential detected."
            )

        if score >= 40:

            return (
                "Moderate spread potential detected."
            )

        return (
            "Low spread potential detected."
        )


spread_factor_service = SpreadFactorService()