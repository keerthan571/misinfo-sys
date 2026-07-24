import os
import json
from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Initialize Tavily
tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)


def verify_claim(claim: str):
    try:
        # -----------------------------
        # Validate Input
        # -----------------------------
        if not claim or len(claim.strip()) < 5:
            return {
                "status": "error",
                "message": "Please enter a valid claim."
            }

        # -----------------------------
        # Search Latest Information
        # -----------------------------
        search_results = tavily_client.search(
            query=claim,
            search_depth="advanced",
            max_results=5
        )

        results = search_results.get("results", [])

        if not results:
            return {
                "status": "success",
                "claim": claim,
                "verdict": "Uncertain",
                "reason": "No reliable web evidence found.",
                "confidence": "0%",
                "sources": []
            }

        evidence = ""
        sources = []

        for result in results:
            title = result.get("title", "")
            content = result.get("content", "")
            url = result.get("url", "")

            evidence += f"""
Title: {title}
Content: {content}
Source: {url}

"""

            if url:
                sources.append(url)

        # Remove duplicate URLs while preserving order
        sources = list(dict.fromkeys(sources))

        # -----------------------------
        # Prompt
        # -----------------------------
        prompt = f"""
You are an expert AI Fact Checker.

A user submitted the following claim:

"{claim}"

Below is the latest information retrieved from the web.

{evidence}

Rules:

1. Use ONLY the evidence provided.
2. Never use your own knowledge.
3. Never guess.
4. If the evidence supports the claim, return "True".
5. If the evidence contradicts the claim, return "False".
6. If the evidence is conflicting, return "Misleading".
7. If the evidence is insufficient, return "Uncertain".

Return ONLY valid JSON.

The verdict MUST be exactly one of:

- True
- False
- Misleading
- Uncertain

Format:

{{
    "verdict": "True",
    "reason": "Explain the verdict in 3-5 lines.",
    "confidence": "98%"
}}

Do NOT return markdown.
Do NOT return any explanation outside the JSON.
Do NOT wrap the JSON inside ```json ... ```.
"""

        # -----------------------------
        # Groq Response
        # -----------------------------
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI fact checker. Use ONLY the provided evidence. Never invent facts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        content = response.choices[0].message.content.strip()

        if not content:
            return {
                "status": "error",
                "message": "Empty response received from Groq."
            }

        # Remove markdown code fences if present
        content = (
            content.replace("```json", "")
                   .replace("```", "")
                   .strip()
        )

        result = json.loads(content)

        # -----------------------------
        # Validate Verdict
        # -----------------------------
        verdict = result.get("verdict", "Uncertain").strip().title()

        valid_verdicts = {
            "True",
            "False",
            "Misleading",
            "Uncertain"
        }

        if verdict not in valid_verdicts:
            verdict = "Uncertain"

        # -----------------------------
        # Normalize Confidence
        # -----------------------------
        confidence = str(result.get("confidence", "0%")).strip()

        if confidence and not confidence.endswith("%"):
            confidence += "%"

        # -----------------------------
        # Final Response
        # -----------------------------
        return {
            "status": "success",
            "claim": claim,
            "verdict": verdict,
            "reason": result.get("reason", ""),
            "confidence": confidence,
            "sources": sources
        }

    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Groq returned an invalid JSON response."
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }