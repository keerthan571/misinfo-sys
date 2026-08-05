import cv2
import pytesseract
import re


class TwitterViewsDetector:


    def clean_number(self,text):

        text=text.lower()
        text=text.replace(",","")


        match=re.search(
            r"(\d+\.?\d*)\s*([km]?)",
            text
        )


        if not match:
            return 0


        number=float(match.group(1))
        unit=match.group(2)


        if unit=="k":
            number*=1000

        elif unit=="m":
            number*=1000000


        return int(number)



    def detect(self,image):

        h,w=image.shape[:2]


        crop=image[
            0:h,
            0:w
        ]


        gray=cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY
        )


        gray=cv2.resize(
            gray,
            None,
            fx=5,
            fy=5,
            interpolation=cv2.INTER_CUBIC
        )


        data=pytesseract.image_to_data(
            gray,
            config="--psm 11",
            output_type=pytesseract.Output.DICT
        )


        views=0


        print("OCR TEXT:",data["text"])


        for text in data["text"]:

            value=self.clean_number(text)


            if value>=1000 and value<100000:

                views=value



        print(
            "TWITTER VIEWS:",
            views
        )


        return views



twitter_views_detector=TwitterViewsDetector()