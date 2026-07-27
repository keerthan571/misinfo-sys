import os
import json

from groq import Groq
from dotenv import load_dotenv


load_dotenv()


groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



class NLPService:


    def normalize_confidence(self, value):

        try:

            value = str(value).replace("%", "")

            value = int(value)

            value = max(0, min(value, 100))

            return f"{value}%"

        except:

            return "0%"





    def analyze_text(self, text: str):

        try:


            if not text or len(text.strip()) < 5:

                return {

                    "status": "error",

                    "message": "Invalid text."

                }






            prompt = f"""

You are an NLP analysis engine for an AI misinformation detection system.


Your job:

- Understand the content.
- Extract the main claim.
- Prepare information for verification.
- Detect suspicious language patterns.


You are NOT a fact checker.

You must NOT decide absolute truth.

Do not use outside knowledge.

Analyze only the given text.



CONTENT:

"{text}"




Return the following fields:





1. CLASSIFICATION

Choose:

- Likely Reliable
- Needs Verification
- Potential Misinformation




2. CONFIDENCE

Return percentage.

This represents NLP analysis confidence only,
not truth accuracy.





3. CLAIM EXTRACTION

Extract the main claim that requires verification.
If information is unavailable, return "Unknown".
Do not invent information.
For lists (entities, keywords, manipulation signals), return [] when nothing is detected.





4. CLAIM TYPE

Choose:

- Scientific Claim
- Health Claim
- Political Claim
- Financial Claim
- Event Claim
- Social Claim
- Opinion
- Prediction
- Other





5. DOMAIN

Choose:

- Health
- Politics
- Science
- Technology
- Finance
- Crime
- Entertainment
- General
- Other





6. CONTENT STYLE

Choose:

- News
- Social Media Post
- Viral Forward
- Article
- Advertisement
- Opinion
- Other





7. ENTITY EXTRACTION

Extract:

- Person
- Organization
- Location
- Event
- Date
- Product


Format:


[
 {{
 "name":"",
 "type":""
 }}
]





8. KEYWORD EXTRACTION

Extract important search keywords
for verification.


Format:


[
"keyword1",
"keyword2"
]





9. LANGUAGE

Choose:

- English
- Hindi
- Kannada
- Tamil
- Mixed
- Unknown





10. TIME CONTEXT

Choose:

- Past
- Present
- Future
- Unknown





11. MANIPULATION SIGNALS

Return only detected signals.


Allowed:

- Clickbait wording detected
- Urgency language detected
- Fear appeal detected
- Extreme claim detected
- Share bait detected
- False authority wording detected
- Missing context detected


If nothing detected:

[]





12. VERIFICATION PRIORITY

Choose:

- High
- Medium
- Low


Based on whether external verification is required.





13. SIMILAR CLAIM

Return:

true

if the content appears similar to repeated misinformation patterns.

Otherwise:

false





Return ONLY JSON.

No explanation.

No markdown.

No extra fields.



FORMAT:


{{
"classification":"Needs Verification",

"confidence":"90%",

"claim":"",

"claim_type":"",

"domain":"",

"content_style":"",

"entities":[],

"keywords":[],

"language":"English",

"time_context":"Unknown",

"manipulation_signals":[],

"verification_priority":"Medium",

"similar_claim":false

}}


Rules:

- Every field is mandatory.
- Use "Unknown" when a value cannot be determined.
- Use empty array [] when no entities, keywords, or manipulation signals exist.
- Return valid JSON only.

"""
            response = groq_client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                temperature=0,

                messages=[

                    {
                        "role": "system",
                        "content":
                        "You are a professional NLP misinformation analysis engine."
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ]

            )



            output = response.choices[0].message.content.strip()



            output = (

                output

                .replace("```json", "")

                .replace("```", "")

                .strip()

            )



            result = json.loads(output)





            # ---------- Normalize Fields ----------


            result["classification"] = result.get(

                "classification",

                "Needs Verification"

            )


            result["confidence"] = self.normalize_confidence(

                result.get(

                    "confidence",

                    "0"

                )

            )


            result["claim"] = result.get(
                "claim",
                "Unknown"
            )



            result["claim_type"] = result.get(

                "claim_type",

                "Other"

            )



            result["domain"] = result.get(

                "domain",

                "General"

            )



            result["content_style"] = result.get(

                "content_style",

                "Other"

            )



            result["language"] = result.get(

                "language",

                "Unknown"

            )



            result["time_context"] = result.get(

                "time_context",

                "Unknown"

            )
            result["verification_priority"] = result.get(
                "verification_priority",
                "Medium"
            )


            result["similar_claim"] = result.get(
                "similar_claim",
                False
            )





            # ---------- Clean Entities ----------


            entities = result.get(

                "entities",

                []

            )


            clean_entities = []



            if isinstance(entities, list):

                for entity in entities:


                    if isinstance(entity, dict):

                        clean_entities.append({

                            "name": entity.get(

                                "name",

                                ""

                            ),

                            "type": entity.get(

                                "type",

                                "Unknown"

                            )

                        })


                    elif isinstance(entity, str):

                        clean_entities.append({

                            "name": entity,

                            "type": "Unknown"

                        })






            # ---------- Keywords ----------


            keywords = result.get(

                "keywords",

                []

            )


            if not isinstance(keywords, list):

                keywords = []






            # ---------- Manipulation Signals ----------


            manipulation_signals = result.get(

                "manipulation_signals",

                []

            )


            if not isinstance(manipulation_signals, list):

                manipulation_signals = []







            return {


                "status": "success",


                "text_analyzed": text,



                "classification":

                result.get(

                    "classification",

                    "Needs Verification"

                ),



                "confidence":

                result.get(

                    "confidence",

                    "0%"

                ),



                "claim": result.get(
                    "claim",
                    "Unknown"
                ),



                "claim_type":

                result.get(

                    "claim_type",

                    "Other"

                ),



                "domain":

                result.get(

                    "domain",

                    "General"

                ),



                "content_style":

                result.get(

                    "content_style",

                    "Other"

                ),



                "entities":

                clean_entities,



                "keywords":

                keywords,



                "language":

                result.get(

                    "language",

                    "Unknown"

                ),



                "time_context":

                result.get(

                    "time_context",

                    "Unknown"

                ),



                "manipulation_signals":

                manipulation_signals,



                "verification_priority":

                result.get(

                    "verification_priority",

                    "Medium"

                ),



                "similar_claim":

                bool(

                    result.get(

                        "similar_claim",

                        False

                    )

                )


            }







        except json.JSONDecodeError:


            return {


                "status": "error",


                "message":

                "Invalid JSON response from NLP model."

            }







        except Exception as e:


            return {


                "status": "error",


                "message": str(e)

            }








nlp_service = NLPService()