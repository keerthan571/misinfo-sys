import re

class EngagementService:

    def __init__(self):
        self.keywords={
            "likes":[
                "likes",
                "like",
                "reactions",
                "reaction"
            ],
            "comments":[
                "comments",
                "comment",
                "replies",
                "reply"
            ],
            "shares":[
                "shares",
                "share",
                "reposts",
                "repost",
                "retweets",
                "retweet"
            ],
            "views":[
                "views",
                "view"
            ],
            "bookmarks":[
                "saves",
                "save",
                "saved",
                "bookmarks",
                "bookmark"
            ]
        }

    def extract_engagement(self,text,platform="Unknown"):

        result={
            "likes":0,
            "shares":0,
            "comments":0,
            "views":0,
            "bookmarks":0,
            "followers":0,
            "platform":platform,
            "metrics":[]
        }

        if not text:
            return result

        text=text.lower()
        text=re.sub(r"\s+"," ",text).strip()

        if platform=="Twitter/X":
            platform="Twitter"

        result["platform"]=platform

        for metric,words in self.keywords.items():

            value=self.find_metric(
                text,
                words
            )

            if value>0:

                result[metric]=value

        if all(
            result[x]==0
            for x in [
                "likes",
                "shares",
                "comments",
                "views",
                "bookmarks"
            ]
        ):
            self.extract_numbers(
                text,
                result,
                platform
            )

        for key in [
            "likes",
            "comments",
            "shares",
            "views",
            "bookmarks"
        ]:

            if result[key]>0:

                label=key.title()

                if platform=="Twitter" and key=="shares":
                    label="Reposts"

                result["metrics"].append(
                    {
                        "label":label,
                        "value":result[key]
                    }
                )

        return result


    def extract_numbers(self,text,result,platform):

        numbers=re.findall(
            r"\d+(?:,\d+)*(?:\.\d+)?\s*[kKmM]?",
            text
        )

        values=[]

        for number in numbers:

            value=self.parse_number(number)

            if value>0:
                values.append(value)


        if not values:
            return


        if platform=="Instagram":

            values=values[-4:]

            if len(values)>=4:

                result["likes"]=values[0]
                result["comments"]=values[1]
                result["shares"]=values[2]
                result["bookmarks"]=values[3]

            elif len(values)>=3:

                result["likes"]=values[0]
                result["comments"]=values[1]
                result["shares"]=values[2]


        elif platform=="Facebook":

            values=values[-3:]

            if len(values)>=3:

                result["likes"]=values[0]
                result["comments"]=values[1]
                result["shares"]=values[2]


        elif platform=="Twitter":

            values=values[-5:]

            if len(values)>=5:

                result["views"]=values[0]
                result["shares"]=values[1]
                result["comments"]=values[2]
                result["likes"]=values[3]
                result["bookmarks"]=values[4]

            elif len(values)>=4:

                result["views"]=values[0]
                result["shares"]=values[1]
                result["comments"]=values[2]
                result["likes"]=values[3]

            elif len(values)>=3:

                result["likes"]=values[0]
                result["shares"]=values[1]
                result["views"]=values[2]


    def find_metric(self,text,words):

        for word in words:

            patterns=[
                rf"(\d+(?:,\d+)*(?:\.\d+)?\s*[km]?)\s*{word}",
                rf"{word}\s*[:\-]?\s*(\d+(?:,\d+)*(?:\.\d+)?\s*[km]?)"
            ]

            for pattern in patterns:

                match=re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

                if match:

                    return self.parse_number(
                        match.group(1)
                    )

        return 0


    def parse_number(self,value):

        value=value.replace(",","").strip()

        suffix=""

        if value[-1:].lower() in [
            "k",
            "m"
        ]:

            suffix=value[-1].lower()
            value=value[:-1]


        number=float(value)

        if suffix=="k":
            number*=1000

        elif suffix=="m":
            number*=1000000


        return int(number)


engagement_service=EngagementService()