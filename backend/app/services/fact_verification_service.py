import os
import json
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

groq_client=Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

tavily_client=TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

def calculate_confidence(verdict,source_count,evidence_length):
    if verdict=="Verified Information":
        if source_count>=4:
            return 95
        elif source_count>=2:
            return 90
        else:
            return 80
    elif verdict=="False Information":
        if source_count>=3:
            return 95
        elif source_count>=1:
            return 85
        else:
            return 70
    elif verdict=="Misleading Information":
        if source_count>=2:
            return 75
        else:
            return 65
    else:
        if source_count>=2 and evidence_length>500:
            return 45
        return 30

def verify_claim(claim:str):

    if not claim or len(claim.strip())<5:
        return {
            "status":"error",
            "claim":claim,
            "verdict":"Insufficient Evidence",
            "reason":"Invalid claim provided.",
            "confidence":0,
            "sources":[]
        }

    try:

        search=tavily_client.search(
            query=claim[:300],
            search_depth="advanced",
            max_results=5
        )

        results=search.get(
            "results",
            []
        )

        if not results:
            return {
                "status":"success",
                "claim":claim,
                "verdict":"Insufficient Evidence",
                "reason":"No reliable evidence found.",
                "confidence":30,
                "sources":[]
            }

        evidence=""
        sources=[]

        for item in results:

            title=item.get(
                "title",
                ""
            )

            content=item.get(
                "content",
                ""
            )[:1200]

            url=item.get(
                "url",
                ""
            )

            evidence+=f"""
Title:
{title}

Content:
{content}

"""

            if url:
                sources.append(url)

        prompt=f"""
Verify this claim using only the evidence.

Claim:
{claim}

Evidence:
{evidence}

Return only JSON.

Format:

{{
"verdict":"",
"reason":""
}}

Allowed verdicts:
Verified Information
False Information
Misleading Information
Insufficient Evidence
"""

        try:

            response=groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0,
                max_tokens=300,
                messages=[
                    {
                        "role":"system",
                        "content":"You are a strict fact verification AI."
                    },
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            output=response.choices[0].message.content.strip()

        except Exception as e:

            print("GROQ FACT ERROR:",e)

            return {
                "status":"error",
                "claim":claim,
                "verdict":"Insufficient Evidence",
                "reason":"Fact verification service unavailable.",
                "confidence":0,
                "sources":sources
            }

        output=output.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        result=json.loads(
            output
        )

        verdict=result.get(
            "verdict",
            "Insufficient Evidence"
        )

        allowed=[
            "Verified Information",
            "False Information",
            "Misleading Information",
            "Insufficient Evidence"
        ]

        if verdict not in allowed:
            verdict="Insufficient Evidence"

        confidence=calculate_confidence(
            verdict,
            len(sources),
            len(evidence)
        )

        return {
            "status":"success",
            "claim":claim,
            "verdict":verdict,
            "reason":result.get(
                "reason",
                "No explanation available."
            ),
            "confidence":confidence,
            "sources":list(
                dict.fromkeys(
                    sources
                )
            )
        }

    except json.JSONDecodeError:

        return {
            "status":"error",
            "claim":claim,
            "verdict":"Insufficient Evidence",
            "reason":"Invalid response from AI.",
            "confidence":0,
            "sources":[]
        }

    except Exception as e:

        print("FACT VERIFICATION ERROR:",e)

        return {
            "status":"error",
            "claim":claim,
            "verdict":"Insufficient Evidence",
            "reason":"Verification failed.",
            "confidence":0,
            "sources":[]
        }