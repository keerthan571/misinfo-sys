import json

from dotenv import load_dotenv
import google.generativeai as genai



load_dotenv()


api_key = None


import os

api_key = os.getenv(
    "GEMINI_API_KEY"
)



if not api_key:

    raise Exception(
        "GEMINI_API_KEY missing"
    )



genai.configure(
    api_key=api_key
)






class VisionEngagementDetector:



    def __init__(self):


        self.model = genai.GenerativeModel(
            "gemini-2.0-flash-lite"
        )







    def _clean_json(
        self,
        text
    ):


        if not text:

            return {

                "post_text":""

            }



        text=text.replace(
            "```json",
            ""
        )


        text=text.replace(
            "```",
            ""
        )


        text=text.strip()



        if "{" in text and "}" in text:


            text=text[
                text.find("{"):
                text.rfind("}")+1
            ]



        return json.loads(
            text
        )









    def analyze(
        self,
        image,
        platform
    ):



        prompt=f"""

You are a social media screenshot analysis AI.


Platform:
{platform}



Analyze only the screenshot.


Extract:

1. Post text:
- headline
- caption
- visible content


Ignore:

- username
- profile name
- dates
- follower counts
- unrelated numbers inside image



IMPORTANT:

Do NOT extract engagement numbers.

Engagement numbers are handled separately by icon detection.



Return ONLY JSON.



Required format:



{{
"post_text":""
}}



"""




        try:



            response=self.model.generate_content(

                [

                    prompt,

                    image

                ],


                generation_config={


                    "temperature":0,


                    "response_mime_type":
                    "application/json"


                }

            )



            result=self._clean_json(
                response.text
            )



            print(
                "========== GEMINI TEXT OUTPUT =========="
            )


            print(
                json.dumps(
                    result,
                    indent=2
                )
            )


            print(
                "========================================="
            )



            return result






        except Exception as e:



            print(
                "VISION ERROR:",
                e
            )



            return {


                "post_text":""

            }






vision_engagement_detector = VisionEngagementDetector()