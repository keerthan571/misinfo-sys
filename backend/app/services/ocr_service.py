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

    def preprocess_image(
        self,
        image
    ):

        image = image.convert(
            "L"
        )

        scale = 4

        target_width = (
            image.width * scale
        )

        target_height = (
            image.height * scale
        )

        longest_side = max(
            target_width,
            target_height
        )

        if (
            longest_side
            > self.MAX_PROCESSED_DIMENSION
        ):

            ratio = (
                self.MAX_PROCESSED_DIMENSION
                / longest_side
            )

            target_width = max(
                1,
                int(
                    target_width
                    * ratio
                )
            )

            target_height = max(
                1,
                int(
                    target_height
                    * ratio
                )
            )

        image = image.resize(
            (
                target_width,
                target_height
            )
        )

        image = ImageEnhance.Contrast(
            image
        ).enhance(
            2
        )

        image = ImageEnhance.Sharpness(
            image
        ).enhance(
            3
        )

        image = image.filter(
            ImageFilter.SHARPEN
        )

        return image

    # -----------------------------------------------------
    # TEXT CLEANING
    #
    # IMPORTANT:
    #
    # Do NOT restrict this to ASCII.
    #
    # \w supports Unicode characters,
    # which preserves Hindi/Kannada text.
    # -----------------------------------------------------

    def clean_text(
        self,
        text
    ):

        text = re.sub(
            r"[^\w\s.,!?@#%:/\-\u0966-\u096F\u0C80-\u0CFF]",
            " ",
            text,
            flags=re.UNICODE
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
            flags=re.UNICODE
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
    # OCR EXTRACTION
    # -----------------------------------------------------

    def extract_text_from_image(
        self,
        image_bytes,
        language="eng"
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
            # OCR DATA
            # ---------------------------------------------

            ocr_data = (
                pytesseract.image_to_data(
                    processed,
                    lang=language,
                    config="--psm 6",
                    output_type=(
                        pytesseract.Output.DICT
                    ),
                )
            )

            # ---------------------------------------------
            # OCR TEXT
            # ---------------------------------------------

            raw_text = (
                pytesseract.image_to_string(
                    processed,
                    lang=language,
                    config="--psm 6"
                )
            )

            # ---------------------------------------------
            # CLEAN TEXT
            # ---------------------------------------------

            cleaned = self.clean_text(
                raw_text
            )

            # ---------------------------------------------
            # CONFIDENCE
            # ---------------------------------------------

            ocr_confidence = (
                self.calculate_ocr_confidence(
                    ocr_data
                )
            )

            # ---------------------------------------------
            # PUBLISHER
            # ---------------------------------------------

            publisher_info = (
                self.detect_publisher(
                    cleaned
                )
            )

            # ---------------------------------------------
            # RESULT
            # ---------------------------------------------

            return {

                "status":
                    "success",

                "extracted_text":
                    cleaned,

                "post_text":
                    cleaned,

                "engagement_text":
                    "",

                "ordered_values":
                    {},

                "raw_text":
                    raw_text,

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
                        cleaned.split()
                    ),

                "language":
                    language,

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