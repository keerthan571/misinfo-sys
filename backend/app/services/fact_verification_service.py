import os
import json
import logging
import re

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient


load_dotenv()

logger = logging.getLogger(__name__)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


groq_client = Groq(
    api_key=GROQ_API_KEY
) if GROQ_API_KEY else None


tavily_client = TavilyClient(
    api_key=TAVILY_API_KEY
) if TAVILY_API_KEY else None


ALLOWED_VERDICTS = {
    "Verified Information",
    "False Information",
    "Misleading Information",
    "Insufficient Evidence",
}


def calculate_confidence(
    verdict,
    source_count,
    evidence_length,
    claim
):

    words = claim.split()

    # Claim quality
    claim_score = 0

    if len(words) >= 8:
        claim_score += 10

    if any(char.isdigit() for char in claim):
        claim_score += 10

    # Evidence quality
    evidence_score = 0

    if source_count >= 5:
        evidence_score += 30
    elif source_count >= 3:
        evidence_score += 20
    elif source_count >= 1:
        evidence_score += 10

    if evidence_length >= 3000:
        evidence_score += 25
    elif evidence_length >= 1500:
        evidence_score += 15
    elif evidence_length >= 500:
        evidence_score += 8

    # Verdict base confidence
    if verdict == "Verified Information":
        base = 50
    elif verdict == "False Information":
        base = 45
    elif verdict == "Misleading Information":
        base = 40
    else:
        base = 25

    confidence = (
        base
        + claim_score
        + evidence_score
    )

    # Short/vague claims should not get very high confidence
    if len(words) < 5:
        confidence = min(confidence, 45)

    if source_count == 0:
        confidence = min(confidence, 35)

    return max(
        20,
        min(confidence, 95)
    )


def extract_json_response(output: str):

    if not output:
        raise ValueError("Empty AI response.")

    cleaned = (
        output
        .replace("```json", "")
        .replace("```JSON", "")
        .replace("```", "")
        .strip()
    )

    # First try parsing the entire response
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Extract the first JSON object if extra text exists
    match = re.search(
        r"\{[\s\S]*\}",
        cleaned
    )

    if not match:
        raise ValueError(
            "No JSON object found in AI response."
        )

    return json.loads(match.group(0))


def verify_claim(claim: str):

    claim = (claim or "").strip()

    if len(claim) < 5:
        return {
            "status": "error",
            "claim": claim,
            "verdict": "Verification Unavailable",
            "reason": "A valid claim is required for verification.",
            "confidence": None,
            "sources": []
        }

    if not TAVILY_API_KEY:
        logger.error(
            "TAVILY_API_KEY is not configured."
        )

        return {
            "status": "error",
            "claim": claim,
            "verdict": "Verification Unavailable",
            "reason": "Fact verification service is not configured.",
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
            "verdict": "Verification Unavailable",
            "reason": "AI verification service is not configured.",
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
            "verdict": "Verification Unavailable",
            "reason": "Verification service initialization failed.",
            "confidence": None,
            "sources": []
        }

    sources = []
    evidence = ""

    try:

        search = tavily_client.search(
            query=claim[:500],
            search_depth="advanced",
            max_results=5
        )

        results = search.get(
            "results",
            []
        )

        if not results:
            return {
                "status": "success",
                "claim": claim,
                "verdict": "Insufficient Evidence",
                "reason": (
                    "No sufficient reliable evidence was found "
                    "for this claim."
                ),
                "confidence": 25,
                "sources": []
            }

        for item in results:

            title = item.get(
                "title",
                ""
            )

            content = item.get(
                "content",
                ""
            )[:1200]

            url = item.get(
                "url",
                ""
            )

            evidence += f"""
Title:
{title}

Content:
{content}

"""

            if url:
                sources.append(url)

        # Remove duplicates while preserving order
        sources = list(
            dict.fromkeys(sources)
        )

        prompt = f"""
Verify the following claim using ONLY the provided evidence.

CLAIM:
{claim}

EVIDENCE:
{evidence}

Return ONLY a valid JSON object in exactly this format:

{{
    "verdict": "one allowed verdict",
    "reason": "brief evidence-based explanation"
}}

Allowed verdicts:
- Verified Information
- False Information
- Misleading Information
- Insufficient Evidence

Rules:
- Do not use knowledge outside the provided evidence.
- Do not assume missing facts.
- Mark False Information only when the evidence clearly contradicts the claim.
- Mark Verified Information only when the evidence clearly supports the claim.
- Use Misleading Information when the claim contains partially correct but materially incomplete or distorted information.
- Use Insufficient Evidence when the available evidence cannot support or contradict the claim.
"""

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=300,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict fact verification AI. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        output = (
            response.choices[0]
            .message.content
            .strip()
        )

        logger.info(
            "Fact verification AI response received successfully."
        )

        result = extract_json_response(output)

        verdict = result.get(
            "verdict",
            "Insufficient Evidence"
        )

        if verdict not in ALLOWED_VERDICTS:
            logger.warning(
                "Invalid verdict returned by AI: %s",
                verdict
            )
            verdict = "Insufficient Evidence"

        reason = (
            result.get("reason")
            or "No explanation was provided by the verification model."
        )

        confidence = calculate_confidence(
            verdict,
            len(sources),
            len(evidence),
            claim
        )

        return {
            "status": "success",
            "claim": claim,
            "verdict": verdict,
            "reason": reason,
            "confidence": confidence,
            "sources": sources
        }

    except json.JSONDecodeError:
        logger.exception(
            "Failed to parse AI verification JSON response."
        )

        return {
            "status": "error",
            "claim": claim,
            "verdict": "Verification Unavailable",
            "reason": (
                "The AI returned an invalid verification response."
            ),
            "confidence": None,
            "sources": sources
        }

    except Exception:
        logger.exception(
            "FACT VERIFICATION ERROR"
        )

        return {
            "status": "error",
            "claim": claim,
            "verdict": "Verification Unavailable",
            "reason": (
                "The fact verification service could not complete "
                "the request."
            ),
            "confidence": None,
            "sources": sources
        }