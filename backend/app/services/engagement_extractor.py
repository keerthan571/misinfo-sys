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
            round(best_confidence, 2)
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
    
        gray = cv2.cvt(
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

        tesseract_start = time.perf_counter()

        data = pytesseract.image_to_data(
            gray,
            config="--psm 11",
            output_type=pytesseract.Output.DICT
        )

        tesseract_time = (
            time.perf_counter()
            - tesseract_start
        )

        print(
            "TESSERACT TIME:",
            round(
                tesseract_time,
                2
            ),
            "seconds"
        )

    def extract_numbers_fast(
        self,
        image,
        icons
    ):

        """
        Fast OCR path.

        Uses the detected icon positions to create a safe
        engagement-area crop.

        OCR settings remain identical to the original
        implementation.
        """

        if not icons:

            return None


        height, width = image.shape[:2]


        icon_positions = []

        for icon in icons.values():

            icon_positions.append(
                (
                    icon["x"],
                    icon["y"]
                )
            )


        if not icon_positions:

            return None


        min_x = min(
            position[0]
            for position in icon_positions
        )

        max_x = max(
            position[0]
            for position in icon_positions
        )

        min_y = min(
            position[1]
            for position in icon_positions
        )

        max_y = max(
            position[1]
            for position in icon_positions
        )


        # Engagement numbers normally occur around the
        # detected action icons.
        #
        # Generous padding is deliberately used so that
        # numbers are not accidentally cut off.

        padding_x = int(
            width * 0.08
        )

        padding_y = int(
            height * 0.08
        )


        x1 = max(
            0,
            int(min_x - padding_x)
        )

        x2 = min(
            width,
            int(max_x + padding_x)
        )

        y1 = max(
            0,
            int(min_y - padding_y)
        )

        y2 = min(
            height,
            int(max_y + padding_y)
        )


        crop_width = x2 - x1
        crop_height = y2 - y1


        # Do not use a suspiciously small crop.
        # If the crop is too small, let the original
        # full-image OCR handle it.

        if (
            crop_width < width * 0.20
            or crop_height < height * 0.05
        ):

            return None


        crop = image[
            y1:y2,
            x1:x2
        ]


        if crop.size == 0:

            return None


        gray = cv2.cvtColor(
            crop,
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


        for i, text in enumerate(
            data["text"]
        ):

            value = self.clean_number(
                text
            )


            if value > 0:

                numbers.append({

                    "value":
                        value,

                    "x":
                        (
                            data["left"][i] / 5
                            + x1
                        ),

                    "y":
                        (
                            data["top"][i] / 5
                            + y1
                        )

                })


        print(
            "FAST OCR NUMBERS:",
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


        # -------------------------------------------------
        # ICON DETECTION
        # -------------------------------------------------

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


        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        ocr_start = time.perf_counter()


        numbers = None


        # -------------------------------------------------
        # FAST OCR
        # -------------------------------------------------

        if icons:

            try:

                numbers = self.extract_numbers_fast(
                    image,
                    icons
                )

            except Exception:

                print(
                    "FAST OCR FAILED - "
                    "falling back to full-image OCR"
                )

                numbers = None


        # -------------------------------------------------
        # QUALITY-PRESERVING FALLBACK
        # -------------------------------------------------

        if numbers is None:

            print(
                "Using full-image OCR fallback."
            )

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


        # -------------------------------------------------
        # PRIMARY ICON BASED MATCHING
        # -------------------------------------------------

        for key, icon in icons.items():

            best_index = None

            best_distance = float(
                "inf"
            )


            for index, num in enumerate(
                numbers
            ):

                if index in used:

                    continue


                distance = math.sqrt(

                    (
                        icon["x"]
                        - num["x"]
                    ) ** 2

                    +

                    (
                        icon["y"]
                        - num["y"]
                    ) ** 2

                )


                if distance < best_distance:

                    best_distance = distance

                    best_index = index


            if (
                best_index is not None
                and best_distance < 350
            ):

                output[key] = (
                    numbers[best_index]["value"]
                )

                used.add(
                    best_index
                )


        # -------------------------------------------------
        # INSTAGRAM SHARE / BOOKMARK FIX
        # -------------------------------------------------

        if (
            output["shares"] > 0
            and output["bookmarks"] > 0
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

                (
                    output["shares"],
                    output["bookmarks"]
                ) = (

                    output["bookmarks"],

                    output["shares"]

                )


        # -------------------------------------------------
        # BOOKMARK FALLBACK
        # -------------------------------------------------

        if output["bookmarks"] == 0:

            remaining = []


            for index, num in enumerate(
                numbers
            ):

                if index not in used:

                    remaining.append(
                        num["value"]
                    )


            if remaining:

                output["bookmarks"] = (
                    remaining[-1]
                )


        # -------------------------------------------------
        # FACEBOOK FALLBACK
        # -------------------------------------------------

        if len(icons) == 0:

            values = [

                x["value"]

                for x in numbers

            ]


            if len(values) >= 3:

                output["likes"] = (
                    values[-3]
                )

                output["comments"] = (
                    values[-2]
                )

                output["shares"] = (
                    values[-1]
                )


        print(
            "FINAL ENGAGEMENT:",
            output
        )


        return output


engagement_extractor = EngagementExtractor()