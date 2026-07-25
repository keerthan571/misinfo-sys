import re


class EngagementService:


    def extract_engagement(self, text):

        data = {

            "likes": None,
            "shares": None,
            "comments": None,
            "views": None,
            "bookmarks": None,
            "followers": None

        }


        if not text:
            return data


        text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )



        data["likes"] = self.find_value(
            text,
            [
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*likes?',
                r'likes?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'
            ]
        )



        data["shares"] = self.find_value(
            text,
            [
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(shares?|reposts?|retweets?|reshares?)',
                r'(?:shares?|reposts?|retweets?|reshares?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'
            ]
        )



        data["comments"] = self.find_value(
            text,
            [
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*comments?',
                r'comments?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'
            ]
        )



        data["views"] = self.find_value(
            text,
            [
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*views?',
                r'views?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'
            ]
        )



        data["bookmarks"] = self.find_value(
            text,
            [
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(bookmarks?|saves?)',
                r'(?:bookmarks?|saves?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'
            ]
        )



        data["followers"] = self.find_value(
            text,
            [
                r'(\d+(?:\.\d+)?)\s*(k|m)?\s*(followers?|subscribers?)',
                r'(?:followers?|subscribers?)\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*(k|m)?'
            ]
        )


        return data





    def find_value(self, text, patterns):

        for pattern in patterns:

            match = re.search(
                pattern,
                text
            )


            if match:

                groups = match.groups()


                # Pattern: number + suffix
                if groups[0].replace('.','',1).isdigit():

                    number = groups[0]

                    suffix = groups[1] if len(groups) > 1 else None


                # Pattern: word + number + suffix
                else:

                    number = groups[1]

                    suffix = groups[2] if len(groups) > 2 else None



                return self.convert_number(
                    number,
                    suffix
                )


        return None





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