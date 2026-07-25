import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



class NLPService:


    def correct_temporal_context(self, text, model_result):

        text_lower = text.lower()


        future_patterns = [
            "will",
            "going to",
            "expected",
            "predicted",
            "upcoming",
            "next year",
            "next month",
            "soon"
        ]


        past_patterns = [
            "won",
            "defeated",
            "launched",
            "released",
            "completed",
            "announced",
            "happened",
            "finished",
            "was",
            "were"
        ]


        present_patterns = [
            "currently",
            "today",
            "now",
            "is happening",
            "are happening"
        ]



        has_future = any(
            word in text_lower
            for word in future_patterns
        )


        has_past = any(
            word in text_lower
            for word in past_patterns
        )


        has_present = any(
            word in text_lower
            for word in present_patterns
        )



        # Future has priority if future action exists
        if has_future:

            return "Future Event"


        if has_past:

            return "Past Event"


        if has_present:

            return "Present Event"


        # General statements
        if model_result in [
            "Timeless",
            "Unknown"
        ]:

            return model_result


        return model_result





    def analyze_text(self, text: str):

        try:


            if not text or len(text.strip()) < 5:

                return {
                    "status":"error",
                    "message":"Please enter valid text."
                }



            prompt = f"""

You are an advanced NLP Content Intelligence Engine
for an AI misinformation analysis system.


Analyze ONLY language structure,
content type, claim style and risk patterns.


TEXT:

"{text}"


IMPORTANT:

You are NOT a fact checker.

Never decide:

True
False
Fake
Real


Fact verification is handled separately.



Analyze:


1. CONTENT TYPE

Choose:

News Article
Social Media Post
Viral Forward
Rumor
Opinion
Prediction
Announcement
Advertisement
Other



2. CLAIM TYPE

Choose:

Factual Statement
Event Claim
Future Prediction
Opinion
Allegation
Question
Other



3. TEMPORAL CONTEXT

Choose:

Past Event
Present Event
Future Event
Timeless
Unknown



Understand complete meaning.

Do not depend only on keywords.



4. NLP RISK ANALYSIS


Check:

- Clickbait
- Sensational words
- Fear
- Anger
- Urgency
- Emotional manipulation
- Share requests
- Extreme claims
- Conspiracy language
- Missing context



Risk:

Low
Medium
High



Risk score:

0-100



5. LANGUAGE

Choose:

English
Hindi
Kannada
Tamil
Mixed
Unknown



6. ENTITIES

Extract:

Person
Organization
Location
Event
Product



7. INDICATORS

Examples:

Neutral language
Specific event mentioned
Emotional wording
Urgency detected
Clickbait pattern
Share request
Strong claim
No suspicious pattern



Return only JSON.


FORMAT:


{{
"prediction":"Normal",
"confidence":"90%",
"language":"English",
"content_type":"News Article",
"claim_type":"Event Claim",
"temporal_context":"Past Event",
"risk_level":"Low",
"risk_score":10,

"entities":[],

"indicators":[],

"reason":"Short NLP explanation"
}}


Rules:

- Never fact check.
- Never use external knowledge.
- Never judge truth.
- Analyze only text characteristics.
- Return JSON only.

"""



            response = groq_client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                temperature=0,

                messages=[

                    {
                        "role":"system",
                        "content":
                        "You are a professional NLP content intelligence analyzer."
                    },

                    {
                        "role":"user",
                        "content":prompt
                    }

                ]

            )



            content = response.choices[0].message.content.strip()


            content = (
                content
                .replace("```json","")
                .replace("```","")
                .strip()
            )



            result = json.loads(content)



            # Fix temporal mistakes
            result["temporal_context"] = self.correct_temporal_context(
                text,
                result.get(
                    "temporal_context",
                    "Unknown"
                )
            )



            confidence = str(
                result.get(
                    "confidence",
                    "0%"
                )
            )


            if not confidence.endswith("%"):

                confidence += "%"



            try:

                risk_score = int(
                    result.get(
                        "risk_score",
                        0
                    )
                )

            except:

                risk_score = 0





            return {

                "status":"success",

                "text_analyzed":text,


                "prediction":
                result.get(
                    "prediction",
                    "Normal"
                ),


                "confidence":
                confidence,


                "language":
                result.get(
                    "language",
                    "Unknown"
                ),


                "content_type":
                result.get(
                    "content_type",
                    "Other"
                ),


                "claim_type":
                result.get(
                    "claim_type",
                    "Other"
                ),


                "temporal_context":
                result.get(
                    "temporal_context",
                    "Unknown"
                ),


                "risk_level":
                result.get(
                    "risk_level",
                    "Low"
                ),


                "risk_score":
                risk_score,


                "entities":
                result.get(
                    "entities",
                    []
                ),


                "indicators":
                result.get(
                    "indicators",
                    []
                ),


                "reason":
                result.get(
                    "reason",
                    ""
                )

            }



        except json.JSONDecodeError:


            return {

                "status":"error",

                "message":
                "Invalid JSON received from NLP model."

            }



        except Exception as e:


            return {

                "status":"error",

                "message":str(e)

            }





nlp_service = NLPService()