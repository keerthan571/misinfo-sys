import json
import logging
import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


load_dotenv()


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)


# ============================================================
# CLIENT INITIALIZATION
# ============================================================

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)

tavily_client = (
    TavilyClient(api_key=TAVILY_API_KEY)
    if TAVILY_API_KEY
    else None
)


# ============================================================
# ALLOWED VERDICTS
# ============================================================

ALLOWED_VERDICTS = {
    "Verified Information",
    "False Information",
    "Misleading Information",
    "Insufficient Evidence",
}


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_response(output: str) -> dict[str, Any]:

    if not output or not output.strip():

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

    # --------------------------------------------------------
    # Attempt 1:
    # Entire response is JSON
    # --------------------------------------------------------

    try:

        result = json.loads(
            cleaned
        )

        if not isinstance(result, dict):

            raise ValueError(
                "AI response JSON is not an object."
            )

        return result

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Attempt 2:
    # Extract JSON object surrounded by other text
    # --------------------------------------------------------

    match = re.search(
        r"\{[\s\S]*\}",
        cleaned
    )

    if not match:

        raise ValueError(
            "No JSON object found in AI response."
        )

    result = json.loads(
        match.group(0)
    )

    if not isinstance(result, dict):

        raise ValueError(
            "Extracted AI response is not a JSON object."
        )

    return result


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# CONFIDENCE CALCULATION
# ============================================================

def calculate_confidence(
    verdict: str,
    source_count: int,
    evidence_length: int,
    evidence_strength: float | None = None,
) -> int:

    """
    Calculate confidence in the verification verdict.

    This confidence represents confidence in the evidence-based
    verification result. It is NOT a probability that the claim
    is true.

    The calculation considers:
    - verification verdict
    - number of retrieved sources
    - amount of usable evidence
    - evidence strength reported by the verification model

    Importantly, a large amount of weak evidence should not
    automatically produce high confidence.
    """

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if source_count <= 0 or evidence_length <= 0:

        return 0

    # --------------------------------------------------------
    # Evidence quantity score
    # --------------------------------------------------------

    if source_count >= 5:
        source_score = 25

    elif source_count >= 4:
        source_score = 22

    elif source_count >= 3:
        source_score = 18

    elif source_count >= 2:
        source_score = 12

    else:
        source_score = 7

    # --------------------------------------------------------
    # Evidence length score
    # --------------------------------------------------------

    if evidence_length >= 5000:
        length_score = 20

    elif evidence_length >= 3000:
        length_score = 17

    elif evidence_length >= 1500:
        length_score = 13

    elif evidence_length >= 750:
        length_score = 9

    else:
        length_score = 5

    # --------------------------------------------------------
    # Base verdict score
    # --------------------------------------------------------

    if verdict == "Verified Information":

        base_score = 45

    elif verdict == "False Information":

        base_score = 45

    elif verdict == "Misleading Information":

        base_score = 40

    else:

        # Insufficient evidence should never look
        # extremely certain.
        base_score = 20

    # --------------------------------------------------------
    # Model evidence-strength contribution
    # --------------------------------------------------------

    if evidence_strength is None:

        model_score = 0

    else:

        try:

            strength = max(
                0,
                min(
                    100,
                    float(evidence_strength)
                )
            )

            model_score = round(
                strength * 0.10
            )

        except (
            TypeError,
            ValueError
        ):

            model_score = 0

    confidence = (
        base_score
        + source_score
        + length_score
        + model_score
    )

    # --------------------------------------------------------
    # Verdict-specific safety caps
    # --------------------------------------------------------

    if verdict == "Insufficient Evidence":

        confidence = min(
            confidence,
            65
        )

    else:

        confidence = min(
            confidence,
            95
        )

    return max(
        0,
        min(
            int(confidence),
            95
        )
    )


# ============================================================
# SEARCH QUERY GENERATION
# ============================================================

def build_search_queries(claim: str) -> list[str]:

    """
    Generate a small set of complementary search queries.

    The system remains domain-independent. No sport, political,
    medical or other domain is hardcoded.
    """

    claim = claim.strip()

    queries = [

        claim[:500],

        f'"{claim[:350]}" fact check',

        f'"{claim[:350]}" official result'

    ]

    # Remove duplicates while preserving order.

    unique_queries = list(
        dict.fromkeys(
            query.strip()
            for query in queries
            if query.strip()
        )
    )

    return unique_queries[:3]


# ============================================================
# TAVILY SEARCH
# ============================================================

