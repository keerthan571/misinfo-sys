import json
import logging
import os
import re

import spacy
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

logger = logging.getLogger(__name__)


# -------------------------
# Environment Configuration
# -------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# -------------------------
# Groq Client
# -------------------------

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)


# -------------------------
# spaCy NER Model
# -------------------------

nlp_model = spacy.load("en_core_web_sm")


# -------------------------
# NLP Service
# -------------------------

class NLPService:

    # -------------------------
    # Entity Extraction
    # -------------------------

    def extract_entities(self, text):

        if not text:
            return []

        try:

            doc = nlp_model(text)

            entities = []

            entity_map = {

                "PERSON": "Person",
                "GPE": "Location",
                "LOC": "Location",
                "ORG": "Organization",
                "EVENT": "Event",
                "DATE": "Date",
                "MONEY": "Money",
                "PRODUCT": "Product"

            }

            seen = set()

            # Generic ignore list.
            # Avoid domain-specific terms such as cricket teams.
            ignored_words = {

                "the",
                "and",
                "or",
                "but",
                "this",
                "that",
                "these",
                "those",
                "today",
                "tomorrow",
                "yesterday",
                "new",
                "latest",
                "live",
                "news",
                "post",
                "update",
                "official",
                "breaking"

            }

            for ent in doc.ents:

                value = ent.text.strip()

                value_lower = value.lower()

                # Unsupported entity type
                if ent.label_ not in entity_map:
                    continue

                # Very short entities are usually noise
                if len(value) < 3:
                    continue

                # Generic noise terms
                if value_lower in ignored_words:
                    continue

                # Duplicate entity
                if value_lower in seen:
                    continue

                # Ignore handles
                if value.startswith("@"):
                    continue

                # Avoid entities that are purely numeric
                if value.isdigit():
                    continue

                entities.append(
                    {
                        "name": value,
                        "type": entity_map[ent.label_]
                    }
                )

                seen.add(value_lower)

            return entities[:10]

        except Exception:
            logger.exception(
                "NLP entity extraction failed."
            )

            return []

    # -------------------------
    # JSON Extraction
    # -------------------------

    def extract_json_response(self, output):

        if not output:
            raise ValueError(
                "Empty AI response."
            )

        cleaned = (
            output
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        # First attempt:
        # Entire response is JSON
        try:

            return json.loads(cleaned)

        except json.JSONDecodeError:
            pass

        # Fallback:
        # Extract JSON object from surrounding text
        match = re.search(
            r"\{[\s\S]*\}",
            cleaned
        )

        if not match:

            raise ValueError(
                "No JSON object found in AI response."
            )

        return json.loads(
            match.group(0)
        )

    # -------------------------
    # Value Validation
    # -------------------------

    @staticmethod
    def clamp_number(
        value,
        minimum,
        maximum,
        default=None
    ):

        try:

            number = float(value)

            return max(
                minimum,
                min(
                    maximum,
                    number
                )
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    # -------------------------
    # Text Analysis
    # -------------------------

    def analyze_text(self, text):

        text = (text or "").strip()

        # -------------------------
        # Invalid Input
        # -------------------------

        if len(text) < 5:

            return {

                "status": "error",

                "claim": "Unknown",

                "claim_type": "Unknown",

                "prediction": "Needs Verification",

                "confidence": None,

                "risk_score": None,

                "keywords": [],

                "entities": [],

                "language": "Unknown",

                "manipulation_signals": []

            }

        # -------------------------
        # Groq Configuration Check
        # -------------------------

        if not GROQ_API_KEY:

            logger.error(
                "GROQ_API_KEY is not configured."
            )

            return {

                "status": "error",

                "claim": text[:200],

                "claim_type": "General",

                "prediction": "Verification Unavailable",

                "confidence": None,

                "risk_score": None,

                "keywords": [],

                "entities": self.extract_entities(text),

                "language": "Unknown",

                "manipulation_signals": []

            }

        if not groq_client:

            logger.error(
                "Groq client could not be initialized."
            )

            return {

                "status": "error",

                "claim": text[:200],

                "claim_type": "General",

                "prediction": "Verification Unavailable",

                "confidence": None,

                "risk_score": None,

                "keywords": [],

                "entities": self.extract_entities(text),

                "language": "Unknown",

                "manipulation_signals": []

            }

        # -------------------------
        # Prompt
        # -------------------------

        prompt = f"""
Analyze the following social media content for misinformation risk.

TEXT:
{text[:2000]}

Extract the MAIN factual claim.

Ignore:
- opinions
- emotions
- jokes
- hashtags unless they are part of the factual claim
- irrelevant social media metadata

Classify the claim type as exactly one of:

Political
Financial
Health
Sports
Technology
Entertainment
General

Return an overall misinformation risk assessment.

Confidence must be between 0 and 100.

Risk score must be between 0 and 100.

Normal factual content should NOT automatically be classified as misinformation.

Identify concise manipulation signals only when there is evidence in the text.

Extract important keywords.

Identify the language of the submitted content.
"""

        # -------------------------
        # Groq Request
        # -------------------------

        try:

            response = groq_client.chat.completions.create(

                model=GROQ_MODEL,

                reasoning_effort="low",

                include_reasoning=False,

                max_completion_tokens=1000,

                response_format={

                    "type": "json_schema",

                    "json_schema": {

                        "name":
                        "nlp_misinformation_analysis",

                        "strict": True,

                        "schema": {

                            "type": "object",

                            "properties": {

                                "claim": {
                                    "type": "string"
                                },

                                "claim_type": {
                                    "type": "string",
                                    "enum": [
                                        "Political",
                                        "Financial",
                                        "Health",
                                        "Sports",
                                        "Technology",
                                        "Entertainment",
                                        "General"
                                    ]
                                },

                                "prediction": {
                                    "type": "string"
                                },

                                "confidence": {
                                    "type": "number"
                                },

                                "risk_score": {
                                    "type": "number"
                                },

                                "language": {
                                    "type": "string"
                                },

                                "keywords": {

                                    "type": "array",

                                    "items": {
                                        "type": "string"
                                    }

                                },

                                "manipulation_signals": {

                                    "type": "array",

                                    "items": {
                                        "type": "string"
                                    }

                                }

                            },

                            "required": [

                                "claim",
                                "claim_type",
                                "prediction",
                                "confidence",
                                "risk_score",
                                "language",
                                "keywords",
                                "manipulation_signals"

                            ],

                            "additionalProperties": False

                        }

                    }

                },

                messages=[

                    {

                        "role": "system",

                        "content": (
                            "You are an expert NLP "
                            "misinformation analysis system. "
                            "Return only the requested "
                            "structured output."
                        )

                    },

                    {

                        "role": "user",

                        "content": prompt

                    }

                ]

            )

            # -------------------------
            # Extract Model Response
            # -------------------------

            output = (
                response
                .choices[0]
                .message
                .content
            )

            if not output:

                raise ValueError(
                    "Groq returned an empty AI response."
                )

            result = self.extract_json_response(
                output
            )

            # -------------------------
            # Validate Prediction
            # -------------------------

            prediction = str(
                result.get(
                    "prediction",
                    "Needs Verification"
                )
            ).strip()

            if not prediction:

                prediction = "Needs Verification"

            # -------------------------
            # Validate Numbers
            # -------------------------

            confidence = self.clamp_number(
                result.get("confidence"),
                0,
                100,
                default=0
            )

            risk_score = self.clamp_number(
                result.get("risk_score"),
                0,
                100,
                default=0
            )

            # Convert confidence to integer
            # when it is mathematically whole.
            if confidence.is_integer():

                confidence = int(
                    confidence
                )

            if risk_score.is_integer():

                risk_score = int(
                    risk_score
                )

            # -------------------------
            # Keywords
            # -------------------------

            keywords = result.get(
                "keywords",
                []
            )

            if not isinstance(
                keywords,
                list
            ):

                keywords = []

            keywords = [

                str(keyword).strip()

                for keyword in keywords

                if str(keyword).strip()

            ][:15]

            # -------------------------
            # Manipulation Signals
            # -------------------------

            manipulation_signals = (
                result.get(
                    "manipulation_signals",
                    []
                )
            )

            if not isinstance(
                manipulation_signals,
                list
            ):

                manipulation_signals = []

            manipulation_signals = [

                str(signal).strip()

                for signal
                in manipulation_signals

                if str(signal).strip()

            ][:10]

            # -------------------------
            # Entities
            # -------------------------

            entities = self.extract_entities(
                text
            )

            # -------------------------
            # Successful Response
            # -------------------------

            return {

                "status": "success",

                "claim": result.get(
                    "claim",
                    "Unknown"
                ),

                "claim_type": result.get(
                    "claim_type",
                    "General"
                ),

                "prediction": prediction,

                "confidence": confidence,

                "risk_score": risk_score,

                "language": result.get(
                    "language",
                    "English"
                ),

                "keywords": keywords,

                "entities": entities,

                "manipulation_signals":
                    manipulation_signals

            }

        # -------------------------
        # AI / JSON / Runtime Error
        # -------------------------

        except Exception:

            logger.exception(
                "NLP analysis failed."
            )

            # IMPORTANT:
            # Never convert an AI failure into
            # risk_score = 0 or confidence = 50.
            #
            # None means:
            # "No valid AI analysis was available."

            return {

                "status": "error",

                "claim": text[:200],

                "claim_type": "General",

                "prediction":
                    "Verification Unavailable",

                "confidence": None,

                "risk_score": None,

                "language": "Unknown",

                "keywords": [],

                "entities":
                    self.extract_entities(text),

                "manipulation_signals": []

            }


# -------------------------
# Service Instance
# -------------------------

nlp_service = NLPService()