import re


class EngagementService:

    def __init__(self):

        self.platform_keywords = {

            "Instagram": {
                "likes": ["likes", "liked by"],
                "comments": ["comments", "comment"],
                "shares": ["shares", "share"],
                "saves": ["saves", "saved", "bookmark"]
            },

            "Twitter/X": {
                "likes": ["likes", "like"],
                "comments": ["replies", "reply", "comments"],
                "shares": ["reposts", "retweets", "repost", "retweet"],
                "views": ["views", "view"],
                "bookmarks": ["bookmarks", "bookmark"]
            },

            "YouTube": {
                "likes": ["likes", "like"],
                "comments": ["comments", "comment"],
                "views": ["views", "view"],
                "followers": ["subscribers", "subscriber"]
            },

            "Facebook": {
                "likes": ["likes", "reactions", "reaction"],
                "comments": ["comments", "comment"],
                "shares": ["shares", "share"]
            },

            "TikTok": {
                "likes": ["likes", "like"],
                "comments": ["comments", "comment"],
                "shares": ["shares", "share"],
                "views": ["views", "view"],
                "saves": ["favorites", "favorite", "saved"]
            }
        }



    def extract_engagement(self, text, platform="Unknown"):

        result = {

            "likes": 0,
            "shares": 0,
            "comments": 0,
            "views": 0,
            "bookmarks": 0,
            "followers": 0,

            "platform": platform,
            "metrics": []

        }


        if not text:
            return result


        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()



        detected_platform = (

            platform
            if platform in self.platform_keywords
            else self.detect_platform(text)

        )


        result["platform"] = detected_platform



        supported = self.platform_keywords.get(
            detected_platform,
            self.platform_keywords["Instagram"]
        )



        for metric, keywords in supported.items():

            value = self.find_metric(
                text,
                keywords
            )


            if value > 0:

                result["metrics"].append(
                    {
                        "label": metric.title(),
                        "value": value
                    }
                )


                if metric == "likes":
                    result["likes"] = value

                elif metric == "comments":
                    result["comments"] = value

                elif metric == "shares":
                    result["shares"] = value

                elif metric == "views":
                    result["views"] = value

                elif metric == "bookmarks":
                    result["bookmarks"] = value

                elif metric == "followers":
                    result["followers"] = value



        return result





    def find_metric(self, text, keywords):

        for keyword in keywords:


            patterns = [

                # 12K likes
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*' + keyword,


                # likes: 12K
                keyword +
                r'\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?',


                # liked by 12K
                r'liked\s*by\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]



            for pattern in patterns:


                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )


                if match:


                    number = None
                    suffix = None


                    for group in match.groups():


                        if group and re.match(
                            r"^\d+(\.\d+)?$",
                            group
                        ):

                            number = group


                        elif group and group.lower() in [
                            "k",
                            "m"
                        ]:

                            suffix = group



                    if number:

                        return self.convert_number(
                            number,
                            suffix
                        )


        return 0





    def convert_number(self, number, suffix=None):

        value = float(number)


        if suffix:

            suffix = suffix.lower()


            if suffix == "k":

                value *= 1000


            elif suffix == "m":

                value *= 1000000



        return int(value)





    def detect_platform(self, text):

        text = text.lower()


        if (
            "instagram" in text
            or "insta" in text
            or "reels" in text
        ):

            return "Instagram"



        if (
            "twitter" in text
            or "tweet" in text
            or "x.com" in text
            or "repost" in text
            or "retweet" in text
        ):

            return "Twitter/X"



        if (
            "youtube" in text
            or "subscribe" in text
            or "channel" in text
        ):

            return "YouTube"



        if "facebook" in text:

            return "Facebook"



        if (
            "tiktok" in text
            or "fyp" in text
        ):

            return "TikTok"



        return "Unknown"




engagement_service = EngagementService()