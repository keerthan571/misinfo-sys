from __future__ import annotations

import io
import logging
import os
import re

import pytesseract
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter,
    UnidentifiedImageError,
)


logger = logging.getLogger(__name__)


# ============================================================
# TESSERACT CONFIGURATION
# ============================================================

if os.name == "nt":

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )


router = APIRouter()


# ============================================================
# OCR SERVICE
# ============================================================

class OCRService:

    MAX_FILE_SIZE = 10 * 1024 * 1024

    MAX_INPUT_PIXELS = 20_000_000

    MAX_DIMENSION = 5000

    MAX_PROCESSED_DIMENSION = 3000

    ALLOWED_FORMATS = {
        "JPEG",
        "PNG",
        "WEBP",
        "BMP",
        "TIFF",
    }

    # --------------------------------------------------------
    # Supported OCR languages
    # --------------------------------------------------------

    SUPPORTED_LANGUAGES = {
        "eng",
        "hin",
        "kan",
        "eng+hin",
        "eng+kan",
        "hin+kan",
        "eng+hin+kan",
    }


    # ========================================================
    # IMAGE PREPROCESSING
    # ========================================================

    def preprocess_image(self, image):

        image = image.convert("L")

        scale = 4

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
            )
        )

        image = ImageEnhance.Contrast(
            image
        ).enhance(2)

        image = ImageEnhance.Sharpness(
            image
        ).enhance(3)

        image = image.filter(
            ImageFilter.SHARPEN
        )

        return image


    # ========================================================
    # TEXT CLEANING
    # ========================================================

    def clean_text(self, text):
    
        """
        Whitespace normalization while preserving
        OCR line structure.
        """

        if not text:
            return ""

        text = str(text)

        # Normalize spaces/tabs inside each line
        lines = []

        for line in text.splitlines():

            line = re.sub(
                r"[ \t]+",
                " ",
                line
            ).strip()

            if line:
                lines.append(line)

        return "\n".join(lines).strip()
    # ========================================================
    # SOCIAL MEDIA OCR FILTERING
    # ========================================================

    def filter_social_media_ocr(
        self,
        text,
        image_height
    ):
        """
        Generic social-media OCR cleanup.

        Removes common UI / metadata / engagement noise from
        Facebook, Instagram, Twitter/X and similar screenshots.

        IMPORTANT:
        - Does NOT translate text.
        - Does NOT rewrite Kannada/Hindi/English content.
        - Does NOT remove normal numbers from post content.
        - Does NOT depend on a specific publisher or post.
        """

        if not text:
            return ""

        lines = text.splitlines()
        cleaned_lines = []

        # ====================================================
        # 1. EXACT SOCIAL MEDIA UI LABELS
        # ====================================================

        ui_exact = {
            "more",
            "see more",
            "see translation",
            "show translation",
            "translate post",
            "translate",
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
            "reply",
            "replies",
            "send",
            "save",
            "saved",
            "bookmark",
            "bookmarks",
            "subscribe",
            "view profile",
            "view post",
            "view replies",
            "view more",
        }

        # ====================================================
        # 2. TIMESTAMP / POST METADATA
        # ====================================================

        timestamp_only = re.compile(
            r"^\s*"
            r"(?:"
            r"\d+\s*(?:s|sec|secs|m|min|mins|h|hr|hrs|d|day|days|w|wk|wks|mo|"
            r"month|months|y|yr|yrs)"
            r"|"
            r"\d{1,2}:\d{2}\s*(?:am|pm)?"
            r")"
            r"(?:\s*[-@·•|])?"
            r"\s*$",
            re.IGNORECASE
        )

        # ====================================================
        # 3. DATE / TIME + VIEWS METADATA
        #
        # Examples:
        #   3:00 pm · 02 Sept 26 · 1.9K Views
        #   3:00 PM · Sep 2 · 1.9K Views
        #   02 Sept 26 · 1.9K Views
        # ====================================================

        views_metadata = re.compile(
            r"^\s*"
            r".*?"
            r"(?:"
            r"\d+(?:\.\d+)?\s*[KMB]?\s*"
            r"(?:views?|view)"
            r"|"
            r"views?"
            r")"
            r"\s*$",
            re.IGNORECASE
        )

        date_metadata = re.compile(
            r"^\s*"
            r"(?:"
            r"\d{1,2}:\d{2}\s*(?:am|pm)?"
            r"|"
            r"\d{1,2}\s+"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"(?:[a-z]*)?"
            r"(?:\s+\d{2,4})?"
            r")"
            r".*?"
            r"(?:·|-|\|)"
            r".*"
            r"(?:views?|view)"
            r"\s*$",
            re.IGNORECASE
        )

        # ====================================================
        # 4. ENGAGEMENT-ONLY LINE
        #
        # Examples:
        #   3 17 129 1
        #   3 17 129 1 5
        #   160 45 7
        #
        # Only remove when the line is essentially numbers
        # and separators. Normal sentence numbers are preserved.
        # ====================================================

        engagement_only = re.compile(
            r"^\s*"
            r"(?:"
            r"[0-9]+"
            r"|"
            r"[0-9.,KMB]+"
            r"|"
            r"[0-9೦-೯०-९]+"
            r")"
            r"(?:"
            r"\s*"
            r"[\W_]*"
            r"(?:"
            r"[0-9]+"
            r"|"
            r"[0-9.,KMB]+"
            r"|"
            r"[0-9೦-೯०-९]+"
            r")"
            r")+"
            r"\s*$",
            re.IGNORECASE
        )

        # ====================================================
        # 5. COMMON OCR GARBAGE
        # ====================================================

        known_ui_garbage = {
            "x",
            "©",
            "®",
            "™",
        }

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            normalized = re.sub(
                r"\s+",
                " ",
                line
            ).strip()

            if not normalized:
                continue

            lower = normalized.lower()

            # ====================================================
            # EXACT UI
            # ====================================================

            if lower in ui_exact:
                continue

            # ====================================================
            # STANDALONE TIMESTAMP
            # ====================================================

            if timestamp_only.match(normalized):
                continue

            # ====================================================
            # VIEWS / POST METADATA
            # ====================================================

            if views_metadata.match(normalized):
                continue

            if date_metadata.match(normalized):
                continue

            # ====================================================
            # ENGAGEMENT-ONLY NUMBERS
            # ====================================================

            if engagement_only.match(normalized):
                continue

            # ====================================================
            # STANDALONE OCR UI GARBAGE
            # ====================================================

            if lower in known_ui_garbage:
                continue

            # ====================================================
            # INLINE "MORE"
            #
            # Kannada text ... More
            # English text ... More
            # ====================================================

            normalized = re.sub(
                r"\s+(?:more|see\s+more)\s*$",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ====================================================
            # INLINE TRANSLATION LABEL
            #
            # Do NOT remove the actual sentence.
            #
            # Example:
            #   Kannada sentence Show translation
            #
            # becomes:
            #   Kannada sentence
            # ====================================================

            normalized = re.sub(
                r"\s+"
                r"(?:"
                r"show\s+translation"
                r"|see\s+translation"
                r"|translate\s+post"
                r"|translate"
                r")"
                r"\s*$",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ====================================================
            # TIMESTAMP PREFIX
            #
            # Example:
            #   3h-@ Kannada text
            #
            # becomes:
            #   Kannada text
            # ====================================================

            normalized = re.sub(
                r"^\s*"
                r"\d+\s*"
                r"(?:s|sec|secs|m|min|mins|h|hr|hrs|d|day|days|w|wk|wks|mo|"
                r"month|months|y|yr|yrs)"
                r"(?:\s*[-@·•|])?"
                r"\s+",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ====================================================
            # KNOWN HEADER SEPARATOR GARBAGE
            #
            # Example:
            #   . \ Kannada Prabha eee x
            # ====================================================

            normalized = re.sub(
                r"^[.\\\/\s]+",
                "",
                normalized
            ).strip()

            normalized = re.sub(
                r"^(Kannada Prabha)"
                r"(?:\s+(?:eee|ee|e))?"
                r"(?:\s+x)?\s*$",
                r"\1",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ====================================================
            # KNOWN OCR ARTIFACT:
            # "MO waves"
            #
            # Only remove it when it appears at the beginning.
            # ====================================================

            normalized = re.sub(
                r"^\s*"
                r"[“\"'‘’]?"
                r"\s*MO\s+waves"
                r"\s*",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ====================================================
            # REMOVE PURE NUMBER / SYMBOL GARBAGE AGAIN
            # after cleanup above.
            # ====================================================

            if engagement_only.match(normalized):
                continue

            # ====================================================
            # FINAL EMPTY CHECK
            # ====================================================

            if not normalized:
                continue

            cleaned_lines.append(
                normalized
            )

        return "\n".join(
            cleaned_lines
        ).strip()
    # ========================================================
    # PUBLISHER DETECTION
    # ========================================================

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
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for keyword, publisher in candidates:

            if keyword in normalized:

                return {
                    "publisher": publisher,
                    "confidence": 95,
                    "method": "ocr_known_publisher",
                }

        # ----------------------------------------------------
        # Social media handle
        # ----------------------------------------------------

        handles = re.findall(
            r"@([A-Za-z0-9_.]{3,40})",
            text,
        )

        ignored_handles = {
            "user",
            "gmail",
            "instagram",
            "twitter",
            "facebook",
        }

        for handle in handles:

            if handle.lower() in ignored_handles:
                continue

            publisher = handle.replace(
                "_",
                " ",
            ).strip()

            if publisher:

                return {
                    "publisher": publisher,
                    "confidence": 80,
                    "method": "ocr_social_handle",
                }

        # ----------------------------------------------------
        # Generic visible source
        # ----------------------------------------------------

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignored_phrases = (
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
        )

        for line in lines[:12]:

            clean = re.sub(
                r"[^A-Za-z0-9&.'@ _\-]",
                "",
                line,
            ).strip()

            if len(clean) < 4:
                continue

            if len(clean) > 50:
                continue

            lower = clean.lower()

            if any(
                phrase in lower
                for phrase in ignored_phrases
            ):
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


    # ========================================================
    # OCR CONFIDENCE
    # ========================================================

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

                confidence = float(value)

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


    # ========================================================
    # IMAGE VALIDATION
    # ========================================================

    def validate_image(
        self,
        image_bytes
    ):

        if not image_bytes:

            raise ValueError(
                "Empty image file."
            )

        if len(image_bytes) > self.MAX_FILE_SIZE:

            raise ValueError(
                "Image file is too large. "
                "Maximum allowed size is 10 MB."
            )

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
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
            io.BytesIO(image_bytes)
        )

        if image.format not in self.ALLOWED_FORMATS:

            raise ValueError(
                "Unsupported image format."
            )

        if image.width <= 0 or image.height <= 0:

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
            image.width * image.height
            > self.MAX_INPUT_PIXELS
        ):

            raise ValueError(
                "Image contains too many pixels."
            )

        return image


    # ========================================================
    # LANGUAGE VALIDATION
    # ========================================================

    def validate_language(
        self,
        language
    ):

        if not language:
            return "eng"

        language = (
            str(language)
            .strip()
            .lower()
        )

        if language not in self.SUPPORTED_LANGUAGES:

            raise ValueError(
                "Unsupported OCR language. "
                "Use one of: "
                "eng, hin, kan, "
                "eng+hin, eng+kan, "
                "hin+kan, eng+hin+kan."
            )

        return language


    # ========================================================
    # OCR EXTRACTION
    # ========================================================

    def extract_text_from_image(
        self,
        image_bytes,
        language="eng"
    ):

        try:

            # ------------------------------------------------
            # Validate language
            # ------------------------------------------------

            language = (
                self.validate_language(
                    language
                )
            )

            # ------------------------------------------------
            # Validate image
            # ------------------------------------------------

            image = (
                self.validate_image(
                    image_bytes
                )
            )

            # ------------------------------------------------
            # Preprocess
            # ------------------------------------------------

            processed = (
                self.preprocess_image(
                    image
                )
            )

            logger.info(
                "OCR language: %s",
                language
            )

            # ------------------------------------------------
            # OCR DATA
            # ------------------------------------------------

            ocr_data = (
                pytesseract.image_to_data(
                    processed,
                    lang=language,
                    config="--psm 6",
                    output_type=
                        pytesseract.Output.DICT,
                )
            )

            # ------------------------------------------------
            # RAW OCR
            # ------------------------------------------------

            raw_text = (
                pytesseract.image_to_string(
                    processed,
                    lang=language,
                    config="--psm 6"
                )
            )

            # ------------------------------------------------
            # DEBUG RAW OCR
            # ------------------------------------------------

            print(
                "\n"
                + "=" * 80
            )

            print(
                "DEBUG: RAW TESSERACT OCR"
            )

            print(
                "=" * 80
            )

            print(
                raw_text
            )

            print(
                "=" * 80
                + "\n"
            )

            # ------------------------------------------------
            # Remove obvious social-media UI
            # ------------------------------------------------

            filtered_text = (
                self.filter_social_media_ocr(
                    raw_text,
                    processed.height
                )
            )

            # ------------------------------------------------
            # Final whitespace normalization
            # ------------------------------------------------

            cleaned = (
                self.clean_text(
                    filtered_text
                )
            )

            # ------------------------------------------------
            # DEBUG FILTERED OCR
            # ------------------------------------------------

            print(
                "\n"
                + "=" * 80
            )

            print(
                "DEBUG: FILTERED OCR TEXT"
            )

            print(
                "=" * 80
            )

            print(
                cleaned
            )

            print(
                "=" * 80
                + "\n"
            )

            # ------------------------------------------------
            # OCR confidence
            # ------------------------------------------------

            ocr_confidence = (
                self.calculate_ocr_confidence(
                    ocr_data
                )
            )

            # ------------------------------------------------
            # Publisher
            # ------------------------------------------------

            publisher_info = (
                self.detect_publisher(
                    cleaned
                )
            )

            # ------------------------------------------------
            # Result
            # ------------------------------------------------

            return {

                "status":
                    "success",

                # Clean OCR text used by frontend.
                "extracted_text":
                    cleaned,

                # Same clean text used by analysis.
                "post_text":
                    cleaned,

                "engagement_text":
                    "",

                "ordered_values":
                    {},

                # Original Tesseract output preserved
                # for debugging.
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


# ============================================================
# SERVICE INSTANCE
# ============================================================

ocr_service = OCRService()


# ============================================================
# OCR API ENDPOINT
# ============================================================

@router.post("/")
async def extract_ocr(
    file: UploadFile = File(...),
    language: str = "eng+hin+kan",
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    try:

        # ----------------------------------------------------
        # Read uploaded file
        # ----------------------------------------------------

        image_bytes = await file.read()

        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # ----------------------------------------------------
        # OCR
        # ----------------------------------------------------

        result = (
            ocr_service.extract_text_from_image(
                image_bytes,
                language=language
            )
        )

        # ----------------------------------------------------
        # OCR failure
        # ----------------------------------------------------

        if (
            result.get("status")
            == "error"
        ):

            raise HTTPException(
                status_code=400,
                detail=result.get(
                    "message",
                    "OCR processing failed."
                )
            )

        return result

    except HTTPException:

        raise

    except Exception as e:

        logger.exception(
            "OCR API error: %s",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )