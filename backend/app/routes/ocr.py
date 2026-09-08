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
        image_height,
    ):
        """
        Universal social-media OCR cleaner.

        PURPOSE:
        Remove social-media UI/OCR noise while preserving
        actual post content in Kannada, Hindi, English, etc.

        IMPORTANT:
        - Does NOT translate.
        - Does NOT rewrite content.
        - Does NOT "correct" Indic OCR.
        - Does NOT remove ordinary numbers from sentences.
        - Engagement numbers are handled separately.
        """

        if not text:
            return ""

        lines = str(text).splitlines()

        cleaned_lines = []

        # ========================================================
        # EXACT SOCIAL MEDIA UI
        # ========================================================

        ui_exact = {
            "more",
            "see more",
            "see translation",
            "show translation",
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
            "view",
            "views",
            "translation",
            "translate",
            "seetranslation",
            "showtranslation",
            "seemore",
        }

        # ========================================================
        # UI PHRASES
        # ========================================================

        ui_phrase_patterns = [

            # Facebook
            r"\bsee\s+translation\b",
            r"\bsee\s+more\b",

            # Twitter / X
            r"\bshow\s+translation\b",
            r"\btranslate\s+post\b",
            r"\bview\s+translation\b",

            # Generic engagement labels
            r"\blikes?\b",
            r"\bcomments?\b",
            r"\breposts?\b",
            r"\breplies?\b",
            r"\bshares?\b",
            r"\bbookmarks?\b",
            r"\bviews?\b",
        ]

        # ========================================================
        # TIMESTAMPS
        # ========================================================

        timestamp_patterns = [

            # 3h
            r"^\d+\s*[smhdwy]$",

            # 3h-@
            r"^\d+\s*[smhdwy]\s*[-@·•]?$",

            # 3:00 pm
            r"^\d{1,2}:\d{2}\s*(?:am|pm)$",

            # 02 Sept 26
            r"^\d{1,2}\s+"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
            r"(?:\s+\d{2,4})?$",

            # 02 September 2026
            r"^\d{1,2}\s+"
            r"(?:January|February|March|April|May|June|July|August|"
            r"September|October|November|December)"
            r"(?:\s+\d{2,4})?$",
        ]

        compiled_timestamp_patterns = [
            re.compile(
                pattern,
                re.IGNORECASE
            )
            for pattern in timestamp_patterns
        ]

        # ========================================================
        # KNOWN OCR UI GARBAGE
        # ========================================================

        # Examples:
        # (J
        # ©}
        # > 
        # ©
        # []
        # icon fragments

        standalone_garbage_pattern = re.compile(
            r"^[\W_]+$",
            re.UNICODE
        )

        # ========================================================
        # PROCESS LINES
        # ========================================================

        for raw_line in lines:

            line = raw_line.strip()

            if not line:
                continue

            # ----------------------------------------------------
            # Normalize whitespace only
            # ----------------------------------------------------

            normalized = re.sub(
                r"\s+",
                " ",
                line
            ).strip()

            if not normalized:
                continue

            lower = normalized.lower()
            
            # ====================================================
            # SOCIAL-MEDIA TRANSLATION UI
            #
            # Handles OCR variations such as:
            #   Show translation
            #   Showtranslation
            #   See translation
            #   Seetranslation
            #
            # These are UI elements, never post content.
            # ====================================================

            translation_ui = re.sub(
                r"[\s]+",
                "",
                lower
            )

            if translation_ui in {
                "showtranslation",
                "seetranslation",
            }:
                continue

            # ----------------------------------------------------
            # 1. Exact UI
            # ----------------------------------------------------

            if lower in ui_exact:
                continue

            # ----------------------------------------------------
            # 2. Timestamp-only lines
            # ----------------------------------------------------

            if any(
                pattern.fullmatch(normalized)
                for pattern in compiled_timestamp_patterns
            ):
                continue

            # ----------------------------------------------------
            # 3. Pure punctuation / icon garbage
            # ----------------------------------------------------

            if standalone_garbage_pattern.fullmatch(
                normalized
            ):
                continue

            # ----------------------------------------------------
            # 4. Remove timestamp + metadata from END
            #
            # Example:
            #
            # 3:00 pm * 02 Sept 26 - 1.9K Views
            #
            # This entire line is metadata, not post text.
            # ----------------------------------------------------

            if re.search(
                r"\b\d{1,2}:\d{2}\s*(?:am|pm)\b",
                normalized,
                flags=re.IGNORECASE
            ):

                # If the line contains Views / engagement metadata,
                # it is almost certainly a social-media metadata line.

                if re.search(
                    r"\bviews?\b",
                    normalized,
                    flags=re.IGNORECASE
                ):
                    continue

            # ----------------------------------------------------
            # 5. Remove UI phrases at the END
            # ----------------------------------------------------

            normalized = re.sub(
                r"\s+(?:More|See\s+more|See\s+translation|"
                r"Show\s+translation)\s*$",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ----------------------------------------------------
            # 6. Remove UI phrases at BEGINNING
            # ----------------------------------------------------

            normalized = re.sub(
                r"^(?:Show\s+translation|See\s+translation|"
                r"See\s+more)\s+",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ----------------------------------------------------
            # 7. Remove standalone timestamp at BEGINNING
            #
            # Example:
            #
            # 3h-@ Kannada text
            #
            # -> Kannada text
            # ----------------------------------------------------

            normalized = re.sub(
                r"^\s*\d+\s*[smhdwy]"
                r"(?:\s*[-@·•])?\s+",
                "",
                normalized,
                flags=re.IGNORECASE
            ).strip()

            # ----------------------------------------------------
            # 8. Remove common OCR icon prefix
            # ----------------------------------------------------

            normalized = re.sub(
                r"^[\(\[\{<«“\"']?\s*[JjIiLlTt]\s*"
                r"(?:\)|\]|\}|>|»|”|\"|'|©|®|™)?\s+",
                "",
                normalized
            ).strip()

            # ----------------------------------------------------
            # 9. Remove obvious social-media metadata suffix
            #
            # IMPORTANT:
            # Only remove when the line is clearly metadata.
            #
            # Do NOT remove ordinary numbers from actual sentences.
            # ----------------------------------------------------

            metadata_suffix = re.compile(
                r"(?:"
                r"\d+(?:\.\d+)?[KMB]?\s*"
                r"(?:likes?|comments?|reposts?|replies?|"
                r"shares?|bookmarks?|views?)"
                r")"
                r"(?:\s+.*)?$",
                re.IGNORECASE
            )

            if metadata_suffix.search(normalized):

                # If line has substantial non-Latin / Indic text,
                # preserve the text and only remove the metadata tail.

                normalized = metadata_suffix.sub(
                    "",
                    normalized
                ).strip()

            # ====================================================
            # 10. Remove obvious social-media engagement UI line
            #
            # IMPORTANT:
            # This affects ONLY OCR post text.
            # It does NOT modify engagement extraction.
            #
            # Typical OCR:
            #   © 3 1, 17 9) 129 ಕ ०2
            #   3 17 129 1
            #   ♡ 129  💬 3  ↻ 17
            #
            # These lines belong to the bottom engagement/UI area,
            # not to the actual post.
            # ====================================================

            ui_symbol_count = len(
                re.findall(
                    r"[©®™○●◦•·|(){}\[\]<>]",
                    normalized,
                    flags=re.UNICODE
                )
            )

            ui_digit_count = len(
                re.findall(
                    r"[0-9೦-೯०-९]",
                    normalized,
                    flags=re.UNICODE
                )
            )

            ui_kannada_count = len(
                re.findall(
                    r"[\u0C80-\u0CFF]",
                    normalized
                )
            )

            ui_latin_count = len(
                re.findall(
                    r"[A-Za-z]",
                    normalized
                )
            )

            # Very short mixed OCR lines containing mostly numbers,
            # symbols and isolated script characters are usually
            # engagement/UI OCR rather than post content.
            if (
                len(normalized) <= 40
                and ui_digit_count >= 2
                and (
                    ui_symbol_count >= 1
                    or ui_kannada_count <= 2
                )
                and ui_latin_count <= 2
            ):
                continue
            # ----------------------------------------------------
            # 11. Remove obvious isolated OCR icon fragments
            # ----------------------------------------------------

            if len(normalized) <= 3:

                # Keep meaningful Indic words.
                meaningful_indic = re.search(
                    r"[\u0900-\u097F\u0C80-\u0CFF]",
                    normalized
                )

                meaningful_latin = re.fullmatch(
                    r"[A-Za-z]{2,3}",
                    normalized
                )

                if (
                    not meaningful_indic
                    and not meaningful_latin
                ):
                    continue

            # ----------------------------------------------------
            # 12. Remove leading OCR separator garbage
            # ----------------------------------------------------

            normalized = re.sub(
                r"^[.\\\/|•·\-_=]+\s*",
                "",
                normalized
            ).strip()

            # ----------------------------------------------------
            # 13. Remove trailing OCR separator garbage
            # ----------------------------------------------------

            normalized = re.sub(
                r"\s*[|•·_=]+$",
                "",
                normalized
            ).strip()

            # ----------------------------------------------------
            # 14. Final check
            # ----------------------------------------------------

            if not normalized:
                continue

            cleaned_lines.append(
                normalized
            )

        # ========================================================
        # FINAL CLEANUP
        # ========================================================

        result = "\n".join(
            cleaned_lines
        ).strip()

        return result
    
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