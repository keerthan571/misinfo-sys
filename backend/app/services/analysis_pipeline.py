import io
import logging
import os
import time
import uuid

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

                logger.warning(
                    "ENGAGEMENT EXTRACTION TIME: %.2fs",
                    engagement_time
                )

                engagement_values.update(
                    opencv_engagement
                )

        # ---------------------------------------------------------
        # VISION / OCR TEXT SELECTION
        # ---------------------------------------------------------

        ocr_text = str(
            ocr_values.get(
                "extracted_text",
                ""
            )
        ).strip()

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

            extracted_text = ocr_text

            logger.info(
                "Using OCR extracted text; Vision fallback skipped."
            )

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

                    logger.warning(
                        "Could not parse OCR engagement value: "
                        "%s=%s",
                        key,
                        value
                    )

        # ---------------------------------------------------------
        # FINAL TEXT
        # ---------------------------------------------------------

        final_text = (
            input_text
            if input_text
            else extracted_text
        ).strip()

        # ---------------------------------------------------------
        # NLP
        # ---------------------------------------------------------
        nlp_start = time.perf_counter()
        detection = (
            nlp_service.analyze_text(
                final_text
            )
        )
        nlp_time = time.perf_counter() - nlp_start

        logger.warning(
            "NLP TIME: %.2fs",
            nlp_time
        )

        claim = detection.get(
            "claim",
            final_text
        )

        # ---------------------------------------------------------
        # FACT VERIFICATION
        # ---------------------------------------------------------

        fact_result = verify_claim(
            claim=claim,
            context=final_text,
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

            if (
                detection.get("status") == "success"
                and nlp_risk_score is not None
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

                logger.warning(
                    "SPREAD ANALYSIS TIME: %.2fs",
                    spread_time
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

                        logger.warning(
                            "GRAPH GENERATION TIME: %.2fs",
                            graph_time
                        )

            else:

                logger.warning(
                    "Skipping spread prediction because "
                    "NLP analysis did not provide a valid risk score."
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

        logger.warning(
            "DATABASE SAVE TIME: %.2fs",
            db_time
        )

        logger.warning(
            "Analysis completed successfully. "
            "analysis_id=%s platform=%s social_input=%s "
            "graph_generated=%s processing_time=%.2fs",
            analysis_id,
            platform,
            has_social_media_input,
            bool(graph),
            time.time() - start
        )

        return {
            "analysis":
                response
        }

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


analysis_pipeline = AnalysisPipeline()