def collect_evidence(claim: str):

    """
    Search multiple complementary queries and combine the
    resulting evidence.

    Returns:
        evidence_text
        sources
    """

    all_results = []

    queries = build_search_queries(
        claim
    )

    for query in queries:

        try:

            search = tavily_client.search(

                query=query,

                search_depth="advanced",

                max_results=5

            )

            results = search.get(
                "results",
                []
            )

            if isinstance(
                results,
                list
            ):

                all_results.extend(
                    results
                )

        except Exception:

            logger.exception(
                "Tavily search failed for query: %s",
                query
            )

    # --------------------------------------------------------
    # Deduplicate results by URL
    # --------------------------------------------------------

    unique_results = []

    seen_urls = set()

    for item in all_results:

        if not isinstance(
            item,
            dict
        ):
            continue

        url = normalize_text(
            item.get("url")
        )

        if url:

            if url in seen_urls:
                continue

            seen_urls.add(url)

        unique_results.append(
            item
        )

    # Keep evidence manageable.

    unique_results = unique_results[:10]

    # --------------------------------------------------------
    # Build evidence text
    # --------------------------------------------------------

    evidence_parts = []

    sources = []

    for index, item in enumerate(
        unique_results,
        start=1
    ):

        title = normalize_text(
            item.get("title")
        )

        content = normalize_text(
            item.get("content")
        )

        url = normalize_text(
            item.get("url")
        )

        published_date = normalize_text(
            item.get("published_date")
        )

        # Limit individual evidence chunks.

        content = content[:1800]

        evidence_parts.append(
            f"""
SOURCE {index}

Title:
{title}

Published Date:
{published_date or "Not available"}

URL:
{url}

Content:
{content}
"""
        )

        if url:

            sources.append(
                url
            )

    evidence = "\n".join(
        evidence_parts
    )

    sources = list(
        dict.fromkeys(
            sources
        )
    )

    return (
        evidence,
        sources
    )


# ============================================================
# VERIFICATION PROMPT
# ============================================================

def build_verification_prompt(
    claim: str,
    evidence: str
) -> str:

    return f"""
You are performing evidence-based fact verification.

CLAIM:
{claim}

PROVIDED EVIDENCE:
{evidence}

Your task is to determine whether the CLAIM is supported,
contradicted, materially distorted, or not established by
the PROVIDED EVIDENCE.

IMPORTANT:

1. Use ONLY the provided evidence.
2. Do not use your own memory or outside knowledge.
3. Pay close attention to dates and years.
4. A claim about a specific year must be evaluated against
   evidence referring to that same year.
5. Do not treat an article about an earlier or later year as
   proof of the current claim.
6. If evidence clearly states that another person, team,
   organization, event, result, date or outcome occurred
   instead of what the claim states, that is evidence
   contradicting the claim.
7. Do not mark a claim false merely because evidence does
   not explicitly repeat the exact wording.
8. If multiple reliable sources consistently support the
   claim, mark it Verified Information.
9. If reliable evidence clearly contradicts the claim,
   mark it False Information.
10. If the claim contains a mixture of supported and
    materially distorted information, mark it
    Misleading Information.
11. If the available evidence is insufficient to determine
    whether the claim is true or false, mark it
    Insufficient Evidence.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "verdict": "Verified Information | False Information | Misleading Information | Insufficient Evidence",
    "reason": "brief explanation directly based on the provided evidence",
    "evidence_strength": 0
}}

evidence_strength must be an integer from 0 to 100.

Interpret evidence_strength as:

0-25:
Very weak or insufficient evidence.

26-50:
Limited evidence.

51-75:
Moderately strong evidence.

76-100:
Strong and consistent evidence.

Do NOT use evidence_strength as probability that the claim
is true. It measures the strength of the available evidence
for the selected verdict.
"""


# ============================================================
# GROQ VERIFICATION
# ============================================================

