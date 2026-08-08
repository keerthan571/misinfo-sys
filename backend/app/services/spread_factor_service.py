class SpreadFactorService:


    def analyze(
        self,
        engagement,
        content_analysis=None,
        platform=None
    ):

        platform_name = str(
            platform or ""
        ).lower()


        likes = 0
        comments = 0
        shares = 0
        views = 0
        saves = 0

        followers = engagement.get(
            "followers",
            0
        )


        # =========================
        # INSTAGRAM (UNCHANGED)
        # =========================

        if "instagram" in platform_name:

            likes = engagement.get(
                "likes",
                0
            )

            comments = engagement.get(
                "comments",
                0
            )

            shares = engagement.get(
                "shares",
                0
            )

            saves = engagement.get(
                "saves",
                0
            )

            views = engagement.get(
                "views",
                0
            )



        # =========================
        # FACEBOOK
        # =========================

        elif "facebook" in platform_name:

            likes = engagement.get(
                "reactions",
                0
            )

            comments = engagement.get(
                "comments",
                0
            )

            shares = engagement.get(
                "shares",
                0
            )

            views = engagement.get(
                "views",
                0
            )



        # =========================
        # TWITTER / X
        # =========================

        elif "twitter" in platform_name or platform_name == "x":


            likes = engagement.get(
                "likes",
                0
            )


            comments = engagement.get(
                "replies",
                0
            )


            shares = engagement.get(
                "reposts",
                0
            )


            views = engagement.get(
                "views",
                0
            )


            saves = engagement.get(
                "bookmarks",
                0
            )




        factors=[]
        warnings=[]
        risk_factors=[]



        total_engagement = (
            likes +
            comments +
            shares +
            saves
        )



        if views > 0:

            engagement_rate = round(
                (total_engagement / views) * 100,
                2
            )


            share_ratio = round(
                (shares / views) * 100,
                2
            )


        else:

            engagement_rate = 0
            share_ratio = 0




        if shares > 0:

            factors.append(
                {
                    "factor":"Content redistribution detected",
                    "impact":"High"
                }
            )



        if comments > likes:

            factors.append(
                {
                    "factor":"High discussion activity",
                    "impact":"Medium"
                }
            )



        if saves > 0:

            factors.append(
                {
                    "factor":"Users saving content",
                    "impact":"Medium"
                }
            )



        influence="Low"



        if "instagram" in platform_name:

            influence="High"



            if followers:

                factors.append(
                    {
                        "factor":
                        f"Instagram account influence ({followers} followers)",
                        "impact":"High"
                    }
                )



        elif "facebook" in platform_name:

            influence="High"



        elif "twitter" in platform_name or platform_name=="x":

            influence="High"



            if shares > 0:

                factors.append(
                    {
                        "factor":
                        "Twitter repost activity increasing distribution",
                        "impact":"High"
                    }
                )





        risk_score=0



        if content_analysis:

            risk_score = content_analysis.get(
                "risk_score",
                0
            )



            if risk_score >= 70:

                risk_factors.append(
                    "High NLP misinformation risk"
                )



                factors.append(
                    {
                        "factor":
                        "High misinformation risk",
                        "impact":"High"
                    }
                )





        if views == 0:

            warnings.append(
                "View count unavailable"
            )



        if shares == 0:

            warnings.append(
                "No redistribution signal detected"
            )





        spread_score=0




        # =========================
        # TWITTER FORMULA
        # =========================

        if "twitter" in platform_name or platform_name=="x":


            view_score = min(
                (views / 100000) * 40,
                40
            )


            repost_score = min(
                (shares / max(views,1)) * 10000,
                25
            )


            engagement_score = min(
                engagement_rate * 2,
                25
            )


            discussion_score = min(
                (comments / max(views,1)) * 10000,
                10
            )


            spread_score = (
                view_score +
                repost_score +
                engagement_score +
                discussion_score
            )



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
                        likes*0.4 +
                        shares*1.5 +
                        comments*0.8 +
                        saves*1.2
                    )/100,
                    70
                )




        spread_score += min(
            risk_score*0.1,
            10
        )



        if "instagram" in platform_name:

            follower_score=min(
                (followers/1000000)*100,
                100
            )

            spread_score += min(
                follower_score*0.2,
                20
            )




        spread_score = round(
            min(
                spread_score,
                100
            ),
            2
        )




        return {


            "metrics":{


                "likes":likes,

                "comments":comments,

                "shares":shares,

                "views":views,

                "saves":saves,

                "followers":followers,

                "engagement_rate":engagement_rate,

                "share_ratio":share_ratio,

                "spread_score":spread_score

            },


            "factors":factors,


            "warnings":warnings,


            "risk_factors":risk_factors,


            "platform_influence":influence,


            "summary":self.generate_summary(
                spread_score
            )

        }




    def generate_summary(
        self,
        score
    ):


        if score >= 70:

            return "High spread potential detected."


        if score >= 40:

            return "Moderate spread potential detected."


        return "Low spread potential detected."





spread_factor_service = SpreadFactorService()