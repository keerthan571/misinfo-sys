import re



class PlatformDetector:


    def __init__(self):


        self.platform_patterns = {


            "Instagram": {


                "strong": [

                    r"\binstagram\b",
                    r"\binsta\b",
                    r"\breels?\b",
                    r"\bstory\b",
                    r"\bstories\b",
                    r"\bfollowers?\b",
                    r"\bfollowing\b",
                    r"\bprofile\b",
                    r"\bexplore\b"

                ],


                "engagement": [

                    r"\blikes?\b",
                    r"\bcomments?\b",
                    r"\bshares?\b",
                    r"\bsaves?\b"

                ],


                "unique": [

                    r"liked by",
                    r"view insights",
                    r"add comment",
                    r"send message"

                ]

            },





            "Twitter/X": {


                "strong": [

                    r"\btwitter\b",
                    r"\bx\.com\b",
                    r"\btweet\b",
                    r"\bpost\b",
                    r"\breposts?\b",
                    r"\bretweets?\b",
                    r"\bquote tweet\b"

                ],


                "engagement": [

                    r"\blikes?\b",
                    r"\bviews?\b",
                    r"\breplies?\b",
                    r"\bbookmarks?\b"

                ],


                "unique": [

                    r"reply",
                    r"repost",
                    r"quote",
                    r"verified"

                ]

            },






            "YouTube": {


                "strong": [

                    r"\byoutube\b",
                    r"\byoutu\.be\b",
                    r"\bchannel\b",
                    r"\bsubscribe\b",
                    r"\bsubscribers?\b",
                    r"\bvideo\b"

                ],


                "engagement": [

                    r"\bviews?\b",
                    r"\blikes?\b",
                    r"\bcomments?\b"

                ],


                "unique": [

                    r"watch later",
                    r"youtube studio",
                    r"live"

                ]

            },







            "Facebook": {


                "strong": [

                    r"\bfacebook\b",
                    r"\bfb\b",
                    r"\breactions?\b",
                    r"\btimeline\b",
                    r"\bprofile\b",
                    r"\bpage\b"

                ],


                "engagement": [

                    r"\blikes?\b",
                    r"\bshares?\b",
                    r"\bcomments?\b",
                    r"\breactions?\b"

                ],


                "unique": [

                    r"like react share",
                    r"feeling",
                    r"write something"

                ]

            },








            "TikTok": {


                "strong": [

                    r"\btiktok\b",
                    r"\btt\b",
                    r"\bfor you\b",
                    r"\bfyp\b"

                ],


                "engagement": [

                    r"\blikes?\b",
                    r"\bcomments?\b",
                    r"\bfavorites?\b",
                    r"\bviews?\b",
                    r"\bshares?\b"

                ],


                "unique": [

                    r"following",
                    r"discover"

                ]

            },








            "WhatsApp": {


                "strong": [

                    r"whatsapp",
                    r"forwarded",
                    r"forwarded many times",
                    r"group chat"

                ],


                "engagement": [

                    r"forwards?",
                    r"messages?"

                ],


                "unique": [

                    r"end-to-end encrypted",
                    r"typing",
                    r"online"

                ]

            }


        }







    def detect_platform(self, text):


        if not text:


            return {

                "platform":"Unknown",

                "confidence":0,

                "matched_signals":[],

                "engagement_supported":[],

                "all_scores":{}

            }





        text = text.lower()



        scores = {}

        matched = {}





        for platform, data in self.platform_patterns.items():


            score = 0

            signals = []





            # Strong signals

            for pattern in data["strong"]:


                if re.search(pattern,text):


                    score += 4

                    signals.append(
                        pattern
                    )





            # Engagement signals

            for pattern in data["engagement"]:


                if re.search(pattern,text):


                    score += 1

                    signals.append(
                        pattern
                    )







            # Unique UI signals

            for pattern in data["unique"]:


                if re.search(pattern,text):


                    score += 5

                    signals.append(
                        pattern
                    )






            scores[platform] = score

            matched[platform] = signals







        best_platform = max(

            scores,

            key=scores.get

        )



        best_score = scores[best_platform]






        if best_score == 0:


            return {

                "platform":"Unknown",

                "confidence":0,

                "matched_signals":[],

                "engagement_supported":[],

                "all_scores":scores

            }







        # confidence calculation


        confidence = min(

            round(

                (best_score / 20) * 100,

                2

            ),

            98

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