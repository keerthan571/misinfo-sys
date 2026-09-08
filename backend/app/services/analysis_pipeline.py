import io
import logging
import os
import re
import time
import uuid

from dotenv import load_dotenv
from groq import Groq

import cv2
import numpy as np
from PIL import Image

from app.database.mongodb import analysis_collection

from app.services.engagement_extractor import (
    engagement_extractor
)

from app.services.fact_verification_service import (
    verify_claim
)

from app.services.graph.graph_generator import (
    graph_generator
)

from app.services.nlp_service import (
    nlp_service
)
from app.services.ocr_service import (
    ocr_service
)
from app.services.prediction_service import (
    prediction_service
)

from app.services.spread_factor_service import (
    spread_factor_service
)

from app.services.twitter_engagement_extractor import (
    twitter_engagement_extractor
)

from app.services.twitter_views_detector import (
    twitter_views_detector
)

from app.services.vision_engagement_detector import (
    vision_engagement_detector
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)
print("🔥 ENV TRANSLATION_MODEL:", os.getenv("TRANSLATION_MODEL"), flush=True)
TRANSLATION_MODEL = os.getenv(
    "TRANSLATION_MODEL",
    "qwen/qwen3.8-27b"
)
print("🔥 FINAL TRANSLATION_MODEL:", TRANSLATION_MODEL, flush=True)
groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)
if groq_client:
    try:
        models = groq_client.models.list()

        print("\n" + "=" * 80)
        print("AVAILABLE GROQ MODELS")
        print("=" * 80)

        for model in models.data:
            print(model.id)

        print("=" * 80 + "\n")

    except Exception as e:
        print("FAILED TO LIST GROQ MODELS:", e)
logger = logging.getLogger(__name__)


