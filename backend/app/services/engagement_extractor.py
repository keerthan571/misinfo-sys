import cv2
import pytesseract
import os
import re
import math
import time


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


TEMPLATE_DIR = os.path.join(
    BASE_DIR,
    "templates"
)



class EngagementExtractor:


    def __init__(self):

        self.templates = {

            "likes": "heart.png",
            "comments": "comment.png",
            "reposts": "repost.png",
            "shares": "share.png",
            "bookmarks": "bookmark.png"

        }




    def find_icon(self, image, template_name):

        template_path = os.path.join(
            TEMPLATE_DIR,
            template_name
        )


        template = cv2.imread(
            template_path,
            0
        )


        if template is None:
            return None



        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        best_confidence = 0
        best_location = None



        for scale in [
            0.5,
            0.75,
            1.0,
            1.25,
            1.5,
            2.0
        ]:


            resized = cv2.resize(
                template,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )


            th, tw = resized.shape[:2]


            if th > gray.shape[0] or tw > gray.shape[1]:
                continue



            result = cv2.matchTemplate(
                gray,
                resized,
                cv2.TM_CCOEFF_NORMED
            )


            _, confidence, _, location = cv2.minMaxLoc(
                result
            )


            if confidence > best_confidence:

                best_confidence = confidence
                best_location = location




        print(
            template_name,
            "confidence:",
            round(best_confidence,2)
        )



        if best_confidence >= 0.75:

            return best_location



        return None






    def clean_number(self, text):

        text = text.lower()

        text = text.replace(
            ",",
            ""
        )


        match = re.search(
            r"(\d+\.?\d*)\s*([km]?)",
            text
        )


        if not match:

            return 0



        number = float(
            match.group(1)
        )


        unit = match.group(2)



        if unit == "k":

            number *= 1000



        elif unit == "m":

            number *= 1000000




        return int(number)







    def extract_numbers(self, image):


        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        gray = cv2.resize(
            gray,
            None,
            fx=5,
            fy=5,
            interpolation=cv2.INTER_CUBIC
        )



        data = pytesseract.image_to_data(
            gray,
            config="--psm 11",
            output_type=pytesseract.Output.DICT
        )



        numbers = []



        for i, text in enumerate(data["text"]):


            value = self.clean_number(text)



            if value > 0:


                numbers.append({

                    "value": value,

                    "x": data["left"][i] / 5,

                    "y": data["top"][i] / 5

                })




        print(
            "NUMBERS:",
            numbers
        )



        return numbers








    def analyze(self, image):

        output = {

            "likes": 0,
            "comments": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0

        }


        if image is None:
            return output



        icons = {}



        # Detect icons

        icon_start = time.perf_counter()

        for key, template in self.templates.items():

            location = self.find_icon(
                image,
                template
            )

            if location is not None:

                icons[key] = {

                    "x": location[0],
                    "y": location[1]

                }

        icon_time = (
            time.perf_counter()
            - icon_start
        )

        print(
            "ICON DETECTION TIME:",
            round(
                icon_time,
                2
            ),
            "seconds"
        )


        ocr_start = time.perf_counter()

        numbers = self.extract_numbers(
            image
        )

        ocr_time = (
            time.perf_counter()
            - ocr_start
        )

        print(
            "ENGAGEMENT OCR TIME:",
            round(
                ocr_time,
                2
            ),
            "seconds"
        )


        print(
            "ALL DETECTED NUMBERS:",
            numbers
        )



        used = set()



        # -----------------------------
        # PRIMARY ICON BASED MATCHING
        # Works for Instagram/Twitter
        # -----------------------------

        for key, icon in icons.items():

            best_index = None
            best_distance = float("inf")



            for index, num in enumerate(numbers):

                if index in used:
                    continue



                distance = math.sqrt(

                    (icon["x"] - num["x"]) ** 2 +

                    (icon["y"] - num["y"]) ** 2

                )



                if distance < best_distance:

                    best_distance = distance
                    best_index = index




            if best_index is not None and best_distance < 350:

                output[key] = numbers[best_index]["value"]

                used.add(best_index)




        # ---------------------------------
        # Instagram fix:
        # share/bookmark are close sometimes
        # ---------------------------------

        if (
            output["shares"] > 0 and
            output["bookmarks"] > 0
        ):

            share_x = icons.get(
                "shares",
                {}
            ).get(
                "x",
                0
            )


            bookmark_x = icons.get(
                "bookmarks",
                {}
            ).get(
                "x",
                0
            )



            if share_x > bookmark_x:

                output["shares"], output["bookmarks"] = (

                    output["bookmarks"],

                    output["shares"]

                )





        # ---------------------------------
        # If bookmark icon missing
        # Use remaining unused number
        # ---------------------------------

        if output["bookmarks"] == 0:

            remaining = []


            for index,num in enumerate(numbers):

                if index not in used:

                    remaining.append(num["value"])



            if remaining:

                # Instagram last icon normally bookmark

                output["bookmarks"] = remaining[-1]





        # ---------------------------------
        # Facebook fallback ONLY
        # No icons detected
        # ---------------------------------

        if len(icons) == 0:


            values = [

                x["value"]

                for x in numbers

            ]


            if len(values) >= 3:

                output["likes"] = values[-3]

                output["comments"] = values[-2]

                output["shares"] = values[-1]





        print(
            "FINAL ENGAGEMENT:",
            output
        )


        return output





engagement_extractor = EngagementExtractor()