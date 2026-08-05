import re
import os
import json
from dotenv import load_dotenv
from groq import Groq
import spacy

load_dotenv()

groq_client=Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

nlp_model=spacy.load("en_core_web_sm")

class NLPService:

    def extract_entities(self,text):

        doc=nlp_model(text)

        entities=[]

        entity_map={
            "PERSON":"Person",
            "GPE":"Location",
            "LOC":"Location",
            "ORG":"Organization",
            "EVENT":"Event",
            "DATE":"Date",
            "MONEY":"Money",
            "PRODUCT":"Product"
        }

        allowed=[
            "PERSON",
            "GPE",
            "LOC",
            "ORG",
            "EVENT",
            "DATE",
            "MONEY",
            "PRODUCT"
        ]

        seen=set()

        for ent in doc.ents:

            value=ent.text.strip()

            if ent.label_ not in allowed:
                continue

            if len(value)<3:
                continue

            if value.isdigit():
                continue

            if value.lower() in seen:
                continue

            if re.match(r"^[0-9%$.,]+$",value):
                continue

            entities.append(
                {
                    "name":value,
                    "type":entity_map.get(
                        ent.label_,
                        "Other"
                    )
                }
            )

            seen.add(value.lower())

        return entities[:10]


    def analyze_text(self,text):

        if not text or len(text.strip())<5:
            return {
                "status":"error",
                "claim":"Unknown",
                "claim_type":"Unknown",
                "prediction":"Needs Verification",
                "confidence":0,
                "risk_score":0,
                "keywords":[],
                "entities":[],
                "language":"Unknown",
                "manipulation_signals":[]
            }

        prompt=f"""
Analyze this social media content for misinformation risk.

Text:
{text[:2000]}

Return ONLY JSON.

Format:

{{
"claim":"",
"claim_type":"",
"prediction":"",
"confidence":0,
"risk_score":0,
"language":"",
"keywords":[],
"manipulation_signals":[]
}}

Rules:
- Extract only the main factual claim.
- Ignore opinions, greetings, praise and emotional words.
- Identify claim type:
Political, Financial, Health, Sports, Technology, Entertainment, General.
- Extract important keywords.
- Detect misinformation risk.
- Normal news, announcements and factual statements should not automatically be misinformation.
- Emotional appeal only for fear, hate, panic, outrage or threatening language.
- Confidence must be 0-100.
- Risk score must be 0-100.
- Do not return markdown.
"""

        try:

            response=groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0,
                max_tokens=700,
                messages=[
                    {
                        "role":"system",
                        "content":"You are an expert NLP misinformation analysis system."
                    },
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )

            output=response.choices[0].message.content.strip()

            output=output.replace("```json","").replace("```","").strip()

            result=json.loads(output)

            entities=self.extract_entities(text)

            confidence=float(
                result.get(
                    "confidence",
                    0
                )
            )

            if confidence<50 and result.get("claim"):
                confidence=85


            signals=result.get(
                "manipulation_signals",
                []
            )

            filtered=[]

            text_lower=text.lower()

            emotional_words=[
                "shocking",
                "urgent",
                "panic",
                "terror",
                "war",
                "attack",
                "destroy",
                "kill",
                "danger",
                "traitor",
                "scandal",
                "fraud",
                "exposed"
            ]

            for signal in signals:

                if signal.lower()=="emotional appeal":

                    if any(
                        word in text_lower
                        for word in emotional_words
                    ):
                        filtered.append(
                            "Emotional appeal"
                        )

                elif signal.lower()=="lack of credible sources":

                    if len(text.split())<25:
                        filtered.append(
                            "Lack of credible sources"
                        )

                else:
                    filtered.append(signal)


            return {
                "status":"success",
                "claim":result.get(
                    "claim",
                    "Unknown"
                ),
                "claim_type":result.get(
                    "claim_type",
                    "General"
                ),
                "prediction":result.get(
                    "prediction",
                    "Needs Verification"
                ),
                "confidence":confidence,
                "risk_score":int(
                    result.get(
                        "risk_score",
                        0
                    )
                ),
                "language":result.get(
                    "language",
                    "English"
                ),
                "keywords":result.get(
                    "keywords",
                    []
                ),
                "entities":entities,
                "manipulation_signals":filtered
            }

        except Exception as e:

            print("NLP ERROR:",e)

            return {
                "status":"error",
                "claim":text[:200],
                "claim_type":"General",
                "prediction":"Needs Verification",
                "confidence":50,
                "risk_score":0,
                "language":"English",
                "keywords":text.split()[:5],
                "entities":[],
                "manipulation_signals":[]
            }

nlp_service=NLPService()