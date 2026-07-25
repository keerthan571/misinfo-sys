import re


class PlatformDetector:

    def __init__(self):

        self.platform_patterns = {

            "Instagram": {

                "strong": [
                    r"instagram",
                    r"insta",
                    r"reels?",
                    r"followers?",
                    r"following"
                ],

                "engagement": [
                    r"likes?",
                    r"comments?",
                    r"shares?",
                    r"saves?"
                ]
            },


            "Twitter/X": {

                "strong": [
                    r"twitter",
                    r"x\.com",
                    r"tweet",
                    r"reposts?",
                    r"retweets?",
                    r"quote tweets?"
                ],

                "engagement": [
                    r"likes?",
                    r"views?",
                    r"bookmarks?",
                    r"replies?"
                ]
            },


            "YouTube": {

                "strong": [
                    r"youtube",
                    r"youtu\.be",
                    r"subscribers?",
                    r"channel"
                ],

                "engagement": [
                    r"views?",
                    r"likes?",
                    r"comments?"
                ]
            },


            "Facebook": {

                "strong": [
                    r"facebook",
                    r"fb",
                    r"reactions?"
                ],

                "engagement": [
                    r"likes?",
                    r"shares?",
                    r"comments?",
                    r"followers?"
                ]
            },


            "TikTok": {

                "strong": [
                    r"tiktok",
                    r"tt",
                    r"followers?"
                ],

                "engagement": [
                    r"likes?",
                    r"favorites?",
                    r"shares?",
                    r"views?"
                ]
            }

        }



    def detect_platform(self, text):

        if not text:

            return {

                "platform": "Unknown",
                "confidence": 0,
                "matched_signals": [],
                "engagement_supported": []

            }


        text = text.lower()


        scores = {}

        matched = {}



        for platform,data in self.platform_patterns.items():

            score = 0

            signals = []


            # Strong indicators
            for pattern in data["strong"]:

                if re.search(pattern,text):

                    score += 3

                    signals.append(pattern)



            # Engagement indicators
            for pattern in data["engagement"]:

                if re.search(pattern,text):

                    score += 1

                    signals.append(pattern)



            scores[platform]=score

            matched[platform]=signals




        best_platform=max(
            scores,
            key=scores.get
        )


        best_score=scores[best_platform]



        if best_score==0:

            return {

                "platform":"Unknown",

                "confidence":0,

                "matched_signals":[],

                "engagement_supported":[],

                "all_scores":scores

            }



        # Better confidence calculation

        confidence=min(
            round((best_score/10)*100,2),
            95
        )



        return {


            "platform":best_platform,


            "confidence":confidence,


            "matched_signals":
            matched[best_platform],



            "engagement_supported":
            self.platform_patterns[best_platform]["engagement"],



            "all_scores":scores

        }



platform_detector = PlatformDetector()