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
        # Search latest information
        search_results = tavily_client.search(
            query=claim,
            search_depth="advanced",
            max_results=5
        )

        evidence = ""
        sources = []

        for result in search_results["results"]:
            evidence += f"""
Title: {result['title']}
Content: {result['content']}
Source: {result['url']}

"""
            sources.append(result["url"])

        prompt = f"""
You are an expert AI Fact Checker.

A user submitted the following claim:

"{claim}"

Below is the latest information retrieved from the web.

{evidence}

Using ONLY the evidence above, determine whether the claim is True, False, Misleading, or Uncertain.

Return ONLY valid JSON in the following format:

{{
    "verdict": "True",
    "reason": "Explain the verdict in 3-5 lines.",
    "confidence": "98%"
}}

Do NOT return markdown.
Do NOT return any extra text.
Return ONLY valid JSON.
"""

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

        # Parse JSON returned by Groq
        result = json.loads(response.choices[0].message.content)

        return {
            "status": "success",
            "claim": claim,
            "verdict": result["verdict"],
            "reason": result["reason"],
            "confidence": result["confidence"],
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