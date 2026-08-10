import time
import uuid
import io
import os

from PIL import Image

import cv2
import numpy as np

from app.services.vision_engagement_detector import (
    vision_engagement_detector
)

from app.services.engagement_extractor import (
    engagement_extractor
)

from app.services.twitter_engagement_extractor import (
    twitter_engagement_extractor
)

from app.services.twitter_views_detector import (
    twitter_views_detector
)

from app.services.graph.graph_generator import (
    graph_generator
)

from app.services.nlp_service import (
    nlp_service
)

from app.services.fact_verification_service import (
    verify_claim
)

from app.services.spread_factor_service import (
    spread_factor_service
)

from app.services.prediction_service import (
    prediction_service
)

from app.database.mongodb import (
    analysis_collection
)


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

        if ocr_values is None:
            ocr_values = {}

        extracted_text = ""

        # =========================================================
        # INITIAL PUBLISHER
        # =========================================================
        #
        # OCR publisher is the initial source.
        # Vision/Gemini may override it later if it actually
        # detects a publisher.
        #
        publisher = (
            ocr_publisher
            or ocr_values.get(
                "publisher"
            )
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

        engagement_values = {
            "likes": 0,
            "comments": 0,
            "replies": 0,
            "reposts": 0,
            "shares": 0,
            "bookmarks": 0,
            "views": 0,
        }

        image_path = None

        # =========================================================
        # IMAGE PROCESSING
        # =========================================================

        if image:

            image_bytes = await image.read()

            upload_dir = "uploads"

            os.makedirs(
                upload_dir,
                exist_ok=True
            )

            filename = (
                f"{analysis_id}_"
                f"{os.path.basename(image.filename)}"
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

            pil_image = Image.open(
                io.BytesIO(
                    image_bytes
                )
            )

            pil_image.load()

            img = np.array(
                pil_image
            )

            img = cv2.cvtColor(
                img,
                cv2.COLOR_RGB2BGR
            )

            # =====================================================
            # TWITTER / X ENGAGEMENT
            # =====================================================

            if platform.lower() in [
                "twitter",
                "x"
            ]:

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
            # OTHER PLATFORM ENGAGEMENT
            # =====================================================

            else:

                opencv_engagement = (
                    engagement_extractor.analyze(
                        img
                    )
                )

                engagement_values.update(
                    opencv_engagement
                )

        # =========================================================
        # VISION ANALYSIS
        # =========================================================
        #
        # OCR is the primary source for uploaded screenshots.
        #
        # If OCR already supplied text, do NOT call Gemini Vision.
        # This prevents the analysis pipeline from getting stuck
        # when Gemini quota is unavailable.
        #
        # Gemini is only used as a fallback when:
        #   1. an image exists
        #   2. OCR/text did not provide usable text
        #
        # =========================================================

        ocr_text = str(
            ocr_values.get(
                "extracted_text",
                ""
            )
        ).strip()

        input_text = str(
            text or ""
        ).strip()

        ocr_has_publisher = bool(
            ocr_values.get(
                "publisher"
            )
        )

        if input_text:

            # Analyze.jsx sends OCR text through `text`.
            # Therefore this is already the best available text.

            extracted_text = input_text

            print(
                "VISION SKIPPED: OCR/input text already available."
            )

        elif ocr_text:

            extracted_text = ocr_text

            print(
                "VISION SKIPPED: OCR text already available."
            )

        elif image:

            # ---------------------------------------------------------
            # OCR failed to provide text.
            # Gemini can be attempted as a fallback.
            # ---------------------------------------------------------

            try:

                print(
                    "VISION FALLBACK: OCR text unavailable."
                )

                vision_result = (
                    vision_engagement_detector.analyze(
                        pil_image,
                        platform
                    )
                )

                extracted_text = (
                    vision_result.get(
                        "post_text",
                        ""
                    )
                )

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

                # Only use Vision publisher if OCR did not
                # already provide one.

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

            except Exception as e:

                print(
                    "VISION FALLBACK ERROR:",
                    e
                )

                # Never destroy OCR results because
                # Gemini failed.

                extracted_text = ""

        # =========================================================
        # OCR PUBLISHER FALLBACK
        # =========================================================

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

        # =========================================================
        # OCR ENGAGEMENT FALLBACK
        # =========================================================

        if ocr_values:

            for key, value in (
                ocr_values.items()
            ):

                # Ignore publisher metadata.
                if key not in engagement_values:
                    continue

                if engagement_values[key] == 0:

                    try:

                        clean = (
                            str(value)
                            .replace(
                                ",",
                                ""
                            )
                            .lower()
                        )

                        if "k" in clean:

                            number = (
                                float(
                                    clean.replace(
                                        "k",
                                        ""
                                    )
                                )
                                * 1000
                            )

                        elif "m" in clean:

                            number = (
                                float(
                                    clean.replace(
                                        "m",
                                        ""
                                    )
                                )
                                * 1000000
                            )

                        else:

                            number = int(
                                clean
                            )

                        engagement_values[
                            key
                        ] = int(
                            number
                        )

                    except Exception as e:

                        print(
                            "OCR VALUE ERROR:",
                            e
                        )

        # =========================================================
        # FINAL TEXT
        # =========================================================

        final_text = (
            text.strip()
            if text
            else extracted_text
        )

        # =========================================================
        # NLP
        # =========================================================

        detection = (
            nlp_service.analyze_text(
                final_text
            )
        )

        claim = detection.get(
            "claim",
            final_text
        )

        # =========================================================
        # FACT VERIFICATION
        # =========================================================

        fact_result = verify_claim(
            claim
        )

        # =========================================================
        # DEBUG
        # =========================================================

        print(
            "========== FINAL DEBUG =========="
        )

        print(
            "PLATFORM:",
            platform
        )

        print(
            "TEXT:",
            extracted_text
        )

        print(
            "PUBLISHER:",
            publisher
        )

        print(
            "PUBLISHER CONFIDENCE:",
            publisher_confidence
        )

        print(
            "PUBLISHER METHOD:",
            publisher_detection_method
        )

        print(
            "ENGAGEMENT:",
            engagement_values
        )

        print(
            "IMAGE PATH:",
            image_path
        )

        print(
            "================================="
        )

        # =========================================================
        # ENGAGEMENT
        # =========================================================

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
                        "label":
                            key.title(),
                        "value":
                            value
                    }
                )

        # =========================================================
        # INSTAGRAM FOLLOWERS
        # =========================================================

        if (
            platform.lower()
            == "instagram"
            and followers
        ):

            engagement[
                "followers"
            ] = followers

        # =========================================================
        # SPREAD ANALYSIS
        # =========================================================

        spread_analysis = (
            spread_factor_service.analyze(
                engagement,
                detection,
                platform
            )
        )

        # =========================================================
        # PREDICTION
        # =========================================================

        prediction = (
            prediction_service.predict_spread(
                {
                    **engagement,

                    "spread_score":
                        spread_analysis[
                            "metrics"
                        ][
                            "spread_score"
                        ],

                    "risk_score":
                        detection.get(
                            "risk_score",
                            0
                        ),

                    "emotion_score":
                        0,

                    "manipulation_score":
                        0
                }
            )
        )

        # =========================================================
        # GRAPH
        # =========================================================

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

        # =========================================================
        # FINAL RESULT
        # =========================================================

        final_result = {

            "label":
                fact_result.get(
                    "verdict",
                    "Insufficient Evidence"
                ),

            "confidence":
                self.convert_confidence(
                    fact_result.get(
                        "confidence",
                        "0%"
                    )
                ),

            "risk_level":
                prediction[
                    "data"
                ][
                    "risk_level"
                ],

            "summary":
                spread_analysis[
                    "summary"
                ]
        }

        # =========================================================
        # RESPONSE
        # =========================================================

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
                    bool(image),

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

            "spread_analysis":
                spread_analysis,

            "prediction":
                prediction[
                    "data"
                ],

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
                    True
            }
        }

        # =========================================================
        # SAVE TO MONGODB
        # =========================================================

        analysis_collection.insert_one(
            {
                **response,

                "email":
                    current_user.get(
                        "email"
                    ),

                "analysis_time":
                    time.strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
            }
        )

        return {
            "analysis":
                response
        }

    def convert_confidence(
        self,
        value
    ):

        if isinstance(
            value,
            (int, float)
        ):

            return value

        value = str(
            value
        ).lower()

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

        except:

            return 0


analysis_pipeline = AnalysisPipeline()