import cv2
import pytesseract
import re


class TwitterEngagementExtractor:


    def clean_number(self, text):

        text = text.lower()
        text = text.replace(",", "")

        match = re.search(
            r"(\d+\.?\d*)\s*([km]?)",
            text
        )

        if not match:
            return 0


        number = float(match.group(1))
        unit = match.group(2)


        if unit == "k":
            number *= 1000

        elif unit == "m":
            number *= 1000000


        return int(number)



    def extract_numbers(self, image):

        h, w = image.shape[:2]


        # bottom engagement section
        crop = image[
            int(h*0.80):h,
            0:w
        ]


        gray = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY
        )


        gray = cv2.resize(
            gray,
            None,
            fx=8,
            fy=8,
            interpolation=cv2.INTER_CUBIC
        )


        data = pytesseract.image_to_data(
            gray,
            config="--psm 11 -c tessedit_char_whitelist=0123456789KM.k",
            output_type=pytesseract.Output.DICT
        )


        numbers=[]


        for i,text in enumerate(data["text"]):

            value=self.clean_number(text)


            if value > 0:

                numbers.append({

                    "value":value,

                    "x":data["left"][i]/8,

                    "y":data["top"][i]/8 + int(h*0.80)

                })


        print(
            "TWITTER NUMBERS:",
            numbers
        )


        return numbers




    def analyze(self,image):


        result={

            "likes":0,
            "replies":0,
            "reposts":0,
            "views":0,
            "bookmarks":0,
            "shares":0

        }



        numbers=self.extract_numbers(image)



        # views

        for n in numbers:

            if n["value"] >= 1000:

                result["views"]=n["value"]




        # engagement numbers

        for n in numbers:


            value=n["value"]
            x=n["x"]



            if value >= 1000:
                continue



            # X mobile layout positions

            if x < 100:

                result["replies"]=value


            elif x >= 100 and x < 270:

                result["reposts"]=value


            elif x >= 270 and x < 480:

                result["likes"]=value


            elif x >= 480 and x < 620:

                result["bookmarks"]=value


            elif x >= 620:

                result["shares"]=value



        print(
            "FINAL TWITTER ENGAGEMENT:",
            result
        )


        return result



twitter_engagement_extractor = TwitterEngagementExtractor()