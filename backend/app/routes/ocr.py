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

# Windows:
# Use the locally installed Tesseract executable.
#
# Render/Linux:
# Do not set a Windows path.
# Tesseract will be resolved from PATH.
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
                    target_width * ratio
                )
            )

            target_height = max(
                1,
                int(
                    target_height * ratio
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

        # Keep Unicode characters so that
        # Hindi and Kannada text are NOT destroyed.

        text = re.sub(
            r"[^\w\s.,!?@#%:/\-]",
            " ",
            text,
            flags=re.UNICODE
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

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

        # =====================================================
        # KNOWN PUBLISHERS
        # =====================================================

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

                    "publisher":
                        publisher,

                    "confidence":
                        95,

                    "method":
                        "ocr_known_publisher",
                }

        # =====================================================
        # SOCIAL MEDIA HANDLE
        # =====================================================

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

            if (
                handle.lower()
                in ignored_handles
            ):
                continue

            publisher = handle.replace(
                "_",
                " ",
            ).strip()

            if publisher:

                return {

                    "publisher":
                        publisher,

                    "confidence":
                        80,

                    "method":
                        "ocr_social_handle",
                }

        # =====================================================
        # GENERIC VISIBLE SOURCE
        # =====================================================

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

                    "publisher":
                        clean,

                    "confidence":
                        65,

                    "method":
                        "ocr_visible_source",
                }

        # =====================================================
        # NOTHING RELIABLE FOUND
        # =====================================================

        return {

            "publisher":
                None,

            "confidence":
                0,

            "method":
                None,
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

        if (
            image.format
            not in self.ALLOWED_FORMATS
        ):

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
            image.width
            > self.MAX_DIMENSION
            or image.height
            > self.MAX_DIMENSION
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

        if (
            language
            not in self.SUPPORTED_LANGUAGES
        ):

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
            # OCR TEXT
            # ------------------------------------------------

            raw_text = (
                pytesseract.image_to_string(
                    processed,
                    lang=language,
                    config="--psm 6"
                )
            )

            # ------------------------------------------------
            # Clean text
            # ------------------------------------------------

            cleaned = (
                self.clean_text(
                    raw_text
                )
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
            # Return result
            # ------------------------------------------------

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
    language: str = "eng",
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