def run_groq_verification(
    claim: str,
    evidence: str
):

    prompt = build_verification_prompt(
        claim,
        evidence
    )

    # ========================================================
    # FIRST ATTEMPT
    # ========================================================

    try:

        response = (
            groq_client
            .chat
            .completions
            .create(

                model=GROQ_MODEL,

                reasoning_effort="low",

                include_reasoning=False,

                max_completion_tokens=1200,

                response_format={

                    "type": "json_schema",

                    "json_schema": {

                        "name":
                            "fact_verification",

                        "strict": True,

                        "schema": {

                            "type": "object",

                            "properties": {

                                "verdict": {

                                    "type": "string",

                                    "enum": [

                                        "Verified Information",

                                        "False Information",

                                        "Misleading Information",

                                        "Insufficient Evidence"

                                    ]

                                },

                                "reason": {

                                    "type": "string"

                                },

                                "evidence_strength": {

                                    "type": "integer",

                                    "minimum": 0,

                                    "maximum": 100

                                }

                            },

                            "required": [

                                "verdict",

                                "reason",

                                "evidence_strength"

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
                            "You are a strict evidence-based "
                            "fact verification system. "
                            "Use only supplied evidence. "
                            "Return structured JSON."
                        )

                    },

                    {

                        "role": "user",

                        "content": prompt

                    }

                ]

            )
        )

        output = (
            response
            .choices[0]
            .message
            .content
        )

        # ----------------------------------------------------
        # Important:
        # Some reasoning models can occasionally return
        # an empty content field.
        # ----------------------------------------------------

        if output and output.strip():

            return extract_json_response(
                output
            )

        logger.warning(
            "Groq returned an empty structured response. "
            "Attempting fallback verification."
        )

    except Exception:

        logger.exception(
            "Primary Groq fact-verification request failed."
        )

    # ========================================================
    # FALLBACK ATTEMPT
    # ========================================================

    try:

        fallback_response = (
            groq_client
            .chat
            .completions
            .create(

                model=GROQ_MODEL,

                reasoning_effort="low",

                include_reasoning=False,

                max_completion_tokens=800,

                messages=[

                    {

                        "role": "system",

                        "content": (
                            "You are a strict fact verifier. "
                            "Return ONLY JSON."
                        )

                    },

                    {

                        "role": "user",

                        "content": f"""
Verify this claim using ONLY the evidence.

CLAIM:
{claim}

EVIDENCE:
{evidence}

Return ONLY JSON:

{{
    "verdict": "Verified Information | False Information | Misleading Information | Insufficient Evidence",
    "reason": "brief evidence-based explanation",
    "evidence_strength": 0
}}

Rules:
- Do not use outside knowledge.
- Pay attention to dates and years.
- Clearly contradictory evidence means False Information.
- Clearly supporting evidence means Verified Information.
- Mixed/distorted evidence means Misleading Information.
- Otherwise use Insufficient Evidence.
- evidence_strength must be 0-100.
"""
                    }

                ]

            )
        )

        fallback_output = (
            fallback_response
            .choices[0]
            .message
            .content
        )

        if not fallback_output:

            raise ValueError(
                "Fallback Groq response was empty."
            )

        return extract_json_response(
            fallback_output
        )

    except Exception:

        logger.exception(
            "Fallback Groq fact-verification request failed."
        )

        raise


# ============================================================
# MAIN VERIFICATION FUNCTION
# ============================================================

def verify_claim(claim: str):

    claim = normalize_text(
        claim
    )

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    if len(claim) < 5:

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "A valid claim is required for verification.",

            "confidence": None,

            "sources": []

        }

    # ========================================================
    # API CONFIGURATION
    # ========================================================

    if not TAVILY_API_KEY:

        logger.error(
            "TAVILY_API_KEY is not configured."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "Fact verification service is not configured.",

            "confidence": None,

            "sources": []

        }

    if not GROQ_API_KEY:

        logger.error(
            "GROQ_API_KEY is not configured."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "AI verification service is not configured.",

            "confidence": None,

            "sources": []

        }

    if not tavily_client or not groq_client:

        logger.error(
            "Fact verification clients could not be initialized."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "Verification service initialization failed.",

            "confidence": None,

            "sources": []

        }

    # ========================================================
    # SEARCH + VERIFICATION
    # ========================================================

    sources = []

    evidence = ""

    try:

        # ----------------------------------------------------
        # Retrieve evidence
        # ----------------------------------------------------

        (
            evidence,
            sources
        ) = collect_evidence(
            claim
        )

        # ----------------------------------------------------
        # No evidence
        # ----------------------------------------------------

        if not evidence.strip():

            return {

                "status": "success",

                "claim": claim,

                "verdict":
                    "Insufficient Evidence",

                "reason": (
                    "No sufficient evidence was found "
                    "to verify or contradict this claim."
                ),

                "confidence": 0,

                "sources": []

            }

        # ----------------------------------------------------
        # Verify using Groq
        # ----------------------------------------------------

        result = run_groq_verification(

            claim,

            evidence

        )

        # ----------------------------------------------------
        # Extract verdict
        # ----------------------------------------------------

        verdict = normalize_text(
            result.get(
                "verdict"
            )
        )

        if verdict not in ALLOWED_VERDICTS:

            logger.warning(
                "Invalid verdict returned by AI: %s",
                verdict
            )

            verdict = (
                "Insufficient Evidence"
            )

        # ----------------------------------------------------
        # Extract reason
        # ----------------------------------------------------

        reason = normalize_text(
            result.get(
                "reason"
            )
        )

        if not reason:

            reason = (
                "No explanation was provided "
                "by the verification model."
            )

        # ----------------------------------------------------
        # Evidence strength
        # ----------------------------------------------------

        evidence_strength = result.get(
            "evidence_strength"
        )

        try:

            evidence_strength = max(
                0,
                min(
                    100,
                    int(
                        evidence_strength
                    )
                )
            )

        except (
            TypeError,
            ValueError
        ):

            evidence_strength = None

        # ----------------------------------------------------
        # Calculate final confidence
        # ----------------------------------------------------

        confidence = calculate_confidence(

            verdict,

            len(sources),

            len(evidence),

            evidence_strength

        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        logger.info(
            "Fact verification completed: verdict=%s "
            "confidence=%s sources=%s",
            verdict,
            confidence,
            len(sources)
        )

        return {

            "status": "success",

            "claim": claim,

            "verdict": verdict,

            "reason": reason,

            "confidence": confidence,

            "sources": sources

        }

    # ========================================================
    # JSON ERROR
    # ========================================================

    except json.JSONDecodeError:

        logger.exception(
            "Failed to parse AI fact-verification JSON."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason": (
                "The verification model returned "
                "an invalid response."
            ),

            "confidence": None,

            "sources": sources

        }

    # ========================================================
    # ALL OTHER ERRORS
    # ========================================================

    except Exception:

        logger.exception(
            "FACT VERIFICATION ERROR"
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason": (
                "The fact verification service "
                "could not complete the request."
            ),

            "confidence": None,

            "sources": sources

        }