class AnalysisPipeline:

    async def run(
        self,
        text="",
        image=None,
        platform="",
        current_user=None,
        followers=0,
        ocr_values=None,
        ocr_publisher=None,
        ocr_publisher_confidence=0,
        ocr_publisher_method=None,
    ):

        start = time.time()

        analysis_id = str(
            uuid.uuid4()
        )

        # ---------------------------------------------------------
        # Normalize inputs
        # ---------------------------------------------------------

        ocr_values = (
            ocr_values
            if isinstance(ocr_values, dict)
            else {}
        )

        input_text = str(
            text or ""
        ).strip()

        normalized_platform = str(
            platform or ""
        ).strip().lower()

        extracted_text = ""

        image_path = None

        # True only when an actual social-media screenshot
        # is available for engagement / propagation analysis.
        has_social_media_input = (
            image is not None
            and normalized_platform not in {
                "",
                "text",
                "general",
                "text / general",
            }
        )

        # ---------------------------------------------------------
        # Publisher initialization
        # ---------------------------------------------------------

        publisher = (
            ocr_publisher
            or ocr_values.get("publisher")
        )

        publisher_confidence = (
            ocr_publisher_confidence
            or ocr_values.get(
                "publisher_confidence",
                0
            )
            or 0
        )

        publisher_detection_method = (
            ocr_publisher_method
            or ocr_values.get(
                "publisher_detection_method"
            )
        )

        # ---------------------------------------------------------
        # Engagement defaults
        # ---------------------------------------------------------

        engagement_values = {
            "likes": 0,
            "comments": 0,
            "replies": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0,
            "views": 0,
        }

        # ---------------------------------------------------------
        # IMAGE PROCESSING
        # ---------------------------------------------------------

        if image:

            image_bytes = await image.read()

            upload_dir = "uploads"

            os.makedirs(
                upload_dir,
                exist_ok=True
            )

            original_filename = (
                os.path.basename(
                    image.filename or "uploaded_image"
                )
            )

            filename = (
                f"{analysis_id}_"
                f"{original_filename}"
            )

            image_path = os.path.join(
                upload_dir,
                filename
            )

            with open(
                image_path,
                "wb"
            ) as file:

                file.write(
                    image_bytes
                )

            # Load image for engagement / Vision processing.
            pil_image = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

            pil_image.load()

            img = np.array(
                pil_image
            )

            # Handle images that contain an alpha channel.
            if len(img.shape) == 3 and img.shape[2] == 4:

                img = cv2.cvtColor(
                    img,
                    cv2.COLOR_RGBA2BGR
                )

            else:

                img = cv2.cvtColor(
                    img,
                    cv2.COLOR_RGB2BGR
                )

            # =====================================================
            # TWITTER / X ENGAGEMENT
            # =====================================================

            if normalized_platform in {
                "twitter",
                "x"
            }:

                twitter_engagement = (
                    twitter_engagement_extractor.analyze(
                        img
                    )
                )

                twitter_views = (
                    twitter_views_detector.detect(
                        img
                    )
                )

                twitter_engagement[
                    "views"
                ] = twitter_views

                engagement_values.update(
                    twitter_engagement
                )

            # =====================================================
            # OTHER SOCIAL-MEDIA PLATFORMS
            # =====================================================

            else:
    
                engagement_start = time.perf_counter()

                opencv_engagement = (
                    engagement_extractor.analyze(
                        img,
                        platform=platform
                    )
                )

                engagement_time = (
                    time.perf_counter()
                    - engagement_start
                )

                print(
                    f"ENGAGEMENT EXTRACTION TIME: {engagement_time:.2f}s",
                    flush=True
                )

                engagement_values.update(
                    opencv_engagement
                )

        ocr_text = str(
            ocr_values.get(
                "post_text",
                ""
            )
        ).strip()
        print("\n" + "=" * 80, flush=True)
        print("DEBUG: OCR VALUES ENTERING ANALYSIS PIPELINE", flush=True)
        print("=" * 80, flush=True)
        print("POST_TEXT:", repr(ocr_values.get("post_text")), flush=True)
        print("EXTRACTED_TEXT:", repr(ocr_values.get("extracted_text")), flush=True)
        print("RAW_TEXT:", repr(ocr_values.get("raw_text")), flush=True)
        print("=" * 80 + "\n", flush=True)

        # IMPORTANT:
        # Use raw_text from OCR as the source for NLP.
        #
        # raw_text is the original selected Tesseract OCR output.
        # Do NOT use post_text here because post_text may contain
        # coordinate-based processing that can damage OCR characters.
        #
        # Only whitespace normalization should happen before NLP.

        if ocr_text:
            logger.info(
                "Using cleaned OCR post_text for NLP."
            )
        else:
            logger.info(
                "No cleaned OCR post_text available."
            )

        vision_fallback_used = False

        # ---------------------------------------------------------
        # Determine analysis text
        # ---------------------------------------------------------

        if input_text:

            extracted_text = input_text

            logger.info(
                "Using supplied input text; Vision fallback skipped."
            )

        elif ocr_text:
            final_text = ocr_text.strip()

        elif image:

            # -----------------------------------------------------
            # OCR did not provide usable text.
            # Vision is only a fallback.
            # -----------------------------------------------------

            try:

                logger.info(
                    "OCR text unavailable. Attempting Vision fallback."
                )

                vision_result = (
                    vision_engagement_detector.analyze(
                        pil_image,
                        platform
                    )
                )

                vision_fallback_used = True

                extracted_text = str(
                    vision_result.get(
                        "post_text",
                        ""
                    )
                ).strip()

                vision_publisher = (
                    vision_result.get(
                        "publisher"
                    )
                )

                vision_publisher_confidence = (
                    vision_result.get(
                        "publisher_confidence",
                        0
                    )
                )

                vision_publisher_method = (
                    vision_result.get(
                        "publisher_detection_method"
                    )
                )

                # Vision publisher is only a fallback.
                # Never overwrite an existing OCR publisher.

                if (
                    vision_publisher
                    and not publisher
                ):

                    publisher = (
                        vision_publisher
                    )

                    publisher_confidence = (
                        vision_publisher_confidence
                    )

                    publisher_detection_method = (
                        vision_publisher_method
                    )

            except Exception:

                logger.exception(
                    "VISION FALLBACK ERROR"
                )

                extracted_text = ""

        # ---------------------------------------------------------
        # Publisher fallback
        # ---------------------------------------------------------

        if not publisher:

            ocr_detected_publisher = (
                ocr_values.get(
                    "publisher"
                )
            )

            if ocr_detected_publisher:

                publisher = (
                    ocr_detected_publisher
                )

                publisher_confidence = (
                    ocr_values.get(
                        "publisher_confidence",
                        0
                    )
                )

                publisher_detection_method = (
                    ocr_values.get(
                        "publisher_detection_method"
                    )
                )

        # ---------------------------------------------------------
        # OCR engagement fallback
        # ---------------------------------------------------------

        if ocr_values:

            for key, value in (
                ocr_values.items()
            ):

                if key not in engagement_values:
                    continue

                # Only use OCR value when the primary
                # engagement detector did not find a value.
                if engagement_values[key] != 0:
                    continue

                try:

                    clean = (
                        str(value)
                        .replace(",", "")
                        .strip()
                        .lower()
                    )

                    if not clean:
                        continue

                    if clean.endswith("k"):

                        number = (
                            float(
                                clean[:-1]
                            )
                            * 1000
                        )

                    elif clean.endswith("m"):

                        number = (
                            float(
                                clean[:-1]
                            )
                            * 1000000
                        )

                    else:

                        number = int(
                            float(clean)
                        )

                    engagement_values[key] = int(
                        number
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    print(
                        f"Could not parse OCR engagement value: {key}={value}",
                        flush=True
                    )

        # =========================================================
        # FINAL TEXT / NLP BOUNDARY
        # =========================================================

        if input_text:
    
            # Manual text input — use exactly what the user entered.
            final_text = input_text.strip()

        elif ocr_values.get("post_text"):
    
            final_text = str(
                ocr_values.get("post_text", "")
            ).strip()

        elif ocr_text:

            # Compatibility fallback for older OCR responses.
            final_text = ocr_text.strip()

        else:

            final_text = extracted_text.strip()


        print(
            "\n" + "=" * 80,
            flush=True
        )

        print(
            "DEBUG: FINAL TEXT ENTERING TRANSLATION",
            flush=True
        )

        print(
            "=" * 80,
            flush=True
        )

        print(
            final_text,
            flush=True
        )

        print(
            "=" * 80 + "\n",
            flush=True
        )


        cleaned_nlp_text = final_text

        original_language = (
            ocr_service.detect_text_language(
                cleaned_nlp_text
            )
        )

        print(
            "DEBUG: ORIGINAL POST LANGUAGE:",
            original_language,
            flush=True
        )
        print("\n" + "=" * 80, flush=True)
        print("DEBUG: OCR TEXT RECEIVED BY ANALYSIS PIPELINE", flush=True)
        print("=" * 80, flush=True)
        print(ocr_text, flush=True)
        print("=" * 80 + "\n", flush=True)


        # =========================================================
        # FINAL NLP TEXT
        # =========================================================

        # =========================================================
        # RAW OCR TEXT -> TRANSLATION
        # =========================================================
        #
        # IMPORTANT:
        # Do NOT pass OCR text through prepare_text_for_nlp().
        #
        # prepare_text_for_nlp() may remove/filter/alter OCR content.
        #
        # The OCR text should reach translation exactly as received,
        # except for the whitespace normalization already performed
        # by OCR service.
        # =========================================================

        cleaned_nlp_text = final_text

        print("\n" + "=" * 80, flush=True)
        print("DEBUG: RAW OCR TEXT BEFORE TRANSLATION", flush=True)
        print("=" * 80, flush=True)
        print(cleaned_nlp_text, flush=True)
        print("=" * 80 + "\n", flush=True)


        # =========================================================
        # TRANSLATION
        # =========================================================
        #
        # OCR text may be Kannada / Hindi / another Indic language.
        # NLP and spaCy entity extraction currently work primarily
        # with English text.
        #
        # Therefore:
        #
        #     Clean OCR
        #         ↓
        #     Translation
        #         ↓
        #     English NLP
        #
        # Engagement is completely untouched.
        # =========================================================

        translation_start = time.perf_counter()

        nlp_text = self.translate_to_english(
            cleaned_nlp_text
        )

        translation_time = (
            time.perf_counter()
            - translation_start
        )

        print("\n" + "=" * 80, flush=True)
        print("DEBUG: FINAL NLP TEXT AFTER TRANSLATION", flush=True)
        print("=" * 80, flush=True)
        print(nlp_text, flush=True)
        print("=" * 80 + "\n", flush=True)

        logger.info(
            "NLP INPUT TEXT AFTER TRANSLATION: %s",
            nlp_text
        )

        print("\n" + "=" * 80, flush=True)
        print("DEBUG: FINAL NLP TEXT", flush=True)
        print("=" * 80, flush=True)
        print(nlp_text, flush=True)
        print("=" * 80 + "\n", flush=True)
                

        print("\n" + "=" * 80, flush=True)
        print("DEBUG: FINAL NLP TEXT", flush=True)
        print("=" * 80, flush=True)
        print(nlp_text, flush=True)
        print("=" * 80 + "\n", flush=True)
        logger.info(
            "NLP INPUT TEXT: %s",
            nlp_text
        )
        # ---------------------------------------------------------
        # NLP
        # ---------------------------------------------------------
        nlp_start = time.perf_counter()
        detection = (
            nlp_service.analyze_text(
                nlp_text
            )
        )
        nlp_time = time.perf_counter() - nlp_start

        # =========================================================
        # PRESERVE ORIGINAL POST LANGUAGE
        # =========================================================
        #
        # NLP receives English translated text, so its own
        # language field may become "English".
        #
        # The UI must show the language of the ORIGINAL POST,
        # not the language used internally for NLP.
        #
        # OCR service already detected the original language.
        # =========================================================

        if (
            detection.get("status") == "success"
            and original_language
            and original_language != "Unknown"
        ):
            detection["language"] = original_language

        print(
            "DEBUG: FINAL DISPLAY LANGUAGE:",
            detection.get("language"),
            flush=True
        )
        print(
            f"NLP TIME: {nlp_time:.2f}s",
            flush=True
        )

        claim = str(
            detection.get(
                "claim",
                ""
            )
        ).strip()

        if (
            not claim
            or claim.lower() in {
                "unknown",
                "n/a",
                "none",
                "null",
            }
        ):

            fact_result = {
                "status": "error",
                "claim": "",
                "verdict": "Verification Unavailable",
                "reason": (
                    "NLP could not extract a valid factual claim "
                    "from the submitted content."
                ),
                "confidence": None,
                "sources": [],
            }

        else:

            fact_result = verify_claim(
                claim=claim,
                context=nlp_text,
                publisher=publisher,
                platform=platform,
            )

        # ---------------------------------------------------------
        # ENGAGEMENT OBJECT
        # ---------------------------------------------------------

        engagement = {
            **engagement_values,
            "metrics": []
        }

        for key, value in (
            engagement_values.items()
        ):

            if (
                value is not None
                and value > 0
            ):

                engagement[
                    "metrics"
                ].append(
                    {
                        "label": key.title(),
                        "value": value
                    }
                )

        # ---------------------------------------------------------
        # INSTAGRAM FOLLOWERS
        # ---------------------------------------------------------

        if (
            normalized_platform == "instagram"
            and followers
        ):

            engagement[
                "followers"
            ] = followers

        # ---------------------------------------------------------
        # SPREAD / PREDICTION / GRAPH
        # ---------------------------------------------------------
        #
        # IMPORTANT:
        #
        # These components require social-media evidence.
        #
        # Text-only analysis:
        #
        #   NLP
        #      ↓
        #   Fact Verification
        #
        # No engagement
        # No spread prediction
        # No propagation graph
        #
        # Screenshot analysis:
        #
        #   OCR
        #      ↓
        #   Engagement
        #      ↓
        #   NLP
        #      ↓
        #   Fact Verification
        #      ↓
        #   Spread Prediction
        #      ↓
        #   Graph
        #
        # ---------------------------------------------------------

        spread_analysis = None
        prediction = None
        graph = None

        if has_social_media_input:

            # Do not continue into numerical spread analysis
            # if NLP analysis failed to produce a valid risk score.

            nlp_risk_score = detection.get(
                "risk_score"
            )
            valid_nlp_claim = bool(
                claim
                and claim.lower() not in {
                    "unknown",
                    "n/a",
                    "none",
                    "null",
                }
            )
            if (
                detection.get("status") == "success"
                and nlp_risk_score is not None
                and claim
            ):
                spread_start = time.perf_counter()
                spread_analysis = (
                    spread_factor_service.analyze(
                        engagement,
                        detection,
                        platform
                    )
                )
                spread_time = time.perf_counter() - spread_start

                print(
                    f"SPREAD ANALYSIS TIME: {spread_time:.2f}s",
                    flush=True
                )

                spread_score = (
                    spread_analysis
                    .get("metrics", {})
                    .get("spread_score")
                )

                if spread_score is not None:

                    prediction_input = {
                        **engagement,

                        "spread_score":
                            spread_score,

                        "risk_score":
                            nlp_risk_score,

                        "emotion_score":
                            0,

                        "manipulation_score":
                            0
                    }

                    prediction = (
                        prediction_service.predict_spread(
                            prediction_input
                        )
                    )

                    # Only generate the graph after
                    # a valid spread prediction exists.

                    if prediction and prediction.get("data"):
                        graph_start = time.perf_counter()
                        graph = (
                            graph_generator.generate(
                                {
                                    "analysis": {

                                        "text":
                                            final_text,

                                        "platform":
                                            platform,

                                        "publisher":
                                            publisher,

                                        "publisher_confidence":
                                            publisher_confidence

                                    },

                                    "engagement":
                                        engagement,

                                    "spread_prediction":
                                        prediction[
                                            "data"
                                        ]
                                }
                            )
                        )
                        graph_time = time.perf_counter() - graph_start

                        print(
                            f"GRAPH GENERATION TIME: {graph_time:.2f}s",
                            flush=True
                        )

            else:

                print(
                    "Skipping spread prediction because "
                    "NLP analysis did not provide a valid risk score.",
                    flush=True
                )

        else:

            logger.info(
                "Text-only analysis: "
                "spread prediction and propagation graph skipped."
            )

        # ---------------------------------------------------------
        # FINAL RESULT
        # ---------------------------------------------------------

        fact_confidence = (
            fact_result.get(
                "confidence"
            )
        )

        final_result = {

            "label":
                fact_result.get(
                    "verdict",
                    "Insufficient Evidence"
                ),

            "confidence":
                self.convert_confidence(
                    fact_confidence
                ),

            "risk_level":
                (
                    prediction.get(
                        "data",
                        {}
                    ).get(
                        "risk_level"
                    )
                    if prediction
                    else None
                ),

            "summary":
                (
                    spread_analysis.get(
                        "summary"
                    )
                    if spread_analysis
                    else (
                        "Spread analysis is not available "
                        "because social-media engagement data "
                        "was not provided."
                    )
                )
        }

        # ---------------------------------------------------------
        # RESPONSE
        # ---------------------------------------------------------

        response = {

            "analysis_id":
                analysis_id,

            "text":
                final_text,

            "platform": {
                "platform":
                    platform
            },

            "publisher":
                publisher,

            "publisher_confidence":
                publisher_confidence,

            "publisher_detection_method":
                publisher_detection_method,

            "image": (
                {
                    "path":
                        image_path.replace(
                            "\\",
                            "/"
                        )
                }
                if image_path
                else None
            ),

            "vision": {

                "used":
                    vision_fallback_used,

                "ocr_used":
                    bool(ocr_text),

                "post_text":
                    extracted_text,

                "engagement_values":
                    engagement_values,

                "publisher":
                    publisher,

                "publisher_confidence":
                    publisher_confidence,

                "publisher_detection_method":
                    publisher_detection_method
            },

            "detection":
                detection,

            "fact_verification":
                fact_result,

            "engagement":
                engagement,

            # None means the analysis was not applicable,
            # not that the calculated score was zero.
            "spread_analysis":
                spread_analysis,

            "prediction":
                (
                    prediction.get("data")
                    if prediction
                    else None
                ),

            "graph":
                graph,

            "final_result":
                final_result,

            "metadata": {

                "analysis_id":
                    analysis_id,

                "processing_status":
                    "completed",

                "processing_time":
                    round(
                        time.time()
                        - start,
                        2
                    ),

                "graph_generated_once":
                    bool(graph)

            }
        }

        # ---------------------------------------------------------
        # DATABASE
        # ---------------------------------------------------------

        user_email = (
            current_user.get("email")
            if current_user
            else None
        )
        
        db_start = time.perf_counter()
        analysis_collection.insert_one(
            {
                **response,

                "email":
                    user_email,

                "analysis_time":
                    time.strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
            }
        )
        db_time = time.perf_counter() - db_start

        print(
            f"DATABASE SAVE TIME: {db_time:.2f}s",
            flush=True
        )

        print(
            "Analysis completed successfully. "
            f"analysis_id={analysis_id} "
            f"platform={platform} "
            f"social_input={has_social_media_input} "
            f"graph_generated={bool(graph)} "
            f"processing_time={time.time() - start:.2f}s",
            flush=True
        )

        return {
            "analysis":
                response
        }

    # ---------------------------------------------------------
    # TRANSLATE CLEANED POST TEXT TO ENGLISH
    # ---------------------------------------------------------

    @staticmethod
    def translate_to_english(text):
    
        print(
            "🔥🔥🔥 TRANSLATION STARTED 🔥🔥🔥",
            flush=True
        )

        if not text:
            return ""

        text = str(text).strip()

        if not text:
            return ""

        # ---------------------------------------------------------
        # Detect Indic scripts
        # ---------------------------------------------------------

        has_indic_script = bool(
            re.search(
                r"[\u0900-\u0DFF]",
                text
            )
        )

        # Already English / Latin text
        if not has_indic_script:

            logger.info(
                "Translation skipped: text appears to be English."
            )

            return text

        # ---------------------------------------------------------
        # Check Groq client
        # ---------------------------------------------------------

        if not groq_client:

            logger.error(
                "TRANSLATION FAILED: Groq client is not initialized."
            )

            return text

        translation_start = time.perf_counter()

        try:

            print(
                f"🔥 TRANSLATION MODEL: {TRANSLATION_MODEL}",
                flush=True
            )

            response = groq_client.chat.completions.create(

                model=TRANSLATION_MODEL,

                temperature=0,

                # IMPORTANT:
                # Qwen 3.6 supports reasoning_effort="none".
                # This prevents reasoning from consuming the
                # entire completion budget.
                reasoning_effort="none",

                max_completion_tokens=600,

                messages=[

                    {
                        "role": "system",

                        "content": (
                            "Translate the user's OCR text into English.\n\n"

                            "The OCR may contain Kannada, Hindi, English, "
                            "mixed languages, OCR spacing errors, character "
                            "recognition errors, and social-media interface text.\n\n"

                            "Instructions:\n"

                            "1. Translate readable Kannada or Hindi into English.\n"

                            "2. Preserve proper names, people, organizations, "
                            "abbreviations, numbers, dates and factual statements.\n"

                            "3. Preserve the meaning of the original text exactly.\n"

                            "4. Do NOT invent, expand, reinterpret or guess "
                            "abbreviations, names or OCR-corrupted words.\n"

                            "5. If an abbreviation or name is ambiguous, preserve "
                            "the original Latin form instead of guessing its meaning.\n"

                            "6. Do not convert an unclear OCR word into a different "
                            "word merely because it seems more likely from context.\n"

                            "7. Preserve questions as questions.\n"

                            "8. Ignore obvious social-media UI text such as "
                            "More, See translation, Like, Comment, Share, "
                            "Follow and Show translation.\n"

                            "9. Fix only obvious OCR spacing errors when the "
                            "intended word is unambiguous.\n"

                            "10. If a portion is genuinely unreadable, omit only "
                            "that portion rather than inventing content.\n"

                            "11. Do not explain your reasoning.\n"

                            "12. Do not describe OCR quality.\n"

                            "13. Do not summarize.\n"

                            "14. Return ONLY the English translation."
                        )
                    },

                    {
                        "role": "user",
                        "content": text
                    }

                ]
            )

            # ---------------------------------------------------------
            # DEBUG
            # ---------------------------------------------------------

            print(
                "\n" + "=" * 80,
                flush=True
            )

            print(
                "🔥 RAW GROQ TRANSLATION RESPONSE",
                flush=True
            )

            print(
                response,
                flush=True
            )

            print(
                "=" * 80,
                flush=True
            )

            choices = getattr(
                response,
                "choices",
                None
            )

            if not choices:

                logger.error(
                    "TRANSLATION FAILED: Groq returned no choices."
                )

                return text

            message = getattr(
                choices[0],
                "message",
                None
            )

            if not message:

                logger.error(
                    "TRANSLATION FAILED: Groq message missing."
                )

                return text

            # ---------------------------------------------------------
            # ONLY use actual content
            # ---------------------------------------------------------

            translated = getattr(
                message,
                "content",
                None
            )

            if not translated and isinstance(
                message,
                dict
            ):

                translated = message.get(
                    "content"
                )

            translated = str(
                translated or ""
            ).strip()

            # ---------------------------------------------------------
            # Debug
            # ---------------------------------------------------------

            finish_reason = getattr(
                choices[0],
                "finish_reason",
                None
            )

            reasoning = getattr(
                message,
                "reasoning",
                None
            )

            print(
                f"🔥 TRANSLATION FINISH REASON: "
                f"{finish_reason}",
                flush=True
            )

            print(
                f"🔥 TRANSLATION CONTENT LENGTH: "
                f"{len(translated)}",
                flush=True
            )

            print(
                f"🔥 REASONING PRESENT: "
                f"{bool(reasoning)}",
                flush=True
            )

            # ---------------------------------------------------------
            # Empty translation
            # ---------------------------------------------------------

            if not translated:

                logger.error(
                    "TRANSLATION FAILED: Groq returned empty content."
                )

                return text

            # ---------------------------------------------------------
            # Success
            # ---------------------------------------------------------

            translation_time = (
                time.perf_counter()
                - translation_start
            )

            print(
                f"TRANSLATION TIME: "
                f"{translation_time:.2f}s",
                flush=True
            )

            print(
                "\n" + "=" * 80,
                flush=True
            )

            print(
                "🔥 TRANSLATION SUCCESS",
                flush=True
            )

            print(
                "=" * 80,
                flush=True
            )

            print(
                "BEFORE:",
                text,
                flush=True
            )

            print(
                "AFTER:",
                translated,
                flush=True
            )

            print(
                "=" * 80 + "\n",
                flush=True
            )

            return translated

        except Exception as e:

            logger.exception(
                "TRANSLATION ERROR: %s",
                e
            )

            return text
    # ---------------------------------------------------------
    # CONFIDENCE CONVERSION
    # ---------------------------------------------------------

    @staticmethod
    def convert_confidence(value):

        # None means confidence was unavailable.
        if value is None:
            return None

        if isinstance(
            value,
            (int, float)
        ):

            return value

        value = str(
            value
        ).lower().strip()

        if "high" in value:
            return 90

        if "medium" in value:
            return 70

        if "low" in value:
            return 40

        try:

            return float(
                value.replace(
                    "%",
                    ""
                )
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    @staticmethod
    def prepare_text_for_nlp(
        text,
        engagement_values=None
    ):
        """
        Prepare OCR text before NLP.

        Removes social-media UI / metadata while preserving
        legitimate claim content, including numbers and dates.

        IMPORTANT:
        Engagement extraction is NOT modified here.

        This function only controls what reaches NLP.
        """

        if not text:
            return ""

        text = str(
            text
        )

        engagement_values = (
            engagement_values
            if isinstance(
                engagement_values,
                dict
            )
            else {}
        )

        lines = text.splitlines()

        cleaned_lines = []

        # ---------------------------------------------------------
        # Obvious social-media UI labels
        # ---------------------------------------------------------

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
            "translate",
            "translation",
        }

        # ---------------------------------------------------------
        # Words which strongly indicate that a line is metadata
        # rather than post content.
        # ---------------------------------------------------------

        metadata_words = {
            "views",
            "view",
            "replies",
            "reply",
            "comments",
            "comment",
            "likes",
            "like",
            "reposts",
            "repost",
            "bookmarks",
            "bookmark",
        }

        # ---------------------------------------------------------
        # Convert engagement values into strings.
        #
        # Example:
        # 1500 -> "1500"
        # 1.5K is handled separately below.
        # ---------------------------------------------------------

        engagement_numbers = set()

        for value in engagement_values.values():

            if value in (
                None,
                "",
                0
            ):
                continue

            try:
                number = int(
                    float(value)
                )

                engagement_numbers.add(
                    str(number)
                )

            except (
                ValueError,
                TypeError
            ):
                continue

        # ---------------------------------------------------------
        # Helpers
        # ---------------------------------------------------------

        def normalize_line(line):
            return re.sub(
                r"\s+",
                " ",
                line
            ).strip()

        def is_time_only(line):

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
                    line,
                    flags=re.IGNORECASE |
                        re.VERBOSE
                )
            )

        def contains_metadata_word(line):

            lower = line.lower()

            words = set(
                re.findall(
                    r"[a-z]+",
                    lower
                )
            )

            return bool(
                words &
                metadata_words
            )

        def is_engagement_only(line):

            compact = (
                line
                .replace(",", "")
                .strip()
                .lower()
            )

            # Direct match.
            if compact in engagement_numbers:
                return True

            # Handle OCR output such as:
            #
            # 3 1
            # 12 5 2
            #
            # when every token corresponds to a detected
            # engagement number.
            tokens = compact.split()

            if (
                tokens
                and len(tokens) <= 8
            ):
                numeric_tokens = []

                for token in tokens:

                    token = (
                        token
                        .replace(".", "")
                    )

                    if token.isdigit():
                        numeric_tokens.append(
                            token
                        )

                if (
                    len(numeric_tokens)
                    == len(tokens)
                ):
                    if all(
                        token in engagement_numbers
                        for token in numeric_tokens
                    ):
                        return True

            return False

        def is_ui_only(line):

            lower = line.lower()

            # Exact UI label.
            if lower in ui_phrases:
                return True

            # A line made only from UI labels.
            tokens = lower.split()

            if tokens:

                normalized_tokens = {
                    token.strip(
                        ".,!?|:;·"
                    )
                    for token in tokens
                }

                if normalized_tokens and \
                normalized_tokens.issubset(
                    ui_phrases
                ):
                    return True

            return False

        # ---------------------------------------------------------
        # Process OCR lines
        # ---------------------------------------------------------

        for raw_line in lines:

            line = normalize_line(
                raw_line
            )

            if not line:
                continue

            # -----------------------------------------------------
            # 1. Obvious UI
            # -----------------------------------------------------

            if is_ui_only(line):
                continue

            # -----------------------------------------------------
            # 2. Timestamp-only line
            #
            # Example:
            # 3:00 pm
            # -----------------------------------------------------

            if is_time_only(line):
                continue

            # -----------------------------------------------------
            # 3. Metadata / engagement line
            #
            # Example:
            # Sep 26 · 1.9K Views
            #
            # We remove this because "Views" makes it clearly
            # social-media metadata rather than claim content.
            #
            # A date appearing inside an ordinary claim is NOT
            # removed.
            # -----------------------------------------------------

            if contains_metadata_word(line):
                continue

            # -----------------------------------------------------
            # 4. Standalone engagement numbers
            # -----------------------------------------------------

            if is_engagement_only(line):
                continue

            # -----------------------------------------------------
            # 5. Keep everything else
            # -----------------------------------------------------

            cleaned_lines.append(
                line
            )

        return "\n".join(
            cleaned_lines
        ).strip()
        
analysis_pipeline = AnalysisPipeline()