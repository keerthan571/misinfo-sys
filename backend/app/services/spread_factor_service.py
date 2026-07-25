class SpreadFactorService:


    def analyze(
        self,
        engagement,
        content_analysis=None,
        platform=None
    ):


        factors = []

        warnings = []


        likes = engagement.get("likes") or 0
        shares = engagement.get("shares") or 0
        comments = engagement.get("comments") or 0
        views = engagement.get("views") or 0
        bookmarks = engagement.get("bookmarks") or 0



        # ==========================
        # Metrics
        # ==========================


        engagement_rate = 0

        if views > 0:

            engagement_rate = round(

                (
                    likes +
                    shares +
                    comments +
                    bookmarks

                ) / views * 100,

                2
            )



        share_ratio = 0

        if views > 0:

            share_ratio = round(

                shares / views * 100,

                2

            )



        comment_ratio = 0

        if views > 0:

            comment_ratio = round(

                comments / views * 100,

                2

            )





        # ==========================
        # Share Signals
        # ==========================


        if share_ratio >= 5:


            factors.append({

                "factor":
                "Extremely high sharing activity",

                "impact":
                "Very High"

            })


        elif share_ratio >= 2:


            factors.append({

                "factor":
                "Strong redistribution through shares/reposts",

                "impact":
                "High"

            })


        elif shares > 0:


            factors.append({

                "factor":
                "Content is being redistributed",

                "impact":
                "Medium"

            })






        # ==========================
        # Engagement
        # ==========================


        if engagement_rate >= 15:


            factors.append({

                "factor":
                "Very high audience interaction",

                "impact":
                "Very High"

            })


        elif engagement_rate >= 5:


            factors.append({

                "factor":
                "Good audience interaction",

                "impact":
                "High"

            })


        elif engagement_rate > 0:


            factors.append({

                "factor":
                "Audience interaction detected",

                "impact":
                "Medium"

            })







        # ==========================
        # Comments
        # ==========================


        if comment_ratio >= 2:


            factors.append({

                "factor":
                "High discussion activity",

                "impact":
                "High"

            })







        # ==========================
        # Saves
        # ==========================


        if bookmarks > 0:


            factors.append({

                "factor":
                "Users saving this content",

                "impact":
                "Medium"

            })








        # ==========================
        # Platform Behaviour
        # ==========================


        if platform:


            platform_name = str(platform).lower()



            if "twitter" in platform_name or "x" == platform_name:


                if shares > likes:


                    factors.append({

                        "factor":
                        "Repost-driven Twitter/X spread",

                        "impact":
                        "High"

                    })




            elif "instagram" in platform_name:


                if bookmarks > 0:


                    factors.append({

                        "factor":
                        "Instagram save-based distribution",

                        "impact":
                        "Medium"

                    })





            elif "youtube" in platform_name:


                if views >= 10000:


                    factors.append({

                        "factor":
                        "Large video audience exposure",

                        "impact":
                        "High"

                    })





            elif "facebook" in platform_name:


                if shares > 0:


                    factors.append({

                        "factor":
                        "Facebook share-driven spread",

                        "impact":
                        "High"

                    })







        # ==========================
        # Content Emotion
        # ==========================


        if content_analysis:


            emotion_score = content_analysis.get(
                "emotion_score",
                0
            )


            if emotion_score >= 70:


                factors.append({

                    "factor":
                    "Strong emotional trigger detected",

                    "impact":
                    "High"

                })








        # ==========================
        # Warnings
        # ==========================


        if views == 0:

            warnings.append(
                "View count unavailable"
            )


        if shares == 0:

            warnings.append(
                "No redistribution signal detected"
            )







        # ==========================
        # Spread Score
        # ==========================


        spread_score = 0



        # Shares = strongest signal

        spread_score += min(
            share_ratio * 5,
            40
        )



        # Interaction

        spread_score += min(
            engagement_rate * 2,
            30
        )



        # Discussion

        spread_score += min(
            comment_ratio * 5,
            15
        )



        # Saves

        spread_score += min(
            bookmarks / 10,
            15
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


                "likes": likes,

                "shares": shares,

                "comments": comments,

                "views": views,

                "bookmarks": bookmarks,

                "engagement_rate": engagement_rate,

                "share_ratio": share_ratio,

                "comment_ratio": comment_ratio,

                "spread_score": spread_score

            },


            "factors": factors,


            "warnings": warnings,


            "summary":
            self.generate_summary(

                spread_score,

                factors

            )

        }





    def generate_summary(
        self,
        score,
        factors
    ):


        high_count = len([

            f for f in factors

            if f["impact"] in [
                "High",
                "Very High"
            ]

        ])



        if score >= 70 or high_count >= 3:


            return (

                "High spread potential detected due to "
                "multiple strong engagement signals."

            )



        elif score >= 40 or high_count >= 1:


            return (

                "Moderate spread potential detected "
                "based on available engagement signals."

            )



        else:


            return (

                "Low spread potential due to limited "
                "redistribution signals."

            )







spread_factor_service = SpreadFactorService()