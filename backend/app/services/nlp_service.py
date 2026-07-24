import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class NLPService:

    def analyze_text(self, text: str):

        try:

            if not text or len(text.strip()) < 5:
                return {
                    "status": "error",
                    "message": "Please enter valid text."
                }


            prompt = f"""
You are an AI misinformation detection expert.

Analyze the following text:

"{text}"

Decide whether the content is:
- Fake
- Real
- Misleading
- Uncertain

Return ONLY valid JSON.

Format:

{{
    "prediction": "Fake",
    "confidence": "90%",
    "reason": "Explain in 2-3 lines."
}}

Rules:
- Do not return markdown.
- Do not add extra text.
- Return only JSON.
"""


            response = groq_client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                temperature=0,

                messages=[
                    {
                        "role": "system",
                        "content":
                        "You are an expert AI misinformation detector."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

            )


            content = response.choices[0].message.content.strip()


            # Remove markdown if returned
            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )


            result = json.loads(content)


            return {

                "status": "success",

                "text_analyzed": text,

                "prediction":
                    result.get(
                        "prediction",
                        "Uncertain"
                    ),

                "confidence":
                    result.get(
                        "confidence",
                        "0%"
                    ),

                "reason":
                    result.get(
                        "reason",
                        ""
                    )

            }


        except json.JSONDecodeError:

            return {
                "status": "error",
                "message": "Invalid JSON received from Groq."
            }


        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }



nlp_service = NLPService()