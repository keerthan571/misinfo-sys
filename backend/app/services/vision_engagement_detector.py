import os
import json

from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise Exception("GEMINI_API_KEY missing")


genai.configure(
    api_key=api_key
)



class VisionEngagementDetector:


    def __init__(self):

        self.model = genai.GenerativeModel(
            "gemini-2.0-flash-lite"
        )



    def _clean_json(self,text):

        if not text:
            return {
                "post_text":"",
                "engagement":{}
            }


        text=text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()


        if "{" in text and "}" in text:

            text=text[
                text.find("{"):
                text.rfind("}")+1
            ]


        return json.loads(text)



    def analyze(
        self,
        image,
        platform
    ):


        prompt=f"""

You are a vision AI model for social media screenshot analysis.

Platform:
{platform}


Analyze the screenshot.

Return ONLY JSON.


Extract post text:
- headline
- main text
- visible caption


Ignore:
- usernames
- profile names
- dates
- hashtags
- follower counts


Extract engagement ONLY from icons.

Instagram:
Heart icon = likes
Comment icon = comments
Repost icon = reposts
Share icon = shares
Bookmark icon = bookmarks


Facebook:
Reaction icon = reactions
Comment icon = comments
Share icon = shares


Twitter/X:
Like icon = likes
Reply icon = replies
Repost icon = reposts
Bookmark icon = bookmarks


STRICT:

- Do not read numbers inside image content.
- Do not read dates.
- Do not read follower counts.
- Do not guess.
- Missing values = 0.


Convert:
42.4K -> 42400
426K -> 426000
1.5M -> 1500000


Return exactly:

{{
"post_text":"",
"engagement":{{
"likes":0,
"comments":0,
"reposts":0,
"shares":0,
"bookmarks":0
}}
}}

"""



        try:


            response = self.model.generate_content(

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



            result = self._clean_json(
                response.text
            )



            print(
                "========== FINAL VISION OUTPUT =========="
            )


            print(
                json.dumps(
                    result,
                    indent=2
                )
            )


            print(
                "=========================================="
            )



            return result



        except Exception as e:


            print(
                "VISION ERROR:",
                e
            )


            return {

                "post_text":"",

                "engagement":{}

            }



vision_engagement_detector = VisionEngagementDetector()