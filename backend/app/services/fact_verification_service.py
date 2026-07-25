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

                "status":"error",

                "claim":claim,

                "verdict":"Uncertain",

                "reason":
                "Invalid claim provided.",

                "confidence":"0%",

                "sources":[]

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

                "status":"success",

                "claim":claim,

                "verdict":"Uncertain",

                "reason":
                "No reliable evidence found from available sources.",

                "confidence":"0%",

                "sources":[]

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
            )


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
        # Groq Prompt
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
- If evidence supports claim return True.
- If evidence contradicts claim return False.
- If partially correct return Misleading.
- If insufficient evidence return Uncertain.


Return ONLY JSON.


Format:


{{
"verdict":"True",
"reason":"Short explanation",
"confidence":"90%"
}}

"""







        response = groq_client.chat.completions.create(


            model="llama-3.3-70b-versatile",


            temperature=0,


            messages=[


                {


                    "role":"system",


                    "content":
                    "You are a strict fact checking AI."


                },


                {


                    "role":"user",


                    "content":prompt


                }


            ]

        )







        output = response.choices[0].message.content.strip()






        if not output:


            return {

                "status":"error",

                "claim":claim,

                "verdict":"Uncertain",

                "reason":
                "Empty AI response received.",

                "confidence":"0%",

                "sources":sources

            }







        # remove markdown

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
                "Uncertain"
            )

            .strip()

            .title()

        )




        allowed = [

            "True",

            "False",

            "Misleading",

            "Uncertain"

        ]



        if verdict not in allowed:

            verdict = "Uncertain"







        confidence = str(

            result.get(

                "confidence",

                "0%"

            )

        )



        if not confidence.endswith("%"):

            confidence += "%"








        return {


            "status":"success",


            "claim":claim,


            "verdict":verdict,


            "reason":

            result.get(

                "reason",

                "No explanation available."

            ),


            "confidence":confidence,


            "sources":sources


        }









    except json.JSONDecodeError:


        return {


            "status":"error",


            "claim":claim,


            "verdict":"Uncertain",


            "reason":
            "Invalid JSON returned by AI model.",


            "confidence":"0%",


            "sources":[]


        }





    except Exception as e:


        return {


            "status":"error",


            "claim":claim,


            "verdict":"Uncertain",


            "reason":str(e),


            "confidence":"0%",


            "sources":[]


        }