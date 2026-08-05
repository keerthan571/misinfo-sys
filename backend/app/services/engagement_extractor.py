import cv2
import pytesseract
import os
import re


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





    def find_icon(
        self,
        image,
        template_name
    ):


        template_path = os.path.join(
            TEMPLATE_DIR,
            template_name
        )


        template = cv2.imread(
            template_path,
            0
        )


        if template is None:

            print(
                "Template missing:",
                template_path
            )

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


            resized_template = cv2.resize(
                template,
                None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_CUBIC
            )


            th, tw = resized_template.shape[:2]

            gh, gw = gray.shape[:2]


            if th > gh or tw > gw:

                continue



            result = cv2.matchTemplate(
                gray,
                resized_template,
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



        if best_confidence >= 0.80:

            return best_location



        return None






    def clean_number(
        self,
        text
    ):


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







    def extract_number(
        self,
        image,
        location
    ):


        if location is None:

            return 0



        x, y = location


        h, w = image.shape[:2]



        crop = image[

            max(0,y-15):
            min(h,y+70),

            max(0,x+20):
            min(w,x+180)

        ]



        if crop.size == 0:

            return 0



        crop = cv2.resize(
            crop,
            None,
            fx=5,
            fy=5,
            interpolation=cv2.INTER_CUBIC
        )



        gray = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY
        )



        gray = cv2.threshold(
            gray,
            0,
            255,
            cv2.THRESH_BINARY +
            cv2.THRESH_OTSU
        )[1]



        text = pytesseract.image_to_string(
            gray,
            config="--psm 7"
        )


        print(
            "OCR:",
            text.strip()
        )


        return self.clean_number(
            text
        )








    def analyze(
        self,
        image
    ):


        if image is None:

            return {}



        output = {}



        for key, template in self.templates.items():


            location = self.find_icon(
                image,
                template
            )


            if location is None:

                continue



            value = self.extract_number(
                image,
                location
            )



            if value > 0:

                output[key] = value




        print(
            "FINAL ENGAGEMENT:",
            output
        )


        return output






engagement_extractor = EngagementExtractor()