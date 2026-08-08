import cv2
import pytesseract
import re


class FacebookEngagementExtractor:


    def clean_number(self, text):

        text = text.replace(",", "")

        numbers = re.findall(
            r"\d+",
            text
        )

        if numbers:

            return int(numbers[0])


        return 0





    def extract_numbers(self, image):

        cv2.imwrite(
            "facebook_app_debug.png",
            image
        )


        h, w = image.shape[:2]


        print(
            "FACEBOOK IMAGE SIZE:",
            image.shape
        )



        # Facebook engagement bar at bottom

        crop = image[
            int(h * 0.85):h,
            0:w
        ]



        cv2.imwrite(
            "facebook_numbers_debug.png",
            crop
        )



        h2, w2 = crop.shape[:2]


        results = []



        # Likes | Comments | Shares

        boxes = [

            crop[:, 0:int(w2 * 0.45)],

            crop[:, int(w2 * 0.45):int(w2 * 0.70)],

            crop[:, int(w2 * 0.70):w2]

        ]





        for i, box in enumerate(boxes):


            gray = cv2.cvtColor(
                box,
                cv2.COLOR_BGR2GRAY
            )



            gray = cv2.resize(
                gray,
                None,
                fx=30,
                fy=30,
                interpolation=cv2.INTER_CUBIC
            )



            _, binary = cv2.threshold(
                gray,
                160,
                255,
                cv2.THRESH_BINARY
            )



            text = pytesseract.image_to_string(
                binary,
                config="--psm 6 -c tessedit_char_whitelist=0123456789KM"
            )



            print(
                "FACEBOOK BOX",
                i,
                "OCR:",
                text
            )



            value = self.clean_number(
                text
            )



            if value > 0:

                results.append(value)




        print(
            "FACEBOOK NUMBERS:",
            results
        )



        return results








    def analyze(self, image):


        result = {

            "likes": 0,

            "comments": 0,

            "shares": 0,

            "views": 0

        }




        numbers = self.extract_numbers(
            image
        )



        print(
            "DETECTED FACEBOOK VALUES:",
            numbers
        )



        if len(numbers) >= 3:


            result["likes"] = numbers[0]

            result["comments"] = numbers[1]

            result["shares"] = numbers[2]




        print(
            "FINAL FACEBOOK ENGAGEMENT:",
            result
        )



        return result




facebook_engagement_extractor = FacebookEngagementExtractor()