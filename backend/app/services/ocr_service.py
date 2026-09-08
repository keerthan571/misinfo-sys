from __future__ import annotations

import io
import logging
import os
import re

import pytesseract
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    UnidentifiedImageError,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# WINDOWS TESSERACT PATH
# ---------------------------------------------------------

if os.name == "nt":

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


class OCRService:

    # -----------------------------------------------------
    # LIMITS
    # -----------------------------------------------------

    MAX_FILE_SIZE = 10 * 1024 * 1024

    MAX_INPUT_PIXELS = 20_000_000

    MAX_DIMENSION = 5000

    MAX_PROCESSED_DIMENSION = 3000

    # -----------------------------------------------------
    # SUPPORTED IMAGE FORMATS
    # -----------------------------------------------------

    ALLOWED_FORMATS = {
        "JPEG",
        "PNG",
        "WEBP",
        "BMP",
        "TIFF",
    }

    # -----------------------------------------------------
    # SUPPORTED OCR LANGUAGES
    #
    # Tesseract language codes:
    #
    # eng = English
    # hin = Hindi
    # kan = Kannada
    #
    # Combinations are also supported.
    # -----------------------------------------------------

    SUPPORTED_LANGUAGES = {
        "eng",
        "hin",
        "kan",
        "eng+hin",
        "eng+kan",
        "hin+kan",
        "eng+hin+kan",
    }

    DEFAULT_LANGUAGE = "eng"

    # -----------------------------------------------------
    # LANGUAGE NORMALIZATION
    # -----------------------------------------------------

    def normalize_language(self, language):

        if not language:

            return self.DEFAULT_LANGUAGE

        language = str(
            language
        ).strip().lower()

        # Accept common frontend names.

        aliases = {

            "english": "eng",

            "hindi": "hin",

            "kannada": "kan",

            "english+hindi": "eng+hin",

            "hindi+english": "eng+hin",

            "english+kannada": "eng+kan",

            "kannada+english": "eng+kan",

            "hindi+kannada": "hin+kan",

            "kannada+hindi": "hin+kan",

            "english+hindi+kannada":
                "eng+hin+kan",

            "english+kannada+hindi":
                "eng+hin+kan",

            "hindi+english+kannada":
                "eng+hin+kan",

            "hindi+kannada+english":
                "eng+hin+kan",

            "kannada+english+hindi":
                "eng+hin+kan",

            "kannada+hindi+english":
                "eng+hin+kan",

        }

        language = aliases.get(
            language,
            language
        )

        if language in self.SUPPORTED_LANGUAGES:

            return language

        logger.warning(
            "Unsupported OCR language '%s'. "
            "Falling back to English.",
            language
        )

        return self.DEFAULT_LANGUAGE

    # -----------------------------------------------------
    # CHECK AVAILABLE TESSERACT LANGUAGES
    # -----------------------------------------------------

    def get_available_languages(self):

        try:

            languages = (
                pytesseract.get_languages(
                    config=""
                )
            )

            return set(
                languages
            )

        except Exception:

            logger.exception(
                "Could not determine available Tesseract languages."
            )

            return {
                "eng"
            }

    # -----------------------------------------------------
    # VALIDATE REQUESTED LANGUAGES
    # -----------------------------------------------------

    def validate_language_models(
        self,
        language
    ):

        requested = set(
            language.split("+")
        )

        available = (
            self.get_available_languages()
        )

        missing = (
            requested - available
        )

        if missing:

            logger.warning(
                "Missing Tesseract language models: %s. "
                "Requested=%s Available=%s",
                sorted(missing),
                language,
                sorted(available),
            )

            # English is the safe fallback.

            if "eng" in available:

                return "eng"

            # If English itself isn't available,
            # use whatever requested language exists.

            available_requested = (
                requested & available
            )

            if available_requested:

                return "+".join(
                    sorted(
                        available_requested
                    )
                )

            raise ValueError(
                "Required Tesseract language data is not installed. "
                f"Requested language: {language}"
            )

        return language

    # -----------------------------------------------------
    # IMAGE PREPROCESSING
    # -----------------------------------------------------

    def preprocess_image(self, image):
        """
        Prepare image for OCR.

        Keeps the original RGB information and creates
        a moderately enhanced grayscale OCR image.

        The image is enlarged only when useful and capped
        by MAX_PROCESSED_DIMENSION.
        """

        # -------------------------------------------------
        # Convert to RGB
        # -------------------------------------------------

        image = image.convert("RGB")

        # -------------------------------------------------
        # Resize for OCR
        # -------------------------------------------------

        scale = 2

        target_width = image.width * scale
        target_height = image.height * scale

        longest_side = max(
            target_width,
            target_height
        )

        if longest_side > self.MAX_PROCESSED_DIMENSION:
            ratio = (
                self.MAX_PROCESSED_DIMENSION
                / longest_side
            )

            target_width = max(
                1,
                int(target_width * ratio)
            )

            target_height = max(
                1,
                int(target_height * ratio)
            )

        image = image.resize(
            (
                target_width,
                target_height
            ),
            Image.Resampling.LANCZOS
        )

        # -------------------------------------------------
        # Create grayscale OCR image
        # -------------------------------------------------

        gray = image.convert("L")

        # Moderate contrast.
        # Avoid aggressive enhancement because
        # screenshots may contain colored/highlighted text.
        gray = ImageEnhance.Contrast(
            gray
        ).enhance(
            1.35
        )

        # Light sharpening.
        gray = ImageEnhance.Sharpness(
            gray
        ).enhance(
            1.15
        )

        return gray  
    # -----------------------------------------------------
    # TEXT CLEANING
    #
    # IMPORTANT:
    # Preserve OCR line structure.
    #
    # The NLP pipeline uses lines to distinguish:
    #   - post text
    #   - social-media UI
    #   - metadata
    #   - engagement information
    #
    # Do NOT flatten all whitespace into one line.
    # -----------------------------------------------------

    def clean_text(self, text):
        """
        Minimal OCR normalization.

        IMPORTANT:
        Do NOT modify OCR characters, words, punctuation,
        Kannada/Hindi text, numbers, etc.

        Only:
        - convert newlines/tabs to spaces
        - collapse repeated whitespace
        - strip leading/trailing whitespace
        """

        if not text:
            return ""

        text = str(text)

        # Only whitespace normalization.
        # DO NOT alter any actual OCR characters.
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    # -----------------------------------------------------
    # PUBLISHER DETECTION
    # -----------------------------------------------------

    def detect_publisher(
        self,
        text: str
    ) -> dict:

        if not text:

            return {
                "publisher": None,
                "confidence": 0,
                "method": None,
            }

        normalized = text.lower()

        publishers = {

            "tv9 kannada":
                "TV9 Kannada",

            "tv9kannada":
                "TV9 Kannada",

            "tv9":
                "TV9",

            "rvcj":
                "RVCJ",

            "ndtv":
                "NDTV",

            "bbc news":
                "BBC News",

            "bbc":
                "BBC",

            "cnn":
                "CNN",

            "reuters":
                "Reuters",

            "times of india":
                "Times of India",

            "the times of india":
                "Times of India",

            "india today":
                "India Today",

            "india tv":
                "India TV",

            "hindustan times":
                "Hindustan Times",

            "the hindu":
                "The Hindu",

            "news18":
                "News18",

            "aaj tak":
                "Aaj Tak",

            "zee news":
                "Zee News",

            "abp news":
                "ABP News",

            "republic tv":
                "Republic TV",

            "republic bharat":
                "Republic Bharat",

            "the indian express":
                "The Indian Express",

            "indian express":
                "The Indian Express",
        }

        candidates = sorted(
            publishers.items(),
            key=lambda item: len(
                item[0]
            ),
            reverse=True,
        )

        for keyword, publisher in candidates:

            if keyword in normalized:

                return {
                    "publisher": publisher,
                    "confidence": 95,
                    "method": "ocr_known_publisher",
                }

        handles = re.findall(
            r"@([A-Za-z0-9_\.]{3,40})",
            text,
        )

        if handles:

            handle = handles[0]

            if (
                handle.lower()
                not in {
                    "user",
                    "gmail",
                    "instagram",
                    "twitter",
                    "facebook",
                }
            ):

                publisher = (
                    handle
                    .replace(
                        "_",
                        " "
                    )
                    .strip()
                )

                return {
                    "publisher": publisher,
                    "confidence": 80,
                    "method": "ocr_social_handle",
                }

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored = {

            "breaking",
            "live",
            "exclusive",
            "watch live",
            "subscribe",
            "suggested for you",
            "follow",
            "share",
            "comment",
            "like",
            "repost",
            "reply",
            "views",
        }

        for line in lines[:12]:

            clean = re.sub(
                r"[^A-Za-z0-9&.'@ _\-\u0966-\u096F\u0C80-\u0CFF]",
                "",
                line,
                flags=re.UNICODE,
            ).strip()

            if len(clean) < 4:
                continue

            if len(clean) > 50:
                continue

            lower = clean.lower()

            if lower in ignored:
                continue

            words = clean.split()

            if 1 <= len(words) <= 6:

                return {
                    "publisher": clean,
                    "confidence": 65,
                    "method": "ocr_visible_source",
                }

        return {
            "publisher": None,
            "confidence": 0,
            "method": None,
        }

    # -----------------------------------------------------
    # OCR CONFIDENCE
    # -----------------------------------------------------

    def calculate_ocr_confidence(
        self,
        data
    ):

        confidences = []

        for value in data.get(
            "conf",
            []
        ):

            try:

                confidence = float(
                    value
                )

                if confidence >= 0:

                    confidences.append(
                        confidence
                    )

            except (
                TypeError,
                ValueError
            ):

                continue

        if not confidences:

            return None

        return round(
            sum(confidences)
            / len(confidences),
            2
        )

    # -----------------------------------------------------
    # IMAGE VALIDATION
    # -----------------------------------------------------

    def validate_image(
        self,
        image_bytes
    ):

        if not image_bytes:

            raise ValueError(
                "Empty image file."
            )

        if (
            len(image_bytes)
            > self.MAX_FILE_SIZE
        ):

            raise ValueError(
                "Image file is too large. "
                "Maximum allowed size is 10 MB."
            )

        try:

            image = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

            image.verify()

        except UnidentifiedImageError:

            raise ValueError(
                "Invalid or unsupported image file."
            )

        except Exception:

            raise ValueError(
                "Unable to read the image file."
            )

        image = Image.open(
            io.BytesIO(
                image_bytes
            )
        )

        if image.format not in self.ALLOWED_FORMATS:

            raise ValueError(
                "Unsupported image format."
            )

        if (
            image.width <= 0
            or image.height <= 0
        ):

            raise ValueError(
                "Invalid image dimensions."
            )

        if (
            image.width > self.MAX_DIMENSION
            or image.height > self.MAX_DIMENSION
        ):

            raise ValueError(
                "Image dimensions are too large. "
                "Maximum dimension is 5000 pixels."
            )

        if (
            image.width
            * image.height
            > self.MAX_INPUT_PIXELS
        ):

            raise ValueError(
                "Image contains too many pixels."
            )

        return image
    
    # -----------------------------------------------------
    # REBUILD OCR TEXT FROM TESSERACT DATA
    #
    # Uses Tesseract's block / paragraph / line information
    # instead of relying only on image_to_string().
    #
    # This preserves the visual OCR line structure.
    # -----------------------------------------------------

    def rebuild_text_from_data(
        self,
        data
    ):
        texts = data.get(
            "text",
            []
        )

        blocks = data.get(
            "block_num",
            []
        )

        paragraphs = data.get(
            "par_num",
            []
        )

        lines = data.get(
            "line_num",
            []
        )

        tops = data.get(
            "top",
            []
        )

        lefts = data.get(
            "left",
            []
        )

        grouped = {}

        for index, value in enumerate(texts):

            value = str(
                value or ""
            ).strip()

            if not value:
                continue

            try:
                block = int(
                    blocks[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                block = 0

            try:
                paragraph = int(
                    paragraphs[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                paragraph = 0

            try:
                line = int(
                    lines[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                line = 0

            try:
                top = int(
                    tops[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                top = 0

            try:
                left = int(
                    lefts[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                left = 0

            key = (
                block,
                paragraph,
                line
            )

            if key not in grouped:
                grouped[key] = {
                    "top": top,
                    "left": left,
                    "words": []
                }

            grouped[key]["words"].append(
                (
                    left,
                    value
                )
            )

        ordered_lines = sorted(
            grouped.values(),
            key=lambda item: (
                item["top"],
                item["left"]
            )
        )

        result = []

        for item in ordered_lines:

            words = sorted(
                item["words"],
                key=lambda pair: pair[0]
            )

            line_text = " ".join(
                word
                for _, word in words
            ).strip()

            if line_text:
                result.append(
                    line_text
                )

        return "\n".join(
            result
        ).strip()

    # -----------------------------------------------------
    # BUILD OCR LINES FROM TESSERACT DATA
    #
    # Keeps:
    #   - text
    #   - x/y position
    #   - width/height
    #   - confidence
    #   - block/paragraph/line identity
    #
    # This is the basis for post-region segmentation.
    # -----------------------------------------------------

    def build_ocr_lines(
        self,
        data
    ):
        texts = data.get(
            "text",
            []
        )

        blocks = data.get(
            "block_num",
            []
        )

        paragraphs = data.get(
            "par_num",
            []
        )

        line_numbers = data.get(
            "line_num",
            []
        )

        lefts = data.get(
            "left",
            []
        )

        tops = data.get(
            "top",
            []
        )

        widths = data.get(
            "width",
            []
        )

        heights = data.get(
            "height",
            []
        )

        confidences = data.get(
            "conf",
            []
        )

        grouped = {}

        for index, value in enumerate(texts):

            value = str(
                value or ""
            ).strip()

            if not value:
                continue

            try:
                block = int(
                    blocks[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                block = 0

            try:
                paragraph = int(
                    paragraphs[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                paragraph = 0

            try:
                line_number = int(
                    line_numbers[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                line_number = 0

            try:
                left = int(
                    lefts[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                left = 0

            try:
                top = int(
                    tops[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                top = 0

            try:
                width = int(
                    widths[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                width = 0

            try:
                height = int(
                    heights[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                height = 0

            try:
                confidence = float(
                    confidences[index]
                )
            except (
                IndexError,
                TypeError,
                ValueError
            ):
                confidence = 0.0

            key = (
                block,
                paragraph,
                line_number
            )

            if key not in grouped:

                grouped[key] = {
                    "text": [],
                    "left": left,
                    "top": top,
                    "right": left + width,
                    "bottom": top + height,
                    "height": height,
                    "confidence": []
                }

            grouped[key]["text"].append(
                (
                    left,
                    value
                )
            )

            grouped[key]["left"] = min(
                grouped[key]["left"],
                left
            )

            grouped[key]["top"] = min(
                grouped[key]["top"],
                top
            )

            grouped[key]["right"] = max(
                grouped[key]["right"],
                left + width
            )

            grouped[key]["bottom"] = max(
                grouped[key]["bottom"],
                top + height
            )

            grouped[key]["height"] = max(
                grouped[key]["height"],
                height
            )

            if confidence >= 0:
                grouped[key]["confidence"].append(
                    confidence
                )

        result = []

        for item in grouped.values():

            words = sorted(
                item["text"],
                key=lambda value: value[0]
            )

            text = " ".join(
                word
                for _, word in words
            ).strip()

            if not text:
                continue

            confidence_values = (
                item["confidence"]
            )

            average_confidence = (
                sum(confidence_values)
                / len(confidence_values)
                if confidence_values
                else 0
            )

            result.append(
                {
                    "text": text,
                    "left": item["left"],
                    "top": item["top"],
                    "right": item["right"],
                    "bottom": item["bottom"],
                    "height": item["height"],
                    "confidence":
                        average_confidence
                }
            )

        result.sort(
            key=lambda item: (
                item["top"],
                item["left"]
            )
        )

        return result
    
    # -----------------------------------------------------
    # EXTRACT POST TEXT FROM OCR COORDINATES
    #
    # Social-media screenshots normally contain:
    #
    #   TOP    -> account/header
    #   MIDDLE -> actual post
    #   BOTTOM -> engagement / metadata
    #
    # We use OCR coordinates to establish the middle
    # content region instead of hard-coding pixel values.
    #
    # This is deliberately platform-agnostic.
    # -----------------------------------------------------

    def extract_post_text_from_data(
        self,
        data,
        image_width,
        image_height
    ):
        print("\n🔥🔥🔥 NEW extract_post_text_from_data CALLED 🔥🔥🔥")
        lines = self.build_ocr_lines(data)

        if not lines:
            return ""

        # -------------------------------------------------
        # Normalize only unnecessary whitespace.
        # IMPORTANT:
        # Do not destroy OCR structure unnecessarily.
        # -------------------------------------------------

        def normalized(value):
            text = str(value or "")
            text = text.replace("\u200c", "")
            text = text.replace("\u200d", "")
            text = re.sub(r"[ \t]+", " ", text)
            return text.strip()

        
        # -------------------------------------------------
        # Social-media UI phrases
        #
        # OCR is not always exact.
        #
        # Examples Tesseract may produce:
        #   Show translation
        #   Showtranslation
        #   Show  translation
        #   See translation
        #   Seetranslation
        #   More
        #
        # Keep this platform-agnostic.
        # -------------------------------------------------

        ui_phrases = {
            "follow",
            "following",
            "like",
            "likes",
            "comment",
            "comments",
            "share",
            "shares",
            "repost",
            "reposts",
            "bookmark",
            "bookmarks",
            "reply",
            "replies",
            "more",
            "show translation",
            "showtranslation",
            "see translation",
            "seetranslation",
            "translate",
            "translation",
        }

        metadata_words = {
            "views",
            "view",
            "likes",
            "like",
            "comments",
            "comment",
            "replies",
            "reply",
            "shares",
            "share",
            "reposts",
            "repost",
            "bookmarks",
            "bookmark",
        }


        def normalize_ui_text(text):

            value = normalized(text).lower()

            # Remove spaces/punctuation only for UI comparison.
            # This does NOT modify the actual returned post text.
            comparison = re.sub(
                r"[\s\W_]+",
                "",
                value,
                flags=re.UNICODE
            )

            return value, comparison


        def is_ui_line(text):

            lower, compact = normalize_ui_text(text)

            # Exact normal form.
            if lower in ui_phrases:
                return True

            # OCR may join words:
            #
            # Show translation -> Showtranslation
            # See translation  -> Seetranslation
            #
            if compact in {
                "follow",
                "following",
                "like",
                "likes",
                "comment",
                "comments",
                "share",
                "shares",
                "repost",
                "reposts",
                "bookmark",
                "bookmarks",
                "reply",
                "replies",
                "more",
                "showtranslation",
                "seetranslation",
                "translate",
                "translation",
            }:
                return True

            # Token-based UI detection.
            tokens = {
                token.strip(
                    ".,!?|:;·•-@()[]{}<>\"'“”‘’"
                )
                for token in lower.split()
            }

            tokens.discard("")

            if (
                tokens
                and tokens.issubset(ui_phrases)
            ):
                return True

            return False


        def is_metadata_line(text):

            lower = normalized(text).lower()

            words = set(
                re.findall(
                    r"[a-z]+",
                    lower
                )
            )

            # If actual Kannada/Hindi content is present,
            # do NOT delete the whole line merely because
            # OCR also detected a UI word.
            has_kannada = bool(
                re.search(
                    r"[\u0C80-\u0CFF]",
                    text
                )
            )

            has_devanagari = bool(
                re.search(
                    r"[\u0900-\u097F]",
                    text
                )
            )

            if has_kannada or has_devanagari:
                return False

            return bool(
                words & metadata_words
            )


        def is_timestamp(text):

            value = normalized(text)

            return bool(
                re.fullmatch(
                    r"""
                    \d{1,2}
                    :
                    \d{2}
                    (?:
                        \s*
                        (?:am|pm)
                    )?
                    """,
                    value,
                    flags=
                        re.IGNORECASE |
                        re.VERBOSE
                )
            )


        def is_numeric_ui(text):

            value = (
                normalized(text)
                .replace(",", "")
                .replace("·", " ")
            )

            tokens = value.split()

            if not tokens:
                return False

            return all(
                re.fullmatch(
                    r"\d+(?:\.\d+)?[KMB]?",
                    token,
                    flags=re.IGNORECASE
                )
                for token in tokens
            )
        # -------------------------------------------------
        # Remove ONLY obvious UI fragments from a mixed line.
        #
        # Example:
        #
        # "ಅಶೋಕ್ ಅಣ್ಣಾ ... More"
        #
        # becomes:
        #
        # "ಅಶೋಕ್ ಅಣ್ಣಾ ..."
        # -------------------------------------------------

        def remove_inline_ui(text):

            cleaned = normalized(text)

            # Remove common trailing UI markers.
            cleaned = re.sub(
                r"""
                \s+
                (?:
                    \.\.\.
                    \s*
                )?
                (?:
                    More
                    |
                    See\s+translation
                    |
                    Show\s+translation
                    |
                    Translate
                    |
                    Translation
                )
                \s*$
                """,
                "",
                cleaned,
                flags=re.IGNORECASE | re.VERBOSE
            )

            return cleaned.strip()

        # -------------------------------------------------
        # Maximum reasonable OCR box height.
        # -------------------------------------------------

        max_reasonable_height = max(
            80,
            int(image_height * 0.18)
        )

        candidates = []

        for original_line in lines:

            line = dict(original_line)

            text = normalized(
                line.get("text", "")
            )

            if not text:
                continue

            # Reject abnormal giant Tesseract boxes.
            if (
                line.get("height", 0)
                > max_reasonable_height
            ):
                continue

            # Pure UI only.
            if is_ui_line(text):
                continue

            if is_timestamp(text):
                continue

            if is_metadata_line(text):
                continue

            if is_numeric_ui(text):
                continue

            # Remove ONLY inline UI suffixes.
            text = remove_inline_ui(text)

            if not text:
                continue

            line["text"] = text

            # -------------------------------------------------
            # Relative vertical position.
            # -------------------------------------------------

            center_y = (
                line["top"]
                + line["bottom"]
            ) / 2.0

            line["relative_y"] = (
                center_y
                / max(
                    image_height,
                    1
                )
            )

            candidates.append(line)

        if not candidates:
            return ""

        # -------------------------------------------------
        # Median normal line height.
        # -------------------------------------------------

        heights = sorted(
            max(
                1,
                line["height"]
            )
            for line in candidates
        )

        median_height = heights[
            len(heights) // 2
        ]

        # -------------------------------------------------
        # Content scoring.
        # -------------------------------------------------

        def content_score(line):

            text = line["text"]

            characters = len(
                re.sub(
                    r"\s+",
                    "",
                    text
                )
            )

            words = len(
                text.split()
            )

            kannada = len(
                re.findall(
                    r"[\u0C80-\u0CFF]",
                    text
                )
            )

            devanagari = len(
                re.findall(
                    r"[\u0900-\u097F]",
                    text
                )
            )

            english = len(
                re.findall(
                    r"[A-Za-z]",
                    text
                )
            )

            script_chars = (
                kannada
                + devanagari
                + english
            )

            score = (
                characters
                + (words * 3)
                + (script_chars * 2)
            )

            # Strongly prefer Kannada-containing text.
            if kannada > 0:
                score += min(
                    kannada * 2,
                    300
                )

            # Very short text at extreme positions is
            # more likely UI.
            if (
                line["relative_y"] < 0.15
                and characters < 40
            ):
                score *= 0.35

            if (
                line["relative_y"] > 0.90
                and characters < 40
            ):
                score *= 0.25

            return score

        for line in candidates:

            line["score"] = content_score(line)

        # -------------------------------------------------
        # Vertical ordering.
        # -------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item["top"],
                item["left"]
            )
        )

        # -------------------------------------------------
        # Vertical grouping.
        # -------------------------------------------------

        max_gap = max(
            25,
            int(
                median_height * 1.8
            )
        )

        regions = []

        current = []

        previous_bottom = None

        for line in candidates:

            if previous_bottom is None:

                current = [
                    line
                ]

            else:

                gap = (
                    line["top"]
                    - previous_bottom
                )

                if gap <= max_gap:

                    current.append(line)

                else:

                    if current:
                        regions.append(
                            current
                        )

                    current = [
                        line
                    ]

            previous_bottom = max(
                previous_bottom or 0,
                line["bottom"]
            )

        if current:
            regions.append(current)

        if not regions:
            return ""

        # -------------------------------------------------
        # Score regions.
        # -------------------------------------------------

        region_scores = []

        for region in regions:

            total_score = sum(
                line["score"]
                for line in region
            )

            total_chars = sum(
                len(
                    re.sub(
                        r"\s+",
                        "",
                        line["text"]
                    )
                )
                for line in region
            )

            kannada_chars = sum(
                len(
                    re.findall(
                        r"[\u0C80-\u0CFF]",
                        line["text"]
                    )
                )
                for line in region
            )

            region_top = min(
                line["top"]
                for line in region
            )

            region_bottom = max(
                line["bottom"]
                for line in region
            )

            region_scores.append(
                {
                    "lines": region,
                    "score": total_score,
                    "characters": total_chars,
                    "kannada": kannada_chars,
                    "top": region_top,
                    "bottom": region_bottom,
                }
            )

        # -------------------------------------------------
        # Rank regions.
        # -------------------------------------------------

        def region_rank(region):

            line_count = len(
                region["lines"]
            )

            score = region["score"]

            score += (
                min(
                    line_count,
                    8
                ) * 12
            )

            score += (
                min(
                    region["kannada"],
                    150
                ) * 2
            )

            if region["characters"] < 12:
                score *= 0.25

            return score

        best_region = max(
            region_scores,
            key=region_rank
        )

        # -------------------------------------------------
        # Select nearby post regions.
        # -------------------------------------------------

        selected_regions = [
            best_region
        ]

        for region in region_scores:

            if region is best_region:
                continue

            gap = min(
                abs(
                    region["top"]
                    - best_region["bottom"]
                ),
                abs(
                    best_region["top"]
                    - region["bottom"]
                )
            )

            if (
                gap <= max_gap
                and region["characters"] >= 20
                and (
                    region["kannada"] > 0
                    or region["characters"] >= 40
                )
            ):

                selected_regions.append(
                    region
                )

        # -------------------------------------------------
        # Flatten selected lines.
        # -------------------------------------------------

        selected_lines = []

        for region in selected_regions:

            selected_lines.extend(
                region["lines"]
            )

        selected_lines.sort(
            key=lambda item: (
                item["top"],
                item["left"]
            )
        )

        # -------------------------------------------------
        # Final protection.
        # -------------------------------------------------

        result = []

        for line in selected_lines:

            text = normalized(
                line["text"]
            )

            if not text:
                continue

            if is_ui_line(text):
                continue

            if is_timestamp(text):
                continue

            if is_metadata_line(text):
                continue

            if is_numeric_ui(text):
                continue

            result.append(text)

        return "\n".join(result).strip()
    
    def repair_indic_spacing(self, text):
        """
        Safely normalize Indic OCR text.

        Do NOT blindly join every Indic character separated by
        whitespace. OCR word boundaries can be legitimate.
        """

        if not text:
            return text

        import unicodedata

        text = unicodedata.normalize("NFC", str(text))

        # Remove whitespace immediately before Indic combining marks.
        # This repairs things like:
        #   ಮೂ ತ್ರ -> ಮೂತ್ರ
        # without merging entire words.
        text = re.sub(
            r"\s+([\u0CBC-\u0CCD\u0900-\u097F])",
            r"\1",
            text
        )

        # Normalize repeated horizontal whitespace.
        text = re.sub(r"[ \t]+", " ", text)

        # Preserve meaningful newlines.
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def run_ocr_candidates(
        self,
        image,
        language
    ):
        """
        Run OCR using multiple Tesseract page segmentation modes.

        IMPORTANT:
        The actual OCR text used by the analysis pipeline comes
        directly from pytesseract.image_to_string().

        We do NOT reconstruct or modify OCR characters.

        Only whitespace normalization is applied before returning
        the candidate:
            - newlines/tabs -> spaces
            - repeated whitespace -> one space
            - leading/trailing whitespace removed

        image_to_data() is still used separately for OCR confidence
        and statistics.
        """

        candidates = []

        configs = [
            "--psm 6",
            "--psm 11",
            "--psm 12",
        ]

        for config in configs:

            try:

                # -------------------------------------------------
                # OCR DATA
                #
                # Used ONLY for confidence/statistics.
                # -------------------------------------------------

                data = pytesseract.image_to_data(
                    image,
                    lang=language,
                    config=config,
                    output_type=pytesseract.Output.DICT,
                )

                # -------------------------------------------------
                # DIRECT RAW OCR TEXT
                #
                # IMPORTANT:
                # Do NOT use rebuild_text_from_data() here.
                #
                # image_to_string() gives us Tesseract's actual
                # OCR text output.
                # -------------------------------------------------

                raw_ocr_text = pytesseract.image_to_string(
                    image,
                    lang=language,
                    config=config,
                )

                # -------------------------------------------------
                # Confidence
                # -------------------------------------------------

                confidence = (
                    self.calculate_ocr_confidence(
                        data
                    )
                )

                if confidence is None:
                    confidence = 0

                # -------------------------------------------------
                # Token count
                #
                # Still obtained from image_to_data().
                # This does NOT modify the OCR text.
                # -------------------------------------------------

                words = []

                for value in data.get("text", []):

                    value = str(value).strip()

                    if value:
                        words.append(value)

                word_count = len(words)

                # -------------------------------------------------
                # TEXT FOR ANALYSIS
                #
                # ONLY whitespace normalization.
                #
                # NO:
                # - character replacement
                # - Kannada modification
                # - Hindi modification
                # - punctuation modification
                # - number modification
                # - OCR correction
                # -------------------------------------------------

                candidate_text = self.clean_text(
                    raw_ocr_text
                )

                # -------------------------------------------------
                # Character statistics
                # -------------------------------------------------

                total_chars = len(
                    re.sub(
                        r"\s+",
                        "",
                        candidate_text
                    )
                )

                kannada_chars = len(
                    re.findall(
                        r"[\u0C80-\u0CFF]",
                        candidate_text
                    )
                )

                hindi_chars = len(
                    re.findall(
                        r"[\u0900-\u097F]",
                        candidate_text
                    )
                )

                english_chars = len(
                    re.findall(
                        r"[A-Za-z]",
                        candidate_text
                    )
                )

                digits = len(
                    re.findall(
                        r"\d",
                        candidate_text
                    )
                )

                # -------------------------------------------------
                # Script characters
                # -------------------------------------------------

                script_chars = (
                    kannada_chars
                    + hindi_chars
                    + english_chars
                )

                # -------------------------------------------------
                # Garbage / suspicious characters
                #
                # This is ONLY for candidate scoring.
                # It does NOT modify candidate_text.
                # -------------------------------------------------

                suspicious_chars = len(
                    re.findall(
                        r"[^A-Za-z0-9\s\u0900-\u097F\u0C80-\u0CFF.,!?;:'\"%()\-]",
                        candidate_text
                    )
                )

                # -------------------------------------------------
                # Line count
                #
                # candidate_text has whitespace normalized, so this
                # will normally be one logical line.
                # This statistic is retained only for compatibility.
                # -------------------------------------------------

                lines = [
                    line.strip()
                    for line in candidate_text.splitlines()
                    if line.strip()
                ]

                line_count = len(lines)

                # -------------------------------------------------
                # Script ratio
                # -------------------------------------------------

                if total_chars > 0:

                    script_ratio = (
                        script_chars / total_chars
                    )

                else:

                    script_ratio = 0

                # -------------------------------------------------
                # Garbage ratio
                # -------------------------------------------------

                if total_chars > 0:

                    garbage_ratio = (
                        suspicious_chars / total_chars
                    )

                else:

                    garbage_ratio = 1

                # -------------------------------------------------
                # SCORE
                # -------------------------------------------------

                score = 0.0

                # OCR confidence
                score += (
                    confidence * 0.35
                )

                # Useful text length
                score += (
                    min(total_chars, 500)
                    * 0.12
                )

                # Multi-line post content
                score += (
                    min(line_count, 10)
                    * 5
                )

                # Kannada
                score += (
                    min(kannada_chars, 300)
                    * 0.55
                )

                # Hindi
                score += (
                    min(hindi_chars, 300)
                    * 0.45
                )

                # English
                score += (
                    min(english_chars, 150)
                    * 0.10
                )

                # Suspicious OCR characters
                score -= (
                    min(
                        suspicious_chars,
                        100
                    )
                    * 0.50
                )

                # Poor script coverage
                if (
                    language != "eng"
                    and total_chars >= 20
                    and script_ratio < 0.20
                ):

                    score -= 15

                # Empty candidate
                if total_chars == 0:

                    score = -999

                # -------------------------------------------------
                # SAVE CANDIDATE
                # -------------------------------------------------

                candidates.append(
                    {
                        "config":
                            config,

                        # THIS is the text that should flow
                        # toward analysis/translation.
                        "raw_text":
                            candidate_text,

                        "post_text":
                            candidate_text,

                        "confidence":
                            confidence,

                        "word_count":
                            word_count,

                        "score":
                            score,

                        "kannada_chars":
                            kannada_chars,

                        "hindi_chars":
                            hindi_chars,

                        "english_chars":
                            english_chars,

                        "total_chars":
                            total_chars,

                        "suspicious_chars":
                            suspicious_chars,

                        "line_count":
                            line_count,
                    }
                )

            except Exception:

                logger.exception(
                    "OCR candidate failed: %s",
                    config
                )

        # =========================================================
        # NO CANDIDATES
        # =========================================================

        if not candidates:

            raise ValueError(
                "All OCR attempts failed."
            )

        # =========================================================
        # DEBUG
        # =========================================================

        print(
            "\n========== OCR CANDIDATES =========="
        )

        for item in candidates:

            print(
                {
                    "config":
                        item["config"],

                    "score":
                        round(
                            item["score"],
                            2
                        ),

                    "confidence":
                        round(
                            item["confidence"],
                            2
                        ),

                    "words":
                        item["word_count"],

                    "kannada":
                        item["kannada_chars"],

                    "hindi":
                        item["hindi_chars"],

                    "english":
                        item["english_chars"],

                    "lines":
                        item["line_count"],

                    "garbage":
                        item["suspicious_chars"],

                    "text":
                        item["post_text"][:500]
                        if item["post_text"]
                        else "",
                }
            )

        print(
            "====================================\n"
        )

        # =========================================================
        # SELECT BEST CANDIDATE
        # =========================================================

        best = max(
            candidates,
            key=lambda item: item["score"]
        )

        # =========================================================
        # DEBUG SELECTED OCR
        # =========================================================

        print(
            "\n========== SELECTED OCR =========="
        )

        print(
            "OCR CONFIG:",
            best["config"]
        )

        print(
            "OCR SCORE:",
            round(
                best["score"],
                2
            )
        )

        print(
            "OCR CONFIDENCE:",
            round(
                best["confidence"],
                2
            )
        )

        print(
            "KANNADA CHARACTERS:",
            best["kannada_chars"]
        )

        print(
            "HINDI CHARACTERS:",
            best["hindi_chars"]
        )

        print(
            "ENGLISH CHARACTERS:",
            best["english_chars"]
        )

        print(
            "OCR TEXT:",
            best["post_text"]
        )

        print(
            "==================================\n"
        )

        logger.info(
            "OCR candidates: %s",
            [
                {
                    "config":
                        item["config"],

                    "confidence":
                        round(
                            item["confidence"],
                            2
                        ),

                    "words":
                        item["word_count"],

                    "score":
                        round(
                            item["score"],
                            2
                        ),

                    "kannada":
                        item["kannada_chars"],

                    "hindi":
                        item["hindi_chars"],
                }
                for item in candidates
            ]
        )

        logger.info(
            "Selected OCR configuration: %s",
            best["config"]
        )

        return best
    # ============================================================
    # DETECT ACTUAL TEXT LANGUAGE
    # ============================================================

    def detect_text_language(self, text):
        
        if not text:
            return "Unknown"

        text = str(text)

        english_count = 0
        hindi_count = 0
        kannada_count = 0

        for char in text:

            code = ord(char)

            # Devanagari
            if 0x0900 <= code <= 0x097F:
                hindi_count += 1

            # Kannada
            elif 0x0C80 <= code <= 0x0CFF:
                kannada_count += 1

            # English alphabet
            elif (
                "A" <= char <= "Z"
                or "a" <= char <= "z"
            ):
                english_count += 1

        total = (
            english_count
            + hindi_count
            + kannada_count
        )

        if total == 0:
            return "Unknown"

        # ---------------------------------------------------------
        # Calculate script ratios
        # ---------------------------------------------------------

        english_ratio = english_count / total
        hindi_ratio = hindi_count / total
        kannada_ratio = kannada_count / total

        # ---------------------------------------------------------
        # Dominant-language detection
        #
        # Social-media screenshots commonly contain:
        # - publisher names
        # - timestamps
        # - buttons
        # - UI labels
        # - English acronyms
        #
        # Therefore, a small amount of English should NOT turn
        # an otherwise Kannada/Hindi post into "Mixed".
        # ---------------------------------------------------------

        ratios = {
            "English": english_ratio,
            "Hindi": hindi_ratio,
            "Kannada": kannada_ratio,
        }

        sorted_languages = sorted(
            ratios.items(),
            key=lambda item: item[1],
            reverse=True
        )

        primary_language, primary_ratio = sorted_languages[0]
        secondary_language, secondary_ratio = sorted_languages[1]

        # ---------------------------------------------------------
        # Clearly dominant language
        # ---------------------------------------------------------

        if primary_ratio >= 0.60:
            return primary_language

        # ---------------------------------------------------------
        # Genuine mixed-language content
        #
        # Require both languages to have substantial presence.
        # ---------------------------------------------------------

        if (
            primary_ratio >= 0.40
            and secondary_ratio >= 0.30
        ):
            return "Mixed"

        # ---------------------------------------------------------
        # Otherwise use the dominant script.
        # This prevents OCR/UI noise from producing Mixed.
        # ---------------------------------------------------------

        return primary_language
    # -----------------------------------------------------
    # OCR EXTRACTION
    # -----------------------------------------------------

    def extract_text_from_image(
        self,
        image_bytes,
        language="eng+hin+kan"
    ):

        try:

            # ---------------------------------------------
            # Validate language
            # ---------------------------------------------

            language = (
                self.normalize_language(
                    language
                )
            )

            language = (
                self.validate_language_models(
                    language
                )
            )

            logger.info(
                "OCR language selected: %s",
                language
            )

            # ---------------------------------------------
            # Validate image
            # ---------------------------------------------

            image = self.validate_image(
                image_bytes
            )

            # ---------------------------------------------
            # Preprocess
            # ---------------------------------------------

            processed = (
                self.preprocess_image(
                    image
                )
            )

            # ---------------------------------------------
            # OCR
            # ---------------------------------------------

            ocr_result = self.run_ocr_candidates(
                processed,
                language
            )

            # -------------------------------------------------
            # RAW OCR TEXT
            # -------------------------------------------------
            #
            # IMPORTANT:
            # Use the selected Tesseract raw_text directly.
            #
            # Do NOT use:
            # - post_text
            # - structured_text
            # - coordinate-based post extraction
            # - character replacement
            # - Kannada/Hindi repair
            # - social-media text filtering
            #
            # The only processing below is whitespace
            # normalization through clean_text().
            #

            ocr_raw_text = str(
                ocr_result.get(
                    "raw_text",
                    ""
                )
            )

            # -------------------------------------------------
            # FINAL TEXT FOR NLP
            # -------------------------------------------------
            #
            # This is the ONLY transformation applied to
            # the raw OCR before sending it to analysis.
            #
            # clean_text() only:
            #   1. converts newlines/tabs/etc. to spaces
            #   2. collapses repeated whitespace
            #   3. strips leading/trailing whitespace
            #
            # No OCR characters are changed.
            #

            analysis_text = self.clean_text(
                ocr_raw_text
            )

            # -------------------------------------------------
            # DEBUG
            # -------------------------------------------------

            print(
                "\n================================================="
            )

            print(
                "DEBUG: RAW OCR TEXT"
            )

            print(
                "================================================="
            )

            print(
                ocr_raw_text
            )

            print(
                "\n================================================="
            )

            print(
                "DEBUG: FINAL TEXT SENT TO NLP"
            )

            print(
                "================================================="
            )

            print(
                analysis_text
            )

            print(
                "=================================================\n"
            )

            # ---------------------------------------------
            # CONFIDENCE
            # ---------------------------------------------

            ocr_confidence = float(
                ocr_result.get(
                    "confidence",
                    0
                )
            )

            # ---------------------------------------------
            # LANGUAGE
            # ---------------------------------------------

            detected_language = (
                self.detect_text_language(
                    analysis_text
                )
            )

            # ---------------------------------------------
            # PUBLISHER
            # ---------------------------------------------

            publisher_info = (
                self.detect_publisher(
                    analysis_text
                )
            )

            # ---------------------------------------------
            # RESULT
            # ---------------------------------------------

            return {

                "status":
                    "success",

                # This is the whitespace-normalized
                # raw Tesseract text that goes to NLP.
                "extracted_text":
                    analysis_text,

                # Keep this identical to extracted_text
                # so downstream analysis receives the
                # same text.
                "post_text":
                    analysis_text,

                "engagement_text":
                    "",

                "ordered_values":
                    {},

                # Original raw Tesseract output preserved.
                "raw_text":
                    ocr_raw_text,

                "confidence":
                    ocr_confidence,

                "publisher":
                    publisher_info[
                        "publisher"
                    ],

                "publisher_confidence":
                    publisher_info[
                        "confidence"
                    ],

                "publisher_detection_method":
                    publisher_info[
                        "method"
                    ],

                "word_count":
                    len(
                        analysis_text.split()
                    ),

                "ocr_language":
                    language,

                "language":
                    detected_language,

                "ready_for_analysis":
                    True,
            }

        except Exception as e:

            logger.exception(
                "OCR processing failed: %s",
                e
            )

            return {

                "status":
                    "error",

                "message":
                    str(e),
            }

ocr_service = OCRService()