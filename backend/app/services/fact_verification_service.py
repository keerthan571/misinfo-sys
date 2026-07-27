import os
import json

from groq import Groq
from tavily import TavilyClient
from dotenv import load_dotenv


load_dotenv()


# ==========================
# Clients
# ==========================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


tavily_client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)



def verify_claim(claim: str):

    try:

        # ==========================
        # Validate Input
        # ==========================

        if not claim or len(claim.strip()) < 5:

            return {
                "status": "error",
                "claim": claim,
                "verdict": "Insufficient Evidence",
                "reason": "Invalid claim provided.",
                "confidence": "0%",
                "sources": []
            }



        # ==========================
        # Tavily Search
        # ==========================

        search_results = tavily_client.search(

            query=claim,

            search_depth="advanced",

            max_results=5

        )


        results = search_results.get(
            "results",
            []
        )



        if not results:

            return {

                "status": "success",

                "claim": claim,

                "verdict": "Insufficient Evidence",

                "reason":
                "No reliable evidence found from available sources.",

                "confidence": "0%",

                "sources": []

            }



        evidence = ""

        sources = []



        for item in results:


            title = item.get(
                "title",
                ""
            )


            content = item.get(
                "content",
                ""
            )[:1000]


            url = item.get(
                "url",
                ""
            )



            evidence += f"""

Title:
{title}

Content:
{content}

Source:
{url}

"""



            if url:

                sources.append(url)



        sources = list(
            dict.fromkeys(
                sources
            )
        )



        # ==========================
        # Groq Verification
        # ==========================


        prompt = f"""

You are an expert fact verification AI.


Claim:

"{claim}"


Evidence collected from web:

{evidence}



Rules:

- Use only provided evidence.
- Do not use previous knowledge.
- Do not guess.
- If evidence strongly supports the claim return Verified Information.
- If evidence contradicts the claim return False Information.
- If evidence shows partial or misleading context return Misleading Information.
- If evidence is insufficient return Insufficient Evidence.



Return ONLY JSON.



Format:


{{
"verdict":"Verified Information",
"reason":"Short explanation",
"confidence":"90%"
}}

"""



        response = groq_client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            temperature=0,

            messages=[

                {
                    "role": "system",
                    "content":
                    "You are a strict fact checking AI."
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )



        output = response.choices[0].message.content.strip()



        if not output:

            return {

                "status": "error",

                "claim": claim,

                "verdict": "Insufficient Evidence",

                "reason":
                "Empty AI response received.",

                "confidence": "0%",

                "sources": sources

            }



        output = (

            output

            .replace(
                "```json",
                ""
            )

            .replace(
                "```",
                ""
            )

            .strip()

        )



        result = json.loads(output)



        # ==========================
        # Normalize Result
        # ==========================


        verdict = (

            result.get(
                "verdict",
                "Insufficient Evidence"
            )

            .strip()

            .title()

        )



        allowed = [

            "Verified Information",

            "False Information",

            "Misleading Information",

            "Insufficient Evidence"

        ]



        if verdict not in allowed:

            verdict = "Insufficient Evidence"



        confidence = str(

            result.get(

                "confidence",

                "0%"

            )

        )


        if not confidence.endswith("%"):

            confidence += "%"




        return {


            "status": "success",

            "claim": claim,

            "verdict": verdict,

            "reason":

            result.get(

                "reason",

                "No explanation available."

            ),

            "confidence": confidence,

            "sources": sources

        }




    except json.JSONDecodeError:


        return {

            "status": "error",

            "claim": claim,

            "verdict": "Insufficient Evidence",

            "reason":
            "Invalid JSON returned by AI model.",

            "confidence": "0%",

            "sources": []

        }




    except Exception as e:

        print("FACT VERIFICATION ERROR:", e)

        return {

            "status": "error",

            "claim": claim,

            "verdict": "Insufficient Evidence",

            "reason":
            "Unable to verify this claim because the external verification service is temporarily unavailable.",

            "confidence": "0%",

            "sources": []

        }