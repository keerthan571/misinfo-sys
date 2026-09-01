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


    def find_icon(
        self,
        image,
        template_name,
        threshold=0.75
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


        if best_confidence >= threshold:

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

        original_width = gray.shape[1]
        original_height = gray.shape[0]

        scale = 5

        target_width = original_width * scale
        target_height = original_height * scale

        # Keep OCR image reasonably small for Render.
        max_dimension = 2000

        longest_side = max(
            target_width,
            target_height
        )

        if longest_side > max_dimension:

            ratio = (
                max_dimension /
                longest_side
            )

            target_width = max(
                1,
                int(target_width * ratio)
            )

            target_height = max(
                1,
                int(target_height * ratio)
            )

        gray = cv2.resize(
            gray,
            (
                target_width,
                target_height
            ),
            interpolation=cv2.INTER_CUBIC
        )

        scale_x = (
            target_width /
            original_width
        )

        scale_y = (
            target_height /
            original_height
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

        numbers = []

        for i, text in enumerate(
            data["text"]
        ):

            value = self.clean_number(
                text
            )

            if value > 0:

                numbers.append(
                    {
                        "value": value,

                        "x": (
                            data["left"][i]
                            / scale_x
                        ),

                        "y": (
                            data["top"][i]
                            / scale_y
                        )
                    }
                )

        print(
            "NUMBERS:",
            numbers
        )

        return numbers
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
       
        scale = 5

        target_width = gray.shape[1] * scale
        target_height = gray.shape[0] * scale

        max_dimension = 3000

        longest_side = max(
            target_width,
            target_height
        )

        if longest_side > max_dimension:

            ratio = (
                max_dimension /
                longest_side
            )

            target_width = max(
                1,
                int(target_width * ratio)
            )

            target_height = max(
                1,
                int(target_height * ratio)
            )

        gray = cv2.resize(
            gray,
            (
                target_width,
                target_height
            ),
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


    # ============================================================
    # INSTAGRAM-SPECIFIC MATCHING
    # ============================================================

    def detect_instagram_layout(self, icons):
        """
        Detect whether Instagram screenshot is:

        1. Vertical / Reels layout
           Engagement icons arranged vertically.

        2. Horizontal / Feed layout
           Engagement icons arranged horizontally.

        Returns:
            "vertical"
            "horizontal"
            None
        """

        if len(icons) < 2:
            return None

        positions = [
            (icon["x"], icon["y"])
            for icon in icons.values()
        ]

        xs = [p[0] for p in positions]
        ys = [p[1] for p in positions]

        x_range = max(xs) - min(xs)
        y_range = max(ys) - min(ys)

        # Instagram Reels:
        # icons are stacked vertically.
        if y_range > x_range * 1.5:
            return "vertical"

        # Instagram Feed:
        # icons are arranged horizontally.
        if x_range > y_range * 1.5:
            return "horizontal"

        return None

    def extract_instagram_feed_numbers(
        self,
        image,
        icons
    ):
        """
        Instagram Feed engagement OCR.

        Feed layout:

            ❤️ 123K
            💬 68
            🔁 166
            ✈️ 154
            🔖

        Each value is OCR'd from a region to the RIGHT
        of its corresponding icon.
        """

        numbers = {}

        height, width = image.shape[:2]

        for key in [
            "likes",
            "comments",
            "reposts",
            "shares",
        ]:

            if key not in icons:
                continue

            icon_x = int(
                icons[key]["x"]
            )

            icon_y = int(
                icons[key]["y"]
            )

            # ------------------------------------------------
            # IMPORTANT
            #
            # Start farther to the right of the icon.
            #
            # The previous crop started too close to the
            # icon and interfered with the first digit.
            # ------------------------------------------------

            x1 = max(
                0,
                icon_x + 45
            )

            x2 = min(
                width,
                icon_x + 145
            )

            # Numbers are horizontally aligned with icons.

            y1 = max(
                0,
                icon_y - 20
            )

            y2 = min(
                height,
                icon_y + 75
            )

            crop = image[
                y1:y2,
                x1:x2
            ]

            if crop.size == 0:
                continue

            gray = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2GRAY
            )

            # ------------------------------------------------
            # Upscale
            # ------------------------------------------------

            gray = cv2.resize(
                gray,
                None,
                fx=7,
                fy=7,
                interpolation=cv2.INTER_CUBIC
            )

            # ------------------------------------------------
            # OCR
            #
            # Try normal grayscale first.
            # This works well with Instagram's white text.
            # ------------------------------------------------

            text = pytesseract.image_to_string(
                gray,
                config=(
                    "--psm 7 "
                    "-c tessedit_char_whitelist="
                    "0123456789KkMm"
                )
            ).strip()

            value = self.clean_number(
                text
            )

            # ------------------------------------------------
            # Threshold fallback
            # ------------------------------------------------

            if value == 0:

                thresholded = cv2.threshold(
                    gray,
                    0,
                    255,
                    cv2.THRESH_BINARY
                    + cv2.THRESH_OTSU
                )[1]

                text = pytesseract.image_to_string(
                    thresholded,
                    config=(
                        "--psm 7 "
                        "-c tessedit_char_whitelist="
                        "0123456789KkMm"
                    )
                ).strip()

                value = self.clean_number(
                    text
                )

            print(
                "INSTAGRAM FEED OCR:",
                key,
                "raw=",
                repr(text),
                "value=",
                value
            )

            if value > 0:

                numbers[key] = value

        print(
            "INSTAGRAM FEED NUMBERS:",
            numbers
        )

        return numbers
    
    def extract_instagram_reel_numbers(
        self,
        image,
        icons=None
    ):
        """
        Instagram Reel engagement extraction.

        Uses fixed relative slots for the Instagram Reel
        engagement numbers and performs OCR on each slot
        independently.

        Expected order:

            likes
            comments
            reposts
            shares
            bookmarks
        """

        height, width = image.shape[:2]

        keys = [
            "likes",
            "comments",
            "reposts",
            "shares",
            "bookmarks",
        ]

        output = {
            "likes": 0,
            "comments": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0,
        }

        # ============================================================
        # NUMBER COLUMN
        # ============================================================

        # Actual Reel numbers are around x=610-705 on a 720px image.
        #
        # Use relative coordinates so resizing the screenshot
        # does not break extraction.

        x1 = int(width * 0.847)
        x2 = int(width * 0.986)

        # ============================================================
        # NUMBER SLOT CENTERS
        # ============================================================

        slot_centers = [
            0.403,   # likes
            0.506,   # comments
            0.609,   # reposts
            0.713,   # shares
            0.815,   # bookmarks
        ]

        # Number text is roughly 30-35px tall in the original
        # 720x1313 screenshot.

        slot_half_height = max(
            28,
            int(height * 0.025)
        )

        # ============================================================
        # OCR EACH SLOT
        # ============================================================

        for key, relative_y in zip(
            keys,
            slot_centers
        ):

            center_y = int(
                height * relative_y
            )

            y1 = max(
                0,
                center_y - slot_half_height
            )

            y2 = min(
                height,
                center_y + slot_half_height
            )

            crop = image[
                y1:y2,
                x1:x2
            ]

            if crop.size == 0:
                continue

            # --------------------------------------------------------
            # GRAYSCALE
            # --------------------------------------------------------

            gray = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2GRAY
            )

            # --------------------------------------------------------
            # UPSCALE
            # --------------------------------------------------------

            gray = cv2.resize(
                gray,
                None,
                fx=10,
                fy=10,
                interpolation=cv2.INTER_CUBIC
            )

            # ========================================================
            # OCR STRATEGY
            # ========================================================
            #
            # For these isolated Instagram labels, PSM 7 is the
            # most stable configuration.
            #
            # Try several thresholds and count their results.
            # ========================================================

            candidates = []

            # --------------------------------------------------------
            # Grayscale
            # --------------------------------------------------------

            for psm in [6, 7, 10, 11]:

                text = pytesseract.image_to_string(
                    gray,
                    config=(
                        f"--psm {psm} "
                        "-c tessedit_char_whitelist="
                        "0123456789KkMm"
                    )
                ).strip()

                value = self.clean_number(
                    text
                )

                if value > 0:

                    candidates.append(
                        value
                    )

            # --------------------------------------------------------
            # Binary threshold
            # --------------------------------------------------------

            for threshold_value in [
                150,
                170,
                190,
                210,
                225,
            ]:

                thresholded = cv2.threshold(
                    gray,
                    threshold_value,
                    255,
                    cv2.THRESH_BINARY
                )[1]

                for psm in [6, 7, 10]:

                    text = pytesseract.image_to_string(
                        thresholded,
                        config=(
                            f"--psm {psm} "
                            "-c tessedit_char_whitelist="
                            "0123456789KkMm"
                        )
                    ).strip()

                    value = self.clean_number(
                        text
                    )

                    if value > 0:

                        candidates.append(
                            value
                        )

            # ========================================================
            # SELECT RESULT
            # ========================================================

            if candidates:

                from collections import Counter

                counts = Counter(
                    candidates
                )

                best_value, best_count = (
                    counts.most_common(1)[0]
                )

                output[key] = best_value

                print(
                    "INSTAGRAM REEL SLOT:",
                    key,
                    "center_y=",
                    center_y,
                    "value=",
                    best_value,
                    "votes=",
                    best_count,
                    "candidates=",
                    dict(counts)
                )

            else:

                print(
                    "INSTAGRAM REEL SLOT:",
                    key,
                    "center_y=",
                    center_y,
                    "OCR FAILED"
                )

        # ============================================================
        # FINAL
        # ============================================================

        print(
            "INSTAGRAM REEL NUMBERS:",
            output
        )

        return output
    def match_instagram_engagement(
        self,
        image,
        icons,
        numbers
    ):
        """
        Instagram-specific engagement mapping.

        Supports two Instagram layouts:

        1. Vertical / Reels

               ❤️
               3238
               💬
               6
               🔁
               46
               ✈️
               290
               🔖
               471

        2. Horizontal / Feed

               ❤️ 123K
               💬 68
               🔁 166
               ✈️ 154
               🔖

        Facebook and Twitter are NOT handled here.
        """

        output = {
            "likes": 0,
            "comments": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0,
        }

        if not icons:
            return output

        layout = self.detect_instagram_layout(
            icons
        )

        print(
            "INSTAGRAM LAYOUT:",
            layout
        )

        # ========================================================
        # INSTAGRAM FEED / HORIZONTAL
        # ========================================================
        #
        # DO NOT use the global OCR numbers here.
        #
        # Each engagement number is extracted directly from
        # the region beside its own icon.
        # ========================================================

        if layout == "horizontal":

            feed_numbers = (
                self.extract_instagram_feed_numbers(
                    image,
                    icons
                )
            )

            output["likes"] = feed_numbers.get(
                "likes",
                0
            )

            output["comments"] = feed_numbers.get(
                "comments",
                0
            )

            output["reposts"] = feed_numbers.get(
                "reposts",
                0
            )

            output["shares"] = feed_numbers.get(
                "shares",
                0
            )

            # ------------------------------------------------
            # Instagram Feed does not show a bookmark count.
            #
            # Therefore NEVER infer bookmark from another
            # number.
            # ------------------------------------------------

            output["bookmarks"] = 0

            print(
                "FINAL INSTAGRAM FEED ENGAGEMENT:",
                output
            )

            return output

        # ========================================================
        # INSTAGRAM REELS / VERTICAL
        # ========================================================
        #
        # Keep the existing spatial mapping for Reels.
        # ========================================================
         
        if layout == "vertical":
    
            reel_numbers = (
                self.extract_instagram_reel_numbers(
                    image,
                    icons
                )
            )

            output["likes"] = reel_numbers.get(
                "likes",
                0
            )

            output["comments"] = reel_numbers.get(
                "comments",
                0
            )

            output["reposts"] = reel_numbers.get(
                "reposts",
                0
            )

            output["shares"] = reel_numbers.get(
                "shares",
                0
            )

            output["bookmarks"] = reel_numbers.get(
                "bookmarks",
                0
            )

            print(
                "FINAL INSTAGRAM REEL ENGAGEMENT:",
                output
            )

            return output
        
        # ========================================================
        # UNKNOWN LAYOUT
        # ========================================================

        print(
            "INSTAGRAM LAYOUT UNKNOWN - "
            "returning zero engagement values."
        )

        return output

    # ============================================================
    # MAIN ANALYSIS
    # ============================================================

    def analyze(
        self,
        image,
        platform=None
    ):

        output = {
            "likes": 0,
            "comments": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0
        }

        if image is None:
            return output

        # -------------------------------------------------
        # NORMALIZE PLATFORM
        # -------------------------------------------------

        normalized_platform = str(
            platform or ""
        ).strip().lower()

        # -------------------------------------------------
        # ICON DETECTION
        # -------------------------------------------------

        icons = {}

        # Instagram screenshots can have slightly weaker
        # template confidence because of compression,
        # scaling and Instagram's dark UI.

        icon_threshold = (
            0.60
            if normalized_platform == "instagram"
            else 0.75
        )

        for key, template in self.templates.items():

            location = self.find_icon(
                image,
                template,
                threshold=icon_threshold
            )

            if location is not None:

                icons[key] = {
                    "x": location[0],
                    "y": location[1]
                }
                
        print(
            "INSTAGRAM ICON POSITIONS:",
            icons
        )
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
        # FULL OCR FALLBACK
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

        # =================================================
        # INSTAGRAM
        # =================================================
        #
        # Instagram has two layouts:
        #
        # Reels:
        #     icon
        #       ↓
        #     number
        #
        # Feed:
        #     icon → number
        #
        # Use the dedicated Instagram mapper.
        # =================================================

        if normalized_platform == "instagram":

            output = self.match_instagram_engagement(
                image,
                icons,
                numbers
            )

            print(
                "FINAL INSTAGRAM ENGAGEMENT:",
                output
            )

            return output

        # =================================================
        # FACEBOOK / OTHER EXISTING LOGIC
        # =================================================
        #
        # IMPORTANT:
        # Keep existing behaviour unchanged.
        # =================================================

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
        # EXISTING SHARE / BOOKMARK FIX
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
        # EXISTING BOOKMARK FALLBACK
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
        # EXISTING FACEBOOK FALLBACK
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