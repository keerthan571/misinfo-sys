import json
import logging
import os
import re


from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class NLPService:

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
            raise ValueError(
                "Extracted AI response is not a JSON object."
            )

        return result

    @staticmethod
    def clamp_number(value, minimum, maximum, default=0):
        try:
            number = float(value)
            return max(minimum, min(maximum, number))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def is_question_only(text):
        """
        Returns True when the submitted content is primarily
        an interrogative question rather than a factual assertion.
        """
        text = (text or "").strip()

        if not text:
            return False

        # Strong signal: the entire submission ends as a question.
        if not text.endswith("?"):
            return False

        # Common English question starters.
        question_starters = (
            "who ",
            "what ",
            "when ",
            "where ",
            "why ",
            "how ",
            "is ",
            "are ",
            "am ",
            "was ",
            "were ",
            "do ",
            "does ",
            "did ",
            "has ",
            "have ",
            "had ",
            "can ",
            "could ",
            "will ",
            "would ",
            "should ",
            "shall ",
            "may ",
            "might ",
            "which ",
        )

        lowered = text.lower()

        return lowered.startswith(question_starters)
    
    @staticmethod
    def is_opinion_only(text):
        text = (text or "").strip().lower()

        opinion_starters = (
            "i think ",
            "i feel ",
            "i believe ",
            "in my opinion ",
            "imo ",
            "personally ",
            "i would say ",
            "i consider ",
        )

        return text.startswith(opinion_starters)
    def analyze_text(self, text):
        text = (text or "").strip()

        # ---------------------------------------------------------
        # QUESTION-ONLY CONTENT
        # ---------------------------------------------------------
        # A question is not itself a factual assertion.
        # Do not send question-only content to fact verification.
        if self.is_question_only(text):
            return {
                "status": "success",
                "claim": "",
                "claim_type": "General",
                "prediction": "Not a Factual Claim",
                "confidence": 0,
                "risk_score": 0,
                "keywords": [],
                "language": "English",
                "manipulation_signals": [],
            }

        if self.is_opinion_only(text):
                return {
                    "status": "success",
                    "claim": "",
                    "claim_type": "Opinion",
                    "prediction": "Not a Factual Claim",
                    "confidence": 0,
                    "risk_score": 0,
                    "keywords": [],
                    "language": "English",
                    "manipulation_signals": [],
                }
        
        if len(text) < 5:
            return {
                "status": "error",
                "claim": "Unknown",
                "claim_type": "Unknown",
                "prediction": "Needs Verification",
                "confidence": None,
                "risk_score": None,
                "keywords": [],
                 
                "language": "Unknown",
                "manipulation_signals": [],
            }

        if not GROQ_API_KEY or not groq_client:
            logger.error("Groq is not configured.")

            return {
                "status": "success",
                "claim": claim,
                "claim_type": claim_type,
                "prediction": prediction,
                "confidence": confidence,
                "risk_score": risk_score,
                "language": language,
                "keywords": keywords,
                "manipulation_signals": manipulation_signals,
            }

        prompt = f"""
Analyze the following submitted social-media content.

The submitted content may come from OCR of a screenshot.
Therefore, it may contain OCR errors, social-media interface
text, usernames, hashtags, engagement counts, publisher
information, unrelated text, and text in languages unrelated
to the main claim.

OCR / SUBMITTED TEXT:
{text[:2000]}

Your task is NLP analysis, NOT factual verification.

Do not decide whether a factual claim is true or false.
Do not use outside knowledge to determine whether the claim
is correct. Current events may have changed.

The separate Fact Verification module verifies factual claims
using external evidence.


IMPORTANT QUESTION RULE:

- A question is NOT itself a factual assertion.
- If the submitted content is solely a question asking whether,
  when, where, why, who, what, or how something happened,
  do NOT extract the question as a factual claim.
- For a question-only submission, return:
  claim = ""
  prediction = "Not a Factual Claim"
- Do NOT send question-only content for factual verification.
- Examples:
  "Did the Bengaluru Metro Purple Line extension open on
   September 28, 2026?"
  -> claim = ""
  -> prediction = "Not a Factual Claim"

  "Is drinking warm water enough to prevent diabetes?"
  -> claim = ""
  -> prediction = "Not a Factual Claim"

  "When did the Bengaluru Metro Purple Line extension open?"
  -> claim = ""
  -> prediction = "Not a Factual Claim"

- A question may contain factual information as part of its wording,
  but the question itself must not automatically be treated as a
  factual assertion.
- Only extract a claim if the submitted content also contains a
  separate factual assertion outside the question.
  
Your responsibilities:

1. Identify whether the submitted content contains at least
   one independently verifiable factual assertion.

2. If one or more factual assertions are present, extract the
   MOST IMPORTANT factual assertion as the claim.

3. If the content contains both non-factual content and factual
   assertions, extract the factual assertion rather than
   classifying the entire post as non-factual.

4. Classify the claim type.

5. Determine the language of the MAIN CLAIM.

6. Extract important keywords from the MAIN CLAIM.

7. Identify manipulation signals actually present in the
   submitted content.

8. Estimate linguistic/manipulation risk.

IMPORTANT LANGUAGE RULES:

- Determine language from the MAIN CLAIM, not from the entire
  OCR text.
- Ignore social-media UI text, usernames, hashtags,
  engagement numbers, publisher names, OCR artifacts,
  unrelated text, and unrelated multilingual text.
- First identify the MAIN factual claim.
- Then determine the language in which that MAIN claim is
  written.
- If the MAIN claim is entirely English, return "English".
- If the MAIN claim is entirely Hindi, return "Hindi".
- If the MAIN claim is entirely Kannada, return "Kannada".
- Return "Mixed" ONLY when the MAIN CLAIM itself genuinely
  contains two or more languages in a meaningful way.
- Do NOT return "Mixed" merely because unrelated OCR text
  contains another script or language.
- OCR noise or isolated words from another language must not
  cause the result to become "Mixed".

The language value MUST be exactly one of:
English
Hindi
Kannada
Mixed

Claim types must be exactly one of:
Political
Financial
Health
Sports
Technology
Entertainment
General

PREDICTION RULES:

- If the submitted content contains at least one independently
  verifiable factual assertion, prediction MUST be:
  "Needs Verification"

- If the submitted content contains no independently verifiable
  factual assertion, prediction MUST be:
  "Not a Factual Claim"

- A post does NOT become "Not a Factual Claim" merely because
  it also contains greetings, wishes, opinions, emotions,
  praise, criticism, questions, hashtags, or other non-factual
  content.

- If a post contains both emotional/non-factual content and a
  factual assertion, extract the factual assertion and return:
  "Needs Verification".

- Do not decide whether the factual assertion is true or false.
  That is the responsibility of the separate Fact Verification
  module.

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
EXAMPLES:

Example 1:

Content:
"Happy birthday! Wishing you health, happiness and success
always."

Result:
- claim = ""
- prediction = "Not a Factual Claim"

Reason:
The content contains only a birthday wish and no independently
verifiable factual assertion.


Example 2:

Content:
"Happy birthday! He has acted in more than 20 films and has
also directed several movies."

Result:
- claim = "He has acted in more than 20 films and has also
  directed several movies."
- prediction = "Needs Verification"

Reason:
The birthday greeting is non-factual, but the post contains
verifiable factual assertions.


Example 3:

Content:
"I think this is the greatest movie ever made."

Result:
- claim = ""
- prediction = "Not a Factual Claim"

Reason:
This is an opinion rather than an independently verifiable
factual assertion.


Example 4:

Content:
"The company announced a 20% increase in revenue this year."

Result:
- claim = "The company announced a 20% increase in revenue
  this year."
- prediction = "Needs Verification"

Reason:
This is a factual assertion that can be checked against
evidence.


Example 5:

Content:
"This medicine completely cures diabetes."

Result:
- claim = "This medicine completely cures diabetes."
- prediction = "Needs Verification"

Reason:
This is a factual/medical assertion requiring external
verification.


Example 6:

Content:
"Congratulations to the team! They won yesterday's match
by 7 wickets."

Result:
- claim = "The team won yesterday's match by 7 wickets."
- prediction = "Needs Verification"

Reason:
The congratulatory text is non-factual, but the match result
is a verifiable factual assertion.


IMPORTANT:
These examples demonstrate the distinction between the PURPOSE
or tone of a post and the presence of verifiable factual
assertions. Always extract a factual assertion when one exists,
even when it appears inside a greeting, opinion, emotional post,
advertisement, or social-media caption.

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
                                        "type": "string",
                                        "enum": [
                                            "English",
                                            "Hindi",
                                            "Kannada",
                                            "Mixed",
                                        ],
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
                                "Determine language from the MAIN CLAIM only. "
                                "Ignore unrelated OCR text and social-media "
                                "interface text when determining language. "
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

            claim = str(
                    result.get("claim", "")
                ).strip()

            invalid_claims = {
                    "",
                    "unknown",
                    "n/a",
                    "none",
                    "null",
                    "not a factual claim",
                }

            if claim.lower() in invalid_claims:

                    prediction = str(
                        result.get(
                            "prediction",
                            "Not a Factual Claim"
                        )
                    ).strip()

                    if prediction not in {
                        "Needs Verification",
                        "Not a Factual Claim",
                    }:
                        prediction = "Not a Factual Claim"

                    return {
                        "status": "success",
                        "claim": "",
                        "claim_type": "General",
                        "prediction": prediction,
                        "confidence": 0,
                        "risk_score": 0,
                        "keywords": [],
                         
                        "language": str(
                            result.get(
                                "language",
                                "Unknown"
                            )
                        ).strip(),
                        "manipulation_signals": [],
                    }

            claim = text[:500].strip()

            if not claim:
                    return {
                        "status": "error",
                        "claim": "Unknown",
                        "claim_type": "General",
                        "prediction": "Verification Unavailable",
                        "confidence": None,
                        "risk_score": None,
                        "language": "Unknown",
                        "keywords": [],
                         
                        "manipulation_signals": [],
                    }

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
                result.get(
                    "prediction",
                    "Needs Verification"
                )
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

            confidence = (
                int(confidence)
                if confidence.is_integer()
                else confidence
            )

            risk_score = (
                int(risk_score)
                if risk_score.is_integer()
                else risk_score
            )

            # ---------------------------------------------
            # LANGUAGE VALIDATION
            # ---------------------------------------------

            language = str(
                result.get("language", "English")
            ).strip()

            allowed_languages = {
                "English",
                "Hindi",
                "Kannada",
                "Mixed",
            }

            if language not in allowed_languages:
                language = "English"

            # ---------------------------------------------
            # KEYWORDS
            # ---------------------------------------------

            keywords = result.get("keywords", [])

            if not isinstance(keywords, list):
                keywords = []

            keywords = [
                str(keyword).strip()
                for keyword in keywords
                if str(keyword).strip()
            ][:15]

            # ---------------------------------------------
            # MANIPULATION SIGNALS
            # ---------------------------------------------

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

            # ---------------------------------------------
            # FINAL RESULT
            # ---------------------------------------------

            return {
                "status": "success",
                "claim": claim,
                "claim_type": claim_type,
                "prediction": prediction,
                "confidence": confidence,
                "risk_score": risk_score,
                "language": language,
                "keywords": keywords,
                 
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
                 
                "manipulation_signals": [],
            }


nlp_service = NLPService()