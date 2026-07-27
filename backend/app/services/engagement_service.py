import re



class EngagementService:



    def extract_engagement(self, text):


        data = {

            # Existing fields (keep compatibility)

            "likes": 0,

            "shares": 0,

            "comments": 0,

            "views": 0,

            "bookmarks": 0,

            "followers": 0,


            # New fields

            "platform_metrics": {

                "likes": 0,

                "comments": 0,

                "shares_or_reposts": 0,

                "views": 0,

                "saves_or_bookmarks": 0,

                "followers_or_subscribers": 0

            },

            "detected_signals": []

        }




        if not text:

            return data





        text = text.lower()


        text = re.sub(

            r"\s+",

            " ",

            text

        )





        # Likes

        data["likes"] = self.find_value(

            text,

            [

                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*likes?',

                r'likes?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]

        )





        # Shares / reposts / retweets

        data["shares"] = self.find_value(

            text,

            [

                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(shares?|reposts?|retweets?|reshares?)',

                r'(?:shares?|reposts?|retweets?|reshares?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]

        )





        # Comments / replies

        data["comments"] = self.find_value(

            text,

            [

                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(comments?|replies?)',

                r'(?:comments?|replies?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]

        )







        # Views

        data["views"] = self.find_value(

            text,

            [

                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*views?',

                r'views?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]

        )







        # Saves / bookmarks

        data["bookmarks"] = self.find_value(

            text,

            [

                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(bookmarks?|saves?|favorites?)',

                r'(?:bookmarks?|saves?|favorites?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]

        )







        # Followers / subscribers

        data["followers"] = self.find_value(

            text,

            [

                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(followers?|subscribers?)',

                r'(?:followers?|subscribers?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'

            ]

        )







        # Platform specific signals


        if re.search(r"repost|retweet|quote tweet", text):

            data["detected_signals"].append(

                "X/Twitter repost activity"

            )



        if re.search(r"save|saved|bookmark", text):

            data["detected_signals"].append(

                "Save/bookmark activity"

            )



        if re.search(r"subscriber|channel", text):

            data["detected_signals"].append(

                "YouTube audience signal"

            )



        if re.search(r"forwarded|forwarded many times", text):

            data["detected_signals"].append(

                "WhatsApp forwarding signal"

            )







        # Store extra metrics

        data["platform_metrics"] = {


            "likes": data["likes"],

            "comments": data["comments"],

            "shares_or_reposts": data["shares"],

            "views": data["views"],

            "saves_or_bookmarks": data["bookmarks"],

            "followers_or_subscribers": data["followers"]


        }




        return data








    def find_value(self, text, patterns):


        for pattern in patterns:


            match = re.search(

                pattern,

                text

            )



            if match:


                groups = match.groups()



                number = None

                suffix = None



                for group in groups:


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







    def convert_number(self, number, suffix):


        value = float(number)



        if suffix:


            suffix = suffix.lower()



            if suffix == "k":

                value *= 1000



            elif suffix == "m":

                value *= 1000000




        return int(value)







engagement_service = EngagementService()