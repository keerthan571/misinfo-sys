import re

class EngagementService:

    def __init__(self):
        self.keywords={
            "likes":["likes","like","reactions","reaction"],
            "comments":["comments","comment","replies","reply"],
            "shares":["shares","share","sent","send","retweets","retweet"],
            "views":["views","view"],
            "bookmarks":["saves","save","saved","bookmarks","bookmark"]
        }

    def extract_engagement(self,text,platform="Unknown"):

        result={
            "likes":0,
            "shares":0,
            "reposts":0,
            "comments":0,
            "views":0,
            "bookmarks":0,
            "followers":None,
            "platform":platform,
            "metrics":[]
        }

        if isinstance(text,list):

            values=[]

            for value in text:
                try:
                    values.append(
                        self.parse_number(str(value))
                    )
                except:
                    continue

            if len(values)>0:
                result["likes"]=values[0]

            if len(values)>1:
                result["comments"]=values[1]

            if len(values)>2:
                result["reposts"]=values[2]

            if len(values)>3:
                result["shares"]=values[3]

            if len(values)>4:
                result["bookmarks"]=values[4]


            self.create_metrics(result)

            return result


        if not text:
            return result


        text=text.lower()
        text=re.sub(r"\s+"," ",text).strip()


        if platform=="Twitter/X":
            platform="Twitter"


        result["platform"]=platform


        if platform=="Instagram":

            self.extract_numbers(
                text,
                result,
                platform
            )

        else:

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


        self.create_metrics(result)

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


            if len(values)>=5:

                result["likes"]=values[0]
                result["comments"]=values[1]
                result["reposts"]=values[2]
                result["shares"]=values[3]
                result["bookmarks"]=values[4]


            elif len(values)==4:

                result["likes"]=values[0]
                result["comments"]=values[1]
                result["reposts"]=values[2]
                result["shares"]=values[3]


            elif len(values)==3:

                result["likes"]=values[0]
                result["comments"]=values[1]
                result["reposts"]=values[2]



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



    def create_metrics(self,result):

        result["metrics"]=[]

        for key in [
            "likes",
            "comments",
            "reposts",
            "shares",
            "views",
            "bookmarks"
        ]:

            if result[key]>0:

                label=key.title()

                if key=="reposts":
                    label="Reposts"


                result["metrics"].append(
                    {
                        "label":label,
                        "value":result[key]
                    }
                )



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


        if value[-1:].lower() in ["k","m"]:

            suffix=value[-1].lower()
            value=value[:-1]


        number=float(value)


        if suffix=="k":
            number*=1000

        elif suffix=="m":
            number*=1000000


        return int(number)



engagement_service=EngagementService()