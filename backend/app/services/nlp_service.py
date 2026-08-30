import json
import logging
import os
import re

import spacy
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

nlp_model = spacy.load("en_core_web_sm")


class NLPService:

    def extract_entities(self, text):
        if not text:
            return []

        try:
            doc = nlp_model(text)

            entity_map = {
                "PERSON": "Person",
                "GPE": "Location",
                "LOC": "Location",
                "ORG": "Organization",
                "EVENT": "Event",
                "DATE": "Date",
                "MONEY": "Money",
                "PRODUCT": "Product",
            }

            ignored_words = {
                "the", "and", "or", "but", "this", "that",
                "these", "those", "today", "tomorrow",
                "yesterday", "new", "latest", "live",
                "news", "post", "update", "official",
                "breaking",
            }

            entities = []
            seen = set()

            for ent in doc.ents:
                value = ent.text.strip()

                if not value:
                    continue

                value_lower = value.lower()

                if ent.label_ not in entity_map:
                    continue

                if len(value) < 3:
                    continue

                if value_lower in ignored_words:
                    continue

                if value_lower in seen:
                    continue

                if value.startswith("@"):
                    continue

                if value.isdigit():
                    continue

                entities.append({
                    "name": value,
                    "type": entity_map[ent.label_],
                })

                seen.add(value_lower)

            return entities[:10]

        except Exception:
            logger.exception("NLP entity extraction failed.")
            return []

    @staticmethod
    def extract_json_response(output):
        if not output or not output.strip():
            raise ValueError("Empty AI response.")

        cleaned = (
            output
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        try:
            result = json.loads(cleaned)

            if not isinstance(result, dict):
                raise ValueError("AI response is not a JSON object.")

            return result

        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}", cleaned)

        if not match:
            raise ValueError("No JSON object found in AI response.")

        result = json.loads(match.group(0))

        if not isinstance(result, dict):
            raise ValueError("Extracted AI response is not a JSON object.")

        return result

    @staticmethod
    def clamp_number(value, minimum, maximum, default=0):
        try:
            number = float(value)
            return max(minimum, min(maximum, number))
        except (TypeError, ValueError):
            return default

    def analyze_text(self, text):
        text = (text or "").strip()

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
                "manipulation_signals": [],
            }

        if not GROQ_API_KEY or not groq_client:
            logger.error("Groq is not configured.")

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
                "manipulation_signals": [],
            }

        prompt = f"""
Analyze the following submitted social-media content.

TEXT:
{text[:2000]}

Your task is NLP analysis, NOT factual verification.

Do not decide whether a factual claim is true or false.
Do not use outside knowledge to determine whether the claim
is correct. Current events may have changed.

The separate Fact Verification module verifies factual claims
using external evidence.

Your responsibilities:

1. Extract the main factual claim.
2. Classify the claim type.
3. Identify the language.
4. Extract important keywords.
5. Identify manipulation signals actually present.
6. Estimate linguistic/manipulation risk.

Claim types must be exactly one of:
Political
Financial
Health
Sports
Technology
Entertainment
General

For factual claims, prediction MUST be:
"Needs Verification"

For opinions, jokes, emotions, or other non-factual content,
prediction may be:
"Not a Factual Claim"

Risk score:
0 = no meaningful linguistic/manipulation risk.
100 = very strong linguistic/manipulation signals.

Risk score must NOT represent factual truth.
Do not increase risk merely because a claim is unusual,
recent, future-dated, controversial, or unknown.

Confidence represents confidence in this NLP analysis only.
It is NOT the probability that the claim is true or false.

Possible manipulation signals include:
- sensational language
- excessive urgency
- fear appeal
- unsupported certainty
- fabricated authority
- emotionally manipulative wording
- conspiracy framing
- misleading calls to action

Only report a signal when supported by the submitted text.

Return ONLY valid JSON.
"""

        try:
            response = (
                groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    reasoning_effort="low",
                    include_reasoning=False,
                    max_completion_tokens=1000,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "nlp_misinformation_analysis",
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
                                            "General",
                                        ],
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
                                        },
                                    },
                                    "manipulation_signals": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                    },
                                },
                                "required": [
                                    "claim",
                                    "claim_type",
                                    "prediction",
                                    "confidence",
                                    "risk_score",
                                    "language",
                                    "keywords",
                                    "manipulation_signals",
                                ],
                                "additionalProperties": False,
                            },
                        },
                    },
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert NLP analysis system. "
                                "Analyze linguistic and manipulation signals. "
                                "Do not determine factual truth. "
                                "Return only structured JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
            )

            output = response.choices[0].message.content

            if not output or not output.strip():
                raise ValueError("Groq returned an empty AI response.")

            result = self.extract_json_response(output)

            claim = str(result.get("claim", "Unknown")).strip() or "Unknown"

            allowed_claim_types = {
                "Political",
                "Financial",
                "Health",
                "Sports",
                "Technology",
                "Entertainment",
                "General",
            }

            claim_type = str(
                result.get("claim_type", "General")
            ).strip()

            if claim_type not in allowed_claim_types:
                claim_type = "General"

            prediction = str(
                result.get("prediction", "Needs Verification")
            ).strip()

            if prediction not in {
                "Needs Verification",
                "Not a Factual Claim",
            }:
                prediction = "Needs Verification"

            confidence = self.clamp_number(
                result.get("confidence"),
                0,
                100,
                0,
            )

            risk_score = self.clamp_number(
                result.get("risk_score"),
                0,
                100,
                0,
            )

            confidence = int(confidence) if confidence.is_integer() else confidence
            risk_score = int(risk_score) if risk_score.is_integer() else risk_score

            keywords = result.get("keywords", [])

            if not isinstance(keywords, list):
                keywords = []

            keywords = [
                str(keyword).strip()
                for keyword in keywords
                if str(keyword).strip()
            ][:15]

            manipulation_signals = result.get(
                "manipulation_signals",
                [],
            )

            if not isinstance(manipulation_signals, list):
                manipulation_signals = []

            manipulation_signals = [
                str(signal).strip()
                for signal in manipulation_signals
                if str(signal).strip()
            ][:10]

            return {
                "status": "success",
                "claim": claim,
                "claim_type": claim_type,
                "prediction": prediction,
                "confidence": confidence,
                "risk_score": risk_score,
                "language": str(
                    result.get("language", "English")
                ).strip() or "English",
                "keywords": keywords,
                "entities": self.extract_entities(text),
                "manipulation_signals": manipulation_signals,
            }

        except Exception:
            logger.exception("NLP analysis failed.")

            return {
                "status": "error",
                "claim": text[:200],
                "claim_type": "General",
                "prediction": "Verification Unavailable",
                "confidence": None,
                "risk_score": None,
                "language": "Unknown",
                "keywords": [],
                "entities": self.extract_entities(text),
                "manipulation_signals": [],
            }


nlp_service = NLPService()