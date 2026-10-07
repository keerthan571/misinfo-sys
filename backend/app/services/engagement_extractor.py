import cv2
import pytesseract
import os
import re
import math
import time
import numpy as np

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

    def find_instagram_icon(
        self,
        image,
        template_name,
        threshold=0.60
    ):
        """
        Find Instagram Reel engagement icons only
        inside the right-side action rail.

        This prevents icons inside the actual post/content
        from being mistaken for Instagram UI icons.
        """

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

        height, width = image.shape[:2]

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        # ---------------------------------------------------------
        # Instagram Reel action rail is on the right side.
        #
        # Ignore the main content area.
        # ---------------------------------------------------------

        x1 = int(
            width * 0.78
        )

        x2 = width

        y1 = int(
            height * 0.25
        )

        y2 = int(
            height * 0.85
        )

        rail = gray[
            y1:y2,
            x1:x2
        ]

        best_confidence = 0
        best_location = None

        best_scale = None

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

            if (
                th > rail.shape[0]
                or tw > rail.shape[1]
            ):
                continue

            result = cv2.matchTemplate(
                rail,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            _, confidence, _, location = (
                cv2.minMaxLoc(result)
            )

            if confidence > best_confidence:

                best_confidence = confidence

                best_location = location

                best_scale = scale

        print(
            "INSTAGRAM RAIL ICON:",
            template_name,
            "confidence=",
            round(best_confidence, 3),
            "scale=",
            best_scale
        )

        if (
            best_location is not None
            and best_confidence >= threshold
        ):

            return (
                best_location[0] + x1,
                best_location[1] + y1
            )

        return None

    def find_icon_region(
        self,
        image,
        template_name,
        region,
        threshold=0.75
    ):
        """
        Run template matching only inside a known UI region.

        This is important for Instagram because searching the
        whole screenshot can match a visually similar shape in
        the post image instead of the real engagement icon.
        """

        x1, y1, x2, y2 = [int(v) for v in region]

        height, width = image.shape[:2]

        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        if x2 <= x1 or y2 <= y1:
            return None

        crop = image[y1:y2, x1:x2]

        location = self.find_icon(
            crop,
            template_name,
            threshold=threshold
        )

        if location is None:
            return None

        return (
            location[0] + x1,
            location[1] + y1
        )

    def find_reel_icon_candidates(
        self,
        image,
        template_name,
        region,
        threshold=0.45
    ):
        """
        Find ALL reasonably good template matches for an Instagram
        Reel engagement icon inside the supplied region.

        Unlike find_icon(), this does NOT use minMaxLoc() to keep
        only one match.

        The Reel detector needs multiple candidates because the
        highest-scoring match is not necessarily the real engagement
        icon.
        """

        x1, y1, x2, y2 = [
            int(v)
            for v in region
        ]

        height, width = image.shape[:2]

        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))
        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        if (
            x2 <= x1
            or y2 <= y1
        ):
            return []

        crop = image[
            y1:y2,
            x1:x2
        ]

        template_path = os.path.join(
            TEMPLATE_DIR,
            template_name
        )

        template = cv2.imread(
            template_path,
            0
        )

        if template is None:
            return []

        gray = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2GRAY
        )

        candidates = []

        # ---------------------------------------------------------
        # Search at the same scales already used by find_icon()
        # ---------------------------------------------------------

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

            if (
                th > gray.shape[0]
                or tw > gray.shape[1]
            ):
                continue

            result = cv2.matchTemplate(
                gray,
                resized,
                cv2.TM_CCOEFF_NORMED
            )

            # -----------------------------------------------------
            # Find all locations above threshold.
            # -----------------------------------------------------

            ys, xs = np.where(
                result >= threshold
            )

            for local_y, local_x in zip(
                ys,
                xs
            ):

                confidence = float(
                    result[
                        local_y,
                        local_x
                    ]
                )

                candidates.append({
                    "x": float(
                        local_x + x1
                    ),
                    "y": float(
                        local_y + y1
                    ),
                    "confidence": confidence,
                    "scale": scale
                })

        # ---------------------------------------------------------
        # Non-maximum suppression.
        #
        # The same icon can produce many nearby matches at
        # different pixels/scales. Keep the strongest one.
        # ---------------------------------------------------------

        candidates.sort(
            key=lambda item:
                item["confidence"],
            reverse=True
        )

        filtered = []

        for candidate in candidates:

            too_close = False

            for existing in filtered:

                distance = math.sqrt(

                    (
                        candidate["x"]
                        -
                        existing["x"]
                    ) ** 2

                    +

                    (
                        candidate["y"]
                        -
                        existing["y"]
                    ) ** 2

                )

                if distance < 35:

                    too_close = True
                    break

            if not too_close:

                filtered.append(
                    candidate
                )

        # ---------------------------------------------------------
        # Convert crop coordinates to full-image coordinates.
        # ---------------------------------------------------------

        print(
            "REEL ICON CANDIDATES:",
            template_name,
            filtered
        )

        return filtered

    def detect_instagram_reel_icons(
        self,
        image,
        reel_region,
        threshold=0.45
    ):
        """
        Detect Instagram Reel engagement icons.

        Strategy:

            1. Collect ALL template candidates.
            2. Build X-axis clusters.
            3. For every X cluster, find the strongest vertical sequence.
            4. Reject isolated candidates far away from that sequence.
            5. For each icon type, choose the candidate closest to
            the selected rail.
            6. Return one position per icon.

        The important point is that a high-confidence false match
        must NOT beat a geometrically consistent Reel rail.
        """

        # =========================================================
        # STEP 1
        # Collect ALL candidates
        # =========================================================

        all_candidates = {}

        for key, template in self.templates.items():

            candidates = self.find_reel_icon_candidates(
                image,
                template,
                reel_region,
                threshold=threshold
            )

            all_candidates[key] = candidates

        print(
            "INSTAGRAM REEL ALL ICON CANDIDATES:",
            all_candidates
        )

        # =========================================================
        # Flatten
        # =========================================================

        points = []

        for key, candidates in all_candidates.items():

            for candidate in candidates:

                if not isinstance(candidate, dict):
                    continue

                if (
                    "x" not in candidate
                    or "y" not in candidate
                ):
                    continue

                points.append({
                    "key": key,
                    "x": float(candidate["x"]),
                    "y": float(candidate["y"]),
                    "confidence": float(
                        candidate.get("confidence", 0)
                    )
                })

        if not points:
            return {}

        # =========================================================
        # STEP 2
        # Build X clusters
        #
        # Reel icons should share approximately the same X.
        # =========================================================

        points_sorted = sorted(
            points,
            key=lambda p: p["x"]
        )

        x_clusters = []

        for point in points_sorted:

            best_cluster = None
            best_distance = float("inf")

            for cluster in x_clusters:

                distance = abs(
                    point["x"]
                    -
                    cluster["center_x"]
                )

                if (
                    distance <= 45
                    and
                    distance < best_distance
                ):
                    best_cluster = cluster
                    best_distance = distance

            if best_cluster is None:

                x_clusters.append({
                    "center_x": point["x"],
                    "points": [point]
                })

            else:

                best_cluster["points"].append(
                    point
                )

                best_cluster["center_x"] = (
                    sum(
                        p["x"]
                        for p in best_cluster["points"]
                    )
                    /
                    len(
                        best_cluster["points"]
                    )
                )

        # =========================================================
        # STEP 3
        # Score X clusters
        #
        # Prefer:
        #   - many different icon types
        #   - many candidates
        #   - good confidence
        # =========================================================

        best_cluster = None
        best_score = float("-inf")

        for cluster in x_clusters:

            cluster_points = cluster["points"]

            if not cluster_points:
                continue

            unique_keys = set(
                p["key"]
                for p in cluster_points
            )

            average_confidence = (
                sum(
                    p["confidence"]
                    for p in cluster_points
                )
                /
                len(cluster_points)
            )

            score = (
                len(unique_keys) * 1000
                +
                len(cluster_points) * 10
                +
                average_confidence
            )

            print(
                "INSTAGRAM REEL X CLUSTER:",
                round(
                    cluster["center_x"],
                    2
                ),
                "types=",
                unique_keys,
                "points=",
                len(cluster_points),
                "score=",
                round(score, 2)
            )

            if score > best_score:

                best_score = score
                best_cluster = cluster

        if best_cluster is None:
            return {}

        # =========================================================
        # STEP 4
        #
        # IMPORTANT:
        #
        # We now remove vertically isolated candidates.
        #
        # A real Reel engagement rail should contain several
        # icons reasonably close together vertically.
        # =========================================================

        rail_points = list(
            best_cluster["points"]
        )

        rail_points.sort(
            key=lambda p: p["y"]
        )

        print(
            "INSTAGRAM REEL X-CLUSTER POINTS:",
            rail_points
        )

        # =========================================================
        # Find the densest vertical region.
        #
        # A normal Reel rail contains multiple engagement icons.
        #
        # We use a sliding window instead of assuming fixed
        # screen coordinates.
        # =========================================================

        WINDOW_HEIGHT = 700

        best_window = None
        best_window_score = float("-inf")

        for start_point in rail_points:

            start_y = start_point["y"]

            window_points = [
                p
                for p in rail_points
                if (
                    start_y
                    <= p["y"]
                    <=
                    start_y + WINDOW_HEIGHT
                )
            ]

            if not window_points:
                continue

            unique_keys = set(
                p["key"]
                for p in window_points
            )

            average_confidence = (
                sum(
                    p["confidence"]
                    for p in window_points
                )
                /
                len(window_points)
            )

            # Different icon types matter more than raw duplicates.
            score = (
                len(unique_keys) * 1000
                +
                len(window_points) * 10
                +
                average_confidence
            )

            if score > best_window_score:

                best_window_score = score

                best_window = {
                    "points": window_points,
                    "start_y": start_y,
                    "end_y": start_y + WINDOW_HEIGHT
                }

        if best_window is None:
            return {}

        rail_points = best_window["points"]

        rail_points.sort(
            key=lambda p: p["y"]
        )

        # =========================================================
        # STEP 5
        #
        # Calculate rail X using the candidates in the selected
        # vertical region.
        # =========================================================

        rail_x = (
            sum(
                p["x"]
                for p in rail_points
            )
            /
            len(rail_points)
        )

        print(
            "INSTAGRAM REEL SELECTED VERTICAL RAIL:",
            rail_points
        )

        print(
            "INSTAGRAM REEL RAIL CENTER X:",
            round(
                rail_x,
                2
            )
        )

        # =========================================================
        # STEP 6
        #
        # Remove candidates that are too far from rail center.
        # =========================================================

        MAX_X_DISTANCE = 35

        aligned_points = [
            p
            for p in rail_points
            if abs(
                p["x"]
                -
                rail_x
            ) <= MAX_X_DISTANCE
        ]

        # =========================================================
        # STEP 7
        #
        # For duplicate icon types:
        #
        #   PRIMARY:
        #       closest to rail X
        #
        #   SECONDARY:
        #       confidence
        #
        # NOT simply highest confidence.
        # =========================================================

        icons = {}

        for point in aligned_points:

            key = point["key"]

            x_distance = abs(
                point["x"]
                -
                rail_x
            )

            if key not in icons:

                icons[key] = {
                    "point": point,
                    "x_distance": x_distance
                }

                continue

            current = icons[key]

            current_point = current["point"]

            current_x_distance = (
                current["x_distance"]
            )

            if x_distance < current_x_distance:

                icons[key] = {
                    "point": point,
                    "x_distance": x_distance
                }

            elif (
                x_distance
                ==
                current_x_distance
                and
                point["confidence"]
                >
                current_point["confidence"]
            ):

                icons[key] = {
                    "point": point,
                    "x_distance": x_distance
                }

        # =========================================================
        # STEP 8
        # Convert to final structure
        # =========================================================

        final_icons = {}

        for key, data in icons.items():

            point = data["point"]

            final_icons[key] = {
                "x": int(
                    round(
                        point["x"]
                    )
                ),
                "y": int(
                    round(
                        point["y"]
                    )
                )
            }

        # =========================================================
        # DEBUG
        # =========================================================

        debug_icons = sorted(
            final_icons.items(),
            key=lambda item:
                item[1]["y"]
        )

        print(
            "INSTAGRAM REEL FINAL ICONS:",
            dict(debug_icons)
        )

        return final_icons
    
    def clean_number(self, text):
    
        text = text.strip().lower()
        text = text.replace(",", "")

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*([km]?)",
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
        Robust Instagram Feed / Horizontal OCR.

        IMPORTANT:
        This function is ONLY for horizontal Instagram feed posts.

        Strategy:
        - Use each detected icon as an anchor.
        - OCR ONLY the number region immediately to the
        right of that icon.
        - Never perform global OCR assignment.
        - Never allow numbers from another engagement slot
        to merge together.

        Example:

            ❤️ 301   💬 7   🔁 1   ✈ 17

        becomes:

            likes    -> 301
            comments -> 7
            reposts  -> 1
            shares   -> 17
        """

        numbers = {
            "likes": 0,
            "comments": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0,
        }

        if not icons:
            return numbers

        height, width = image.shape[:2]

        # ---------------------------------------------------------
        # Instagram feed engagement order
        # ---------------------------------------------------------

        keys = [
            "likes",
            "comments",
            "reposts",
            "shares",
        ]

        available = [
            key
            for key in keys
            if key in icons
        ]

        if not available:
            return numbers

        print(
            "INSTAGRAM FEED OCR ICON ORDER:",
            available
        )

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # The detected icon x-coordinate is the LEFT SIDE
        # of the icon bounding box.
        #
        # The number is NOT immediately at icon_x.
        #
        # Example from your screenshot:
        #
        # icon x = 13
        # heart ends around x = 69
        # "301" begins around x = 80
        #
        # Therefore we deliberately start OCR at:
        #
        #     icon_x + 55
        #
        # This removes the icon from the OCR region.
        # ---------------------------------------------------------

        for index, key in enumerate(available):

            icon_x = int(
                round(
                    icons[key]["x"]
                )
            )

            icon_y = int(
                round(
                    icons[key]["y"]
                )
            )

            # -----------------------------------------------------
            # X START
            #
            # Move past the icon itself.
            # -----------------------------------------------------

            x1 = icon_x + 55

            # -----------------------------------------------------
            # X END
            #
            # Stop BEFORE the next engagement icon.
            #
            # This prevents:
            #
            #     301 + 7 + 1 + 17
            #
            # from becoming:
            #
            #     3017117
            # -----------------------------------------------------

            if index + 1 < len(available):

                next_key = available[index + 1]

                next_x = int(
                    round(
                        icons[next_key]["x"]
                    )
                )

                x2 = next_x - 12

            else:

                # -------------------------------------------------
                # Shares is the last counted engagement.
                #
                # Stop before bookmark icon.
                # -------------------------------------------------

                if "bookmarks" in icons:

                    bookmark_x = int(
                        round(
                            icons["bookmarks"]["x"]
                        )
                    )

                    x2 = bookmark_x - 20

                else:

                    x2 = width - 5

            # -----------------------------------------------------
            # Y REGION
            #
            # The icon itself is around y.
            #
            # The engagement number is slightly BELOW the icon
            # center in these Instagram screenshots.
            #
            # We therefore use a narrow vertical strip.
            #
            # This is VERY important because your previous
            # extractor was also picking numbers from the post
            # image / banner above the engagement row.
            # -----------------------------------------------------

            y1 = icon_y + 12
            y2 = icon_y + 62

            # -----------------------------------------------------
            # Clamp coordinates
            # -----------------------------------------------------

            x1 = max(
                0,
                min(
                    x1,
                    width
                )
            )

            x2 = max(
                0,
                min(
                    x2,
                    width
                )
            )

            y1 = max(
                0,
                min(
                    y1,
                    height
                )
            )

            y2 = max(
                0,
                min(
                    y2,
                    height
                )
            )

            if x2 <= x1 or y2 <= y1:

                print(
                    "INSTAGRAM FEED OCR:",
                    key,
                    "INVALID ROI",
                    (
                        x1,
                        y1,
                        x2,
                        y2
                    )
                )

                continue

            # -----------------------------------------------------
            # Extract ONLY this engagement number region.
            # -----------------------------------------------------

            crop = image[
                y1:y2,
                x1:x2
            ]

            if crop.size == 0:

                print(
                    "INSTAGRAM FEED OCR:",
                    key,
                    "EMPTY ROI"
                )

                continue

            # -----------------------------------------------------
            # Grayscale
            # -----------------------------------------------------

            gray = cv2.cvtColor(
                crop,
                cv2.COLOR_BGR2GRAY
            )

            # -----------------------------------------------------
            # Upscale
            #
            # Your screenshots have small white numbers.
            # Upscaling makes Tesseract much more reliable.
            # -----------------------------------------------------

            gray = cv2.resize(
                gray,
                None,
                fx=7,
                fy=7,
                interpolation=cv2.INTER_CUBIC
            )

            candidates = []

            # -----------------------------------------------------
            # OCR variants
            #
            # We intentionally keep OCR INSIDE THIS SLOT ONLY.
            # -----------------------------------------------------

            variants = [
                gray
            ]

            for threshold_value in [
                150,
                180,
                200,
                220
            ]:

                thresholded = cv2.threshold(
                    gray,
                    threshold_value,
                    255,
                    cv2.THRESH_BINARY
                )[1]

                variants.append(
                    thresholded
                )

            # -----------------------------------------------------
            # OCR
            # -----------------------------------------------------

            for variant_index, variant in enumerate(
                variants
            ):

                for psm in [
                    7,
                    8,
                    10,
                    13
                ]:

                    raw_text = pytesseract.image_to_string(
                        variant,
                        config=(
                            f"--psm {psm} "
                            "-c tessedit_char_whitelist="
                            "0123456789KkMm"
                        )
                    ).strip()

                    value = self.clean_number(
                        raw_text
                    )

                    if value > 0:

                        candidates.append(
                            value
                        )

            # -----------------------------------------------------
            # Select strongest OCR consensus.
            # -----------------------------------------------------

            if candidates:

                from collections import Counter

                counts = Counter(
                    candidates
                )

                value, votes = (
                    counts.most_common(1)[0]
                )

                numbers[key] = value

                print(
                    "INSTAGRAM FEED OCR:",
                    key,
                    "value=",
                    value,
                    "votes=",
                    votes,
                    "candidates=",
                    dict(counts)
                )

            else:

                print(
                    "INSTAGRAM FEED OCR:",
                    key,
                    "OCR FAILED"
                )

        # ---------------------------------------------------------
        # Instagram feed bookmark has no numeric count here.
        # ---------------------------------------------------------

        numbers["bookmarks"] = 0

        print(
            "INSTAGRAM FEED NUMBERS:",
            numbers
        )

        return numbers
    
    def _instagram_reel_icon_centers(self, image, all_candidates=None):
        """
        Detect the OUTER Instagram Reel action rail using geometry.

        We do not trust the strongest template match.  Instead we look
        for the repeated, large white UI icons at the right edge and use
        their vertical spacing.  This is what separates the outer Reel
        controls from numbers/icons that happen to exist inside the Reel.
        """

        if image is None:
            return []

        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        x0 = int(w * 0.84)
        x1 = int(w * 0.995)
        y0 = int(h * 0.25)
        y1 = int(h * 0.94)

        threshold_solutions = []

        # Prefer bright-white UI at 220, but try darker thresholds as
        # fallbacks for compressed screenshots.
        for threshold in [220, 200, 180, 160]:
            rail_gray = gray[y0:y1, x0:x1]

            binary = cv2.threshold(
                rail_gray,
                threshold,
                255,
                cv2.THRESH_BINARY
            )[1]

            count, labels, stats, centroids = (
                cv2.connectedComponentsWithStats(
                    binary,
                    8
                )
            )

            raw = []

            for i in range(1, count):
                bx, by, bw, bh, area = stats[i]

                # Instagram action icons are large, compact components.
                # Number glyphs are deliberately excluded here.
                if not (
                    30 <= bw <= 75
                    and 30 <= bh <= 65
                    and 200 <= area <= 1000
                ):
                    continue

                raw.append({
                    "x": float(
                        bx + x0 + bw / 2.0
                    ),
                    "y": float(
                        by + y0 + bh / 2.0
                    ),
                    "area": float(area)
                })

            if not raw:
                continue

            # Merge split parts of one icon (most commonly the repost
            # icon) when they are close vertically.
            raw.sort(key=lambda p: p["y"])
            clusters = []

            for point in raw:
                merged = None

                for cluster in clusters:
                    if (
                        abs(point["y"] - cluster["y"]) <= 45
                        and
                        abs(point["x"] - cluster["x"]) <= 45
                    ):
                        merged = cluster
                        break

                if merged is None:
                    clusters.append({
                        "x": point["x"],
                        "y": point["y"],
                        "area": point["area"],
                        "points": [point]
                    })
                else:
                    merged["points"].append(point)
                    # Weighted/strongest representative.  Bounding-box
                    # centre is more stable than a pixel centroid when
                    # the icon is hollow.
                    strongest = max(
                        merged["points"],
                        key=lambda p: p["area"]
                    )
                    merged["x"] = strongest["x"]
                    merged["y"] = strongest["y"]
                    merged["area"] = strongest["area"]

            clusters.sort(key=lambda c: c["y"])

            # Remove any remaining duplicate clusters.
            cleaned = []
            for cluster in clusters:
                if (
                    cleaned
                    and
                    abs(
                        cluster["y"]
                        -
                        cleaned[-1]["y"]
                    ) < 55
                ):
                    if cluster["area"] > cleaned[-1]["area"]:
                        cleaned[-1] = cluster
                else:
                    cleaned.append(cluster)

            # Score how much the sequence looks like a real Reel rail.
            # A full five-icon sequence gets a strong bonus; regular
            # vertical spacing gets another strong bonus.
            if len(cleaned) >= 2:
                gaps = [
                    cleaned[i + 1]["y"] - cleaned[i]["y"]
                    for i in range(len(cleaned) - 1)
                ]

                valid_gaps = [
                    gap
                    for gap in gaps
                    if 55 <= gap <= 180
                ]

                if valid_gaps:
                    mean_gap = sum(valid_gaps) / len(valid_gaps)
                    gap_error = sum(
                        abs(gap - mean_gap)
                        for gap in valid_gaps
                    )
                else:
                    gap_error = 9999

                score = (
                    min(len(cleaned), 5) * 10000
                    + len(valid_gaps) * 1000
                    + sum(c["area"] for c in cleaned)
                    - gap_error * 5
                )
            else:
                score = -9999

            threshold_solutions.append(
                (
                    score,
                    cleaned,
                    threshold
                )
            )

        if not threshold_solutions:
            return []

        # Choose the threshold whose vertical structure is strongest.
        _, clusters, chosen_threshold = max(
            threshold_solutions,
            key=lambda item: item[0]
        )

        # If more than five remain, choose the most coherent five-icon
        # subsequence.  In normal screenshots this simply removes a
        # decorative/menu icon below the Reel rail.
        if len(clusters) > 5:
            from itertools import combinations

            best_subset = None
            best_score = float("-inf")

            for subset in combinations(clusters, 5):
                ys = [c["y"] for c in subset]
                gaps = [
                    ys[i + 1] - ys[i]
                    for i in range(4)
                ]

                if any(
                    gap < 55 or gap > 180
                    for gap in gaps
                ):
                    continue

                mean_gap = sum(gaps) / 4.0
                gap_error = sum(
                    abs(gap - mean_gap)
                    for gap in gaps
                )

                score = (
                    50000
                    - gap_error * 10
                    + sum(c["area"] for c in subset)
                )

                if score > best_score:
                    best_score = score
                    best_subset = subset

            if best_subset is not None:
                clusters = list(best_subset)
            else:
                clusters = clusters[:5]

        centers = [
            {
                "x": int(round(cluster["x"])),
                "y": int(round(cluster["y"]))
            }
            for cluster in clusters
        ]

        # Template fallback for a missing icon.  Only add a candidate
        # when it fills a genuine gap in the vertical sequence; template
        # confidence alone never decides the rail.
        if len(centers) < 5 and isinstance(all_candidates, dict):
            template_points = []

            for values in all_candidates.values():
                if not isinstance(values, list):
                    continue

                for item in values:
                    if not isinstance(item, dict):
                        continue

                    try:
                        cx = float(item["x"])
                        cy = float(item["y"])
                        conf = float(
                            item.get("confidence", 0)
                        )
                    except Exception:
                        continue

                    if (
                        cx >= w * 0.86
                        and
                        h * 0.25 <= cy <= h * 0.94
                        and
                        conf >= 0.65
                    ):
                        template_points.append({
                            "x": cx,
                            "y": cy,
                            "confidence": conf
                        })

            template_points.sort(
                key=lambda p: p["confidence"],
                reverse=True
            )

            for point in template_points:
                if any(
                    abs(point["y"] - center["y"]) < 50
                    for center in centers
                ):
                    continue

                centers.append({
                    "x": int(round(point["x"])),
                    "y": int(round(point["y"]))
                })

                centers.sort(key=lambda p: p["y"])

                if len(centers) >= 5:
                    break

        if len(centers) < 2:
            return []

        centers = sorted(
            centers,
            key=lambda p: p["y"]
        )[:5]

        print(
            "INSTAGRAM ROBUST REEL ICON CENTERS:",
            centers,
            "threshold=",
            chosen_threshold
        )

        return centers

    def _instagram_reel_ocr_value(self, image, icon_y):
        """
        Read the number immediately below one Reel icon.

        OCR is performed on several preprocessing variants and the
        result is chosen by consensus.  This is deliberately local:
        numbers inside an embedded post are not allowed to participate.
        """

        if image is None:
            return 0

        h, w = image.shape[:2]

        # Instagram's UI icon-to-number distance is visually stable even
        # when screenshots have very different total heights.  Use a
        # generous local search band instead of a fixed absolute Y slot.
        search_y1 = int(icon_y + 42)
        search_y2 = int(icon_y + 112)

        if search_y1 >= h:
            return 0

        search_y2 = min(h, search_y2)

        x1 = int(w * 0.84)
        x2 = int(w * 0.995)

        gray = cv2.cvtColor(
            image[search_y1:search_y2, x1:x2],
            cv2.COLOR_BGR2GRAY
        )

        if gray.size == 0:
            return 0

        # ------------------------------------------------------------
        # Find text rows in several binary representations.
        # ------------------------------------------------------------
        row_candidates = []

        variants = [
            gray,
            cv2.threshold(
                gray, 160, 255, cv2.THRESH_BINARY
            )[1],
            cv2.threshold(
                gray, 180, 255, cv2.THRESH_BINARY
            )[1],
            cv2.threshold(
                gray, 200, 255, cv2.THRESH_BINARY
            )[1],
            cv2.threshold(
                gray, 220, 255, cv2.THRESH_BINARY
            )[1],
        ]

        # HSV white-mask variant.  This is particularly useful when the
        # number is drawn over yellow/coloured content.
        hsv = cv2.cvtColor(
            image[search_y1:search_y2, x1:x2],
            cv2.COLOR_BGR2HSV
        )

        for saturation_limit in [40, 60, 80]:
            variants.append(
                cv2.inRange(
                    hsv,
                    np.array([0, 0, 130]),
                    np.array([180, saturation_limit, 255])
                )
            )

        for variant in variants:
            if variant.ndim != 2:
                continue

            # For raw grayscale, thresholding here makes component
            # detection consistent with the binary variants.
            if np.max(variant) > 0 and np.min(variant) != 0:
                binary = cv2.threshold(
                    variant,
                    190,
                    255,
                    cv2.THRESH_BINARY
                )[1]
            else:
                binary = variant

            count, labels, stats, centroids = (
                cv2.connectedComponentsWithStats(
                    binary,
                    8
                )
            )

            components = []

            for i in range(1, count):
                bx, by, bw, bh, area = stats[i]

                # Number glyphs are normally about 10-25 px high.
                if not (
                    8 <= bh <= 28
                    and 2 <= bw <= 40
                    and 10 <= area <= 900
                ):
                    continue

                components.append(
                    (
                        int(bx),
                        int(by),
                        int(bw),
                        int(bh),
                        int(area)
                    )
                )

            components.sort(key=lambda c: c[1])

            # Group glyphs belonging to one number by their vertical
            # alignment.
            groups = []

            for component in components:
                _, by, _, bh, _ = component

                if not groups:
                    groups.append([
                        by,
                        by + bh,
                        [component]
                    ])
                    continue

                if by <= groups[-1][1] + 5:
                    groups[-1][0] = min(
                        groups[-1][0],
                        by
                    )
                    groups[-1][1] = max(
                        groups[-1][1],
                        by + bh
                    )
                    groups[-1][2].append(component)
                else:
                    groups.append([
                        by,
                        by + bh,
                        [component]
                    ])

            for group in groups:
                gy1, gy2, group_components = group

                # A numeric label is compact.  Large vertical groups are
                # usually a number merged with an adjacent icon/background.
                if (gy2 - gy1) > 30:
                    continue

                group_center = (
                    (gy1 + gy2) / 2.0
                    + search_y1
                )

                # The expected number is below the icon.
                if not (
                    icon_y + 45
                    <= group_center
                    <= icon_y + 100
                ):
                    continue

                gx1 = min(
                    c[0]
                    for c in group_components
                )
                gx2 = max(
                    c[0] + c[2]
                    for c in group_components
                )

                # Expand slightly so punctuation such as commas is kept.
                crop_y1 = max(0, gy1 - 2)
                crop_y2 = min(
                    variant.shape[0],
                    gy2 + 2
                )
                crop_x1 = max(0, gx1 - 2)
                crop_x2 = min(
                    variant.shape[1],
                    gx2 + 2
                )

                row_candidates.append({
                    "center_y": group_center,
                    "center_x": (
                        (gx1 + gx2) / 2.0
                        + x1
                    ),
                    "row_top": int(gy1 + search_y1),
                    "row_bottom": int(gy2 + search_y1),
                    "crop_gray": gray[
                        crop_y1:crop_y2,
                        crop_x1:crop_x2
                    ],
                    "crop_binary": binary[
                        crop_y1:crop_y2,
                        crop_x1:crop_x2
                    ],
                    "component_count": len(group_components),
                    "text_width": int(gx2 - gx1)
                })

        if not row_candidates:
            return 0

        # Remove duplicate row proposals produced by different masks.
        row_candidates.sort(
            key=lambda item: abs(
                item["center_y"]
                -
                (icon_y + 60)
            )
        )

        merged_rows = []

        for candidate in row_candidates:
            merged = False

            for existing in merged_rows:
                if abs(
                    candidate["center_y"]
                    -
                    existing["center_y"]
                ) <= 10:
                    # Keep the row with more glyphs.
                    # Keep the most useful estimate of the number of
                    # glyphs.  Thresholds can merge several digits into
                    # one blob or split punctuation/background into extra
                    # blobs.  A count between 2 and 6 is the useful range.
                    old_count = int(
                        existing.get("component_count", 0)
                    )
                    new_count = int(
                        candidate.get("component_count", 0)
                    )

                    if 2 <= new_count <= 6:
                        if not (2 <= old_count <= 6):
                            existing["component_count"] = new_count
                        else:
                            existing["component_count"] = min(
                                old_count,
                                new_count
                            )

                    # Keep the candidate with the best horizontal alignment
                    # to the Reel rail.  Its crop is usually the cleanest
                    # threshold-specific representation of the number.
                    old_dx = abs(
                        existing.get("center_x", w * 0.915)
                        -
                        (w * 0.915)
                    )
                    new_dx = abs(
                        candidate.get("center_x", w * 0.915)
                        -
                        (w * 0.915)
                    )

                    if new_dx < old_dx:
                        for field in [
                            "center_x",
                            "crop_gray",
                            "crop_binary",
                            "component_count",
                            "text_width",
                            "row_top",
                            "row_bottom"
                        ]:
                            if field in candidate:
                                existing[field] = candidate[field]

                    merged = True
                    break

            if not merged:
                merged_rows.append(candidate)

        if not merged_rows:
            return 0

        # The number closest to icon+74 is normally the correct one.
        rail_center_x = w * 0.915

        best_row = min(
            merged_rows,
            key=lambda item: (
                abs(
                    item["center_y"]
                    -
                    (icon_y + 60)
                )
                +
                abs(
                    item.get("center_x", rail_center_x)
                    -
                    rail_center_x
                ) * 0.35,
                -item["component_count"]
            )
        )

        votes = []

        # OCR a broad but vertically localized row.  The Y position comes
        # from the detected Reel rail, while the X region stays on the
        # right-side UI.  This keeps the entire number visible without
        # admitting numbers from the embedded post.
        row_center = float(
            best_row["center_y"]
        )


        row_top = max(
            0,
            int(best_row.get("row_top", row_center - 4)) - 4
        )

        row_bottom = min(
            h,
            int(best_row.get("row_bottom", row_center + 4)) + 4
        )

        rail_row = image[
            row_top:row_bottom,
            x1:x2
        ]

        gray_row = cv2.cvtColor(
            rail_row,
            cv2.COLOR_BGR2GRAY
        )

        # Estimate expected digit count from the localized component
        # width.  It is only a sanity filter; OCR consensus remains the
        # main signal.
        text_width = int(
            best_row.get(
                "text_width",
                40
            )
        )

        estimated_digits = max(
            1,
            int(
                round(
                    text_width / 13.0
                )
            )
        )

        component_count = int(
            best_row.get(
                "component_count",
                0
            )
        )

        # Width is a stable signal for the Instagram count font.  Use
        # component count only to preserve genuine one-digit labels.
        if component_count == 1 and text_width <= 18:
            plausible_digits = {1, 2}
        elif text_width <= 28:
            plausible_digits = {2}
        elif text_width <= 45:
            plausible_digits = {3, 2}
        elif text_width <= 70:
            plausible_digits = {4, 3, 5}
        else:
            plausible_digits = {5, 4, 6}

        preprocessing = [
            (
                "gray",
                gray_row,
                1
            ),
            (
                "threshold160",
                cv2.threshold(
                    gray_row,
                    160,
                    255,
                    cv2.THRESH_BINARY
                )[1],
                2
            ),
            (
                "threshold180",
                cv2.threshold(
                    gray_row,
                    180,
                    255,
                    cv2.THRESH_BINARY
                )[1],
                2
            ),
            (
                "threshold200",
                cv2.threshold(
                    gray_row,
                    200,
                    255,
                    cv2.THRESH_BINARY
                )[1],
                2
            ),
            (
                "threshold220",
                cv2.threshold(
                    gray_row,
                    220,
                    255,
                    cv2.THRESH_BINARY
                )[1],
                8
            ),
        ]

        votes = []

        for _, source, preprocessing_weight in preprocessing:
            if source.size == 0:
                continue

            up = cv2.resize(
                source,
                None,
                fx=10,
                fy=10,
                interpolation=cv2.INTER_CUBIC
            )

            for psm in [
                6,
                7,
                8
            ]:
                try:
                    text = pytesseract.image_to_string(
                        up,
                        config=(
                            f"--psm {psm} "
                            "-c tessedit_char_whitelist="
                            "0123456789KkMm.,"
                        )
                    ).strip()
                except Exception:
                    continue

                value = self.clean_number(text)

                if value <= 0:
                    continue

                digit_count = len(
                    re.sub(
                        r"[^0-9]",
                        "",
                        text
                    )
                )

                if digit_count not in plausible_digits:
                    continue

                psm_weights = {
                    6: 1,
                    7: 2,
                    8: 5
                }

                psm_weight = psm_weights.get(
                    psm,
                    1
                )

                for _ in range(
                    preprocessing_weight * psm_weight
                ):
                    votes.append(value)

        if not votes:
            return 0

        from collections import Counter

        counts = Counter(votes)
        best_value, best_count = counts.most_common(1)[0]

        # Safety rule: if several values exist, prefer the value whose
        # digit length is closest to the localized text width.  This stops
        # hallucinations such as 274625 from replacing 7462.
        text_width = int(
            best_row.get(
                "text_width",
                best_row["crop_gray"].shape[1]
            )
        )

        estimated_digits = max(
            1,
            int(
                round(
                    text_width / 13.0
                )
            )
        )

        plausible = [
            (value, count)
            for value, count in counts.items()
            if abs(
                len(str(value))
                -
                estimated_digits
            ) <= 1
        ]

        if plausible:
            best_value, best_count = max(
                plausible,
                key=lambda item: (
                    item[1],
                    -abs(
                        len(str(item[0]))
                        -
                        estimated_digits
                    )
                )
            )

        print(
            "INSTAGRAM REEL ROBUST OCR:",
            "icon_y=",
            icon_y,
            "value=",
            best_value,
            "votes=",
            dict(counts)
        )

        return int(best_value)

    def extract_instagram_reel_numbers(
        self,
        image,
        icons=None,
        all_candidates=None
    ):
        """
        Universal Instagram Reel engagement extraction.

        The old implementation tried to decide the answer from the
        strongest template match.  That is unsafe when a Reel contains
        an embedded post/Reel with its own Instagram-looking UI.

        This implementation instead:

            1. Finds the OUTER right-side action rail geometrically.
            2. Uses vertical order to assign the actions.
            3. OCRs each number locally below its own icon.
            4. Uses OCR voting across multiple preprocessing paths.

        Therefore a number such as 206 remains a Reel share count when
        it is outside/below the outer share icon, while numbers inside
        an embedded post are not considered.
        """

        output = {
            "likes": 0,
            "comments": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0,
        }

        if image is None:
            return output

        # Prefer the freshly detected geometric rail.  If the caller has
        # already supplied template candidates, use them only as fallback
        # geometry; never use their type for number assignment.
        rail = self._instagram_reel_icon_centers(
            image,
            all_candidates=all_candidates
        )

        if len(rail) < 2:
            print(
                "INSTAGRAM REEL ROBUST OCR: rail not confidently detected"
            )
            return output

        # Instagram Reel action order is stable from top to bottom.
        keys = [
            "likes",
            "comments",
            "reposts",
            "shares",
            "bookmarks"
        ]

        # If there are more than five candidates, keep the strongest five
        # already selected by _instagram_reel_icon_centers().
        rail = sorted(
            rail,
            key=lambda item: item["y"]
        )[:5]

        print(
            "INSTAGRAM REEL ROBUST RAIL:",
            rail
        )

        for key, icon in zip(keys, rail):
            value = self._instagram_reel_ocr_value(
                image,
                icon["y"]
            )

            if value > 0:
                output[key] = value

        print(
            "INSTAGRAM REEL ROBUST RESULT:",
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
        Instagram engagement dispatcher.

        IMPORTANT:
        Horizontal and vertical Instagram layouts are completely
        separated.

        Horizontal:
            ONLY extract_instagram_feed_numbers()

        Vertical:
            ONLY extract_instagram_reel_numbers()

        Never run Reel logic for a horizontal screenshot.
        Never run Feed logic for a vertical screenshot.
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

        # ---------------------------------------------------------
        # Detect layout from the already-selected icon positions
        # ---------------------------------------------------------

        layout = self.detect_instagram_layout(icons)

        print(
            "INSTAGRAM FINAL LAYOUT:",
            layout
        )

        # =========================================================
        # HORIZONTAL / FEED
        # =========================================================

        if layout == "horizontal":

            print(
                "INSTAGRAM FEED: USING HORIZONTAL OCR ONLY"
            )

            feed_numbers = self.extract_instagram_feed_numbers(
                image,
                icons
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

            # Instagram feed does not expose a bookmark count.
            output["bookmarks"] = 0

            print(
                "FINAL INSTAGRAM FEED ENGAGEMENT:",
                output
            )

            return output

        # =========================================================
        # VERTICAL / REELS
        # =========================================================

        if layout == "vertical":

            print(
                "INSTAGRAM REEL: USING VERTICAL OCR ONLY"
            )

            reel_numbers = self.extract_instagram_reel_numbers(
                image,
                icons
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

        # =========================================================
        # UNKNOWN
        # =========================================================

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

        # Instagram must NOT search the whole screenshot for icons.
        # The post image itself often contains shapes that look like
        # the engagement templates. That was the main reason the
        # feed screenshot was returning values such as 7/7/7.
        
        icon_threshold = 0.60
        if normalized_platform == "instagram":

            height, width = image.shape[:2]

            feed_icons = {}
            reel_icons = {}

            # Feed: engagement row is near the bottom and horizontal.
            feed_region = (
                0,
                int(height * 0.82),
                width,
                height
            )

            # Reels: engagement column is on the right side and
            # occupies the middle/lower part of the screen.
            reel_region = (
                int(width * 0.78),
                int(height * 0.25),
                width,
                int(height * 0.90)
            )

            for key, template in self.templates.items():
    
                feed_location = self.find_icon_region(
                    image,
                    template,
                    feed_region,
                    threshold=icon_threshold
                )

                if feed_location is not None:

                    feed_icons[key] = {
                        "x": feed_location[0],
                        "y": feed_location[1]
                    }


            # ---------------------------------------------------------
            # Reel detection
            # ---------------------------------------------------------
            #
            # IMPORTANT:
            # Do NOT use find_icon_region() here.
            #
            # Reel needs multiple candidate matches so that we can
            # identify the coherent vertical engagement rail.
            # ---------------------------------------------------------

            reel_icons = self.detect_instagram_reel_icons(
                image,
                reel_region,
                threshold=0.45
            )

            print(
                "INSTAGRAM FEED ICONS:",
                feed_icons
            )

            print(
                "INSTAGRAM REEL ICONS:",
                reel_icons
            )

            # Choose the layout whose expected UI region contains
            # more engagement icons.
            if (
                len(feed_icons) >= 2
                and len(feed_icons) >= len(reel_icons)
            ):
                icons = feed_icons
                print("INSTAGRAM LAYOUT PRESELECTED: horizontal")

            elif len(reel_icons) >= 2:
                icons = reel_icons
                print("INSTAGRAM LAYOUT PRESELECTED: vertical")

            elif feed_icons:
                icons = feed_icons
                print("INSTAGRAM LAYOUT PRESELECTED: horizontal (partial)")

            elif reel_icons:
                icons = reel_icons
                print("INSTAGRAM LAYOUT PRESELECTED: vertical (partial)")

        else:

            # Existing Facebook/Twitter behaviour remains unchanged.
            for key, template in self.templates.items():
    
                if normalized_platform == "instagram":

                    location = self.find_instagram_icon(
                        image,
                        template,
                        threshold=0.60
                    )

                else:

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
            "ENGAGEMENT ICON POSITIONS:",
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

        # -------------------------------------------------
        # RETURN ONLY ACTUALLY DETECTED ENGAGEMENT VALUES
        # -------------------------------------------------

        final_output = {
            key: value
            for key, value in output.items()
            if value > 0
        }

        print(
            "FINAL ENGAGEMENT:",
            final_output
        )

        return final_output


engagement_extractor = EngagementExtractor()