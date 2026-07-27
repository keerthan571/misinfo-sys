class SpreadFactorService:


    def analyze(
        self,
        engagement,
        content_analysis=None,
        platform=None
    ):


        factors = []

        warnings = []

        trend_signals = []

        risk_factors = []



        likes = engagement.get("likes") or 0

        shares = engagement.get("shares") or 0

        comments = engagement.get("comments") or 0

        views = engagement.get("views") or 0

        bookmarks = engagement.get("bookmarks") or 0





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






        # Share analysis

        if share_ratio >= 5:


            factors.append({

                "factor":
                "Extremely high sharing activity",

                "impact":
                "Very High"

            })

            trend_signals.append(
                "Rapid redistribution detected"
            )



        elif share_ratio >= 2:


            factors.append({

                "factor":
                "Strong redistribution through shares",

                "impact":
                "High"

            })





        elif shares > 0:


            factors.append({

                "factor":
                "Content redistribution detected",

                "impact":
                "Medium"

            })








        # Engagement

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






        # Comments

        if comment_ratio >= 2:


            factors.append({

                "factor":
                "High discussion activity",

                "impact":
                "High"

            })








        # Saves

        if bookmarks > 0:


            factors.append({

                "factor":
                "Users saving content",

                "impact":
                "Medium"

            })









        # Platform behaviour

        platform_name = str(platform).lower()


        platform_influence = "Low"



        if "instagram" in platform_name:


            platform_influence = "Medium"


            if bookmarks > 0:


                factors.append({

                    "factor":
                    "Instagram save-based distribution",

                    "impact":
                    "Medium"

                })



        elif "twitter" in platform_name or "x" == platform_name:


            platform_influence = "High"


            if shares > likes:


                factors.append({

                    "factor":
                    "X/Twitter repost-driven spread",

                    "impact":
                    "High"

                })



        elif "youtube" in platform_name:


            platform_influence = "High"



            if views >= 10000:


                factors.append({

                    "factor":
                    "Large video audience exposure",

                    "impact":
                    "High"

                })




        elif "facebook" in platform_name:


            platform_influence = "High"



            if shares > 0:


                factors.append({

                    "factor":
                    "Facebook share-driven spread",

                    "impact":
                    "High"

                })








        # NLP influence

        if content_analysis:


            risk_score = content_analysis.get(
                "risk_score",
                0
            )


            if risk_score >= 70:


                factors.append({

                    "factor":
                    "High misinformation-style language risk",

                    "impact":
                    "High"

                })


                risk_factors.append(
                    "High NLP risk score"
                )





            emotion = content_analysis.get(
                "emotion_analysis",
                {}
            )


            scores = emotion.get(
                "scores",
                {}
            )


            emotional_score = max(

                scores.values()

            ) if scores else 0





            if emotional_score >= 70:


                factors.append({

                    "factor":
                    "Strong emotional trigger detected",

                    "impact":
                    "High"

                })



                risk_factors.append(
                    "High emotional influence"
                )






            manipulation = content_analysis.get(
                "manipulation_signals",
                []
            )


            if manipulation:


                risk_factors.extend(
                    manipulation
                )








        if views == 0:

            warnings.append(
                "View count unavailable"
            )


        if shares == 0:

            warnings.append(
                "No redistribution signal detected"
            )







        # Spread score


        spread_score = 0



        spread_score += min(

            share_ratio * 5,

            40

        )



        spread_score += min(

            engagement_rate * 2,

            30

        )



        spread_score += min(

            comment_ratio * 5,

            15

        )



        spread_score += min(

            bookmarks / 10,

            15

        )





        if content_analysis:


            spread_score += min(

                content_analysis.get(
                    "risk_score",
                    0
                ) * 0.1,

                10

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

                "shares":shares,

                "comments":comments,

                "views":views,

                "bookmarks":bookmarks,

                "engagement_rate":engagement_rate,

                "share_ratio":share_ratio,

                "comment_ratio":comment_ratio,

                "spread_score":spread_score

            },


            "factors":factors,


            "warnings":warnings,


            "trend_signals":trend_signals,


            "risk_factors":risk_factors,


            "platform_influence":platform_influence,


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
                "multiple engagement and content risk signals."

            )



        elif score >= 40 or high_count >= 1:


            return (

                "Moderate spread potential detected "
                "from available signals."

            )



        else:


            return (

                "Low spread potential detected."

            )





spread_factor_service = SpreadFactorService()