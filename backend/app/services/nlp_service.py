import json
import logging
import os
import re

import spacy
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

logger = logging.getLogger(__name__)


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)


# ============================================================
# GROQ CLIENT
# ============================================================

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)


# ============================================================
# SPACY NER MODEL
# ============================================================

nlp_model = spacy.load(
    "en_core_web_sm"
)


# ============================================================
# NLP SERVICE
# ============================================================

class NLPService:

    # ========================================================
    # ENTITY EXTRACTION
    # ========================================================

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
            # Do NOT put domain-specific terms such as
            # cricket teams, movie names, political parties, etc.
            # here.
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

                if not value:
                    continue

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

                # Ignore social-media handles
                if value.startswith("@"):
                    continue

                # Ignore entities that are purely numeric
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

    # ========================================================
    # JSON EXTRACTION
    # ========================================================

    @staticmethod
    def extract_json_response(output):

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
        # Entire response is JSON.
        try:

            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:
            pass

        # Fallback:
        # Extract JSON object if the model added
        # surrounding text.
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

    # ========================================================
    # NUMBER VALIDATION
    # ========================================================

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

    # ========================================================
    # TEXT ANALYSIS
    # ========================================================

    def analyze_text(self, text):

        text = (
            text or ""
        ).strip()

        # ----------------------------------------------------
        # Invalid input
        # ----------------------------------------------------

        if len(text) < 5:

            return {

                "status": "error",

                "claim": "Unknown",

                "claim_type": "Unknown",

                "prediction":
                    "Needs Verification",

                "confidence": None,

                "risk_score": None,

                "keywords": [],

                "entities": [],

                "language": "Unknown",

                "manipulation_signals": []

            }

        # ----------------------------------------------------
        # Groq configuration
        # ----------------------------------------------------

        if not GROQ_API_KEY:

            logger.error(
                "GROQ_API_KEY is not configured."
            )

            return {

                "status": "error",

                "claim": text[:200],

                "claim_type": "General",

                "prediction":
                    "Verification Unavailable",

                "confidence": None,

                "risk_score": None,

                "keywords": [],

                "entities":
                    self.extract_entities(text),

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

                "prediction":
                    "Verification Unavailable",

                "confidence": None,

                "risk_score": None,

                "keywords": [],

                "entities":
                    self.extract_entities(text),

                "language": "Unknown",

                "manipulation_signals": []

            }

        # ====================================================
        # PROMPT
        # ====================================================

        prompt = f"""
Analyze the following submitted social-media content.

TEXT:
{text[:2000]}

Your task is NLP analysis, NOT factual verification.

IMPORTANT:
Do NOT decide whether a factual claim is true or false.
Do NOT use your own world knowledge to determine whether
the claim is correct.
Current events may have changed after your training data.

The separate Fact Verification module will verify factual
claims using external evidence.

Your responsibilities are:

1. Extract the MAIN factual claim.
2. Classify the claim type.
3. Identify the language.
4. Extract important keywords.
5. Identify linguistic/manipulation signals that are
   actually present in the text.
6. Estimate linguistic/manipulation risk.

Claim types must be exactly one of:

Political
Financial
Health
Sports
Technology
Entertainment
General

Prediction must be:

"Needs Verification"

for factual claims because factual correctness is determined
by the separate evidence-based verification module.

For non-factual content such as opinions, emotions, jokes,
or subjective statements, prediction may be:

"Not a Factual Claim"

Risk score:
- 0 means no meaningful linguistic/manipulation risk detected.
- 100 means very strong linguistic/manipulation signals.
- This score MUST NOT represent factual truth.
- Do not increase risk merely because a claim is unusual,
  recent, future-dated, controversial, or unknown.
- Do not use your knowledge cutoff as evidence of misinformation.

Confidence:
- Represents confidence in this NLP analysis only.
- It is NOT the probability that the claim is true or false.

Manipulation signals may include things such as:
- sensational language
- excessive urgency
- fear appeal
- unsupported certainty
- fabricated authority
- emotionally manipulative wording
- conspiracy framing
- misleading calls to action

Only report a signal when there is textual evidence.

Return ONLY JSON.
"""

        # ====================================================
        # GROQ REQUEST
        # ====================================================

        try:

            response = (
                groq_client
                .chat
                .completions
                .create(

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

                                "additionalProperties":
                                    False

                            }

                        }

                    },

                    messages=[

                        {

                            "role": "system",

                            "content": (
                                "You are an expert NLP "
                                "analysis system. "
                                "You analyze linguistic "
                                "and manipulation signals. "
                                "You do not determine "
                                "whether factual claims "
                                "are true or false. "
                                "Return only structured "
                                "JSON."
                            )

                        },

                        {

                            "role": "user",

                            "content": prompt

                        }

                    ]

                )
            )

            # =================================================
            # MODEL OUTPUT
            # =================================================

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

            result = (
                self.extract_json_response(
                    output
                )
            )

            # =================================================
            # CLAIM
            # =================================================

            claim = str(
                result.get(
                    "claim",
                    "Unknown"
                )
            ).strip()

            if not claim:

                claim = "Unknown"

            # =================================================
            # CLAIM TYPE
            # =================================================

            allowed_claim_types = {

                "Political",
                "Financial",
                "Health",
                "Sports",
                "Technology",
                "Entertainment",
                "General"

            }

            claim_type = str(
                result.get(
                    "claim_type",
                    "General"
                )
            ).strip()

            if claim_type not in allowed_claim_types:

                claim_type = "General"

            # =================================================
            # PREDICTION
            # =================================================

            prediction = str(
                result.get(
                    "prediction",
                    "Needs Verification"
                )
            ).strip()

            # IMPORTANT:
            #
            # NLP must not independently declare a factual
            # claim true or false.
            #
            # The fact-verification service is responsible
            # for evidence-based factual classification.

            if prediction not in {
                "Not a Factual Claim",
                "Needs Verification"
            }:

                prediction = (
                    "Needs Verification"
                )

            # =================================================
            # CONFIDENCE
            # =================================================

            confidence = self.clamp_number(

                result.get(
                    "confidence"
                ),

                0,

                100,

                default=0

            )

            # =================================================
            # RISK SCORE
            # =================================================

            risk_score = self.clamp_number(

                result.get(
                    "risk_score"
                ),

                0,

                100,

                default=0

            )

            # Convert whole numbers to integers
            if confidence is not None:

                if confidence.is_integer():

                    confidence = int(
                        confidence
                    )

            if risk_score is not None:

                if risk_score.is_integer():

                    risk_score = int(
                        risk_score
                    )

            # =================================================
            # KEYWORDS
            # =================================================

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

            # =================================================
            # MANIPULATION SIGNALS
            # =================================================

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

                for signal in manipulation_signals

                if str(signal).strip()

            ][:10]

            # =================================================
            # ENTITIES
            # =================================================

            entities = (
                self.extract_entities(
                    text
                )
            )

            # =================================================
            # SUCCESS
            # =================================================

            return {

                "status": "success",

                "claim": claim,

                "claim_type": claim_type,

                "prediction": prediction,

                "confidence": confidence,

                "risk_score": risk_score,

                "language": str(
                    result.get(
                        "language",
                        "English"
                    )
                ).strip()
                or "English",

                "keywords": keywords,

                "entities": entities,

                "manipulation_signals":
                    manipulation_signals

            }

        # ====================================================
        # ERROR HANDLING
        # ====================================================

        except Exception:

            logger.exception(
                "NLP analysis failed."
            )

            # IMPORTANT:
            #
            # Never return:
            # risk_score = 0
            # confidence = 50
            #
            # when the model failed.
            #
            # None means the analysis was unavailable.

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


# ============================================================
# SERVICE INSTANCE
# ============================================================

nlp_service = NLPService()