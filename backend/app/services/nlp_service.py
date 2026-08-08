import re
import os
import json
from dotenv import load_dotenv
from groq import Groq
import spacy


load_dotenv()


groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# Transformer NER model
nlp_model = spacy.load("en_core_web_trf")



class NLPService:


    def extract_entities(self, text):

        doc = nlp_model(text)

        entities = []


        entity_map = {

            "PERSON": "Person",
            "GPE": "Location",
            "LOC": "Location",
            "ORG": "Organization",
            "EVENT": "Event",
            "DATE": "Date",
            "MONEY": "Money",
            "PRODUCT": "Product"

        }


        seen = set()



        known_entities = {

            "bcci": "Organization",
            "icc": "Organization",
            "fifa": "Organization",
            "rvcj": "Organization",
            "google": "Organization",
            "openai": "Organization",
            "chatgpt": "Product",
            "instagram": "Organization",
            "facebook": "Organization",
            "twitter": "Organization",
            "youtube": "Organization"

        }



        special_entities = {

            "adipurush": "Product",
            "ramayana": "Event",
            "voldemort": "Person"

        }



        lower_text = text.lower()



        # Known organizations/products

        for name, label in known_entities.items():

            if name in lower_text:

                display = (
                    name.upper()
                    if name in [
                        "bcci",
                        "icc",
                        "fifa",
                        "rvcj"
                    ]
                    else name.title()
                )


                entities.append(
                    {
                        "name": display,
                        "type": label
                    }
                )


                seen.add(name)



        # Special corrections

        for name, label in special_entities.items():

            if name in lower_text:

                entities.append(
                    {
                        "name": name.title(),
                        "type": label
                    }
                )

                seen.add(name)



        ignored_words = {

            "vs",
            "the",
            "and",
            "new",
            "live",
            "today",
            "match",
            "test",
            "odi",
            "t20",
            "day",
            "this",
            "four",
            "nz"

        }



        for ent in doc.ents:


            value = ent.text.strip()

            value_lower = value.lower()



            if ent.label_ not in entity_map:
                continue



            if len(value) < 3:
                continue



            if value_lower in ignored_words:
                continue



            if value_lower in seen:
                continue



            if re.search(r"\d", value):
                continue



            if value.startswith("@"):
                continue



            # remove wrong detections

            if value_lower in {

                "maiden odi",
                "this day",
                "vs nz",
                "odi"

            }:

                continue




            # Acronym correction

            if value.isupper() and len(value) <= 6:

                final_type = "Organization"

            else:

                final_type = entity_map[ent.label_]



            entities.append(

                {
                    "name": value,
                    "type": final_type
                }

            )


            seen.add(value_lower)



        return entities[:10]





    def analyze_text(self, text):


        if not text or len(text.strip()) < 5:


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




        prompt = f"""

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

- Extract only main factual claim.
- Ignore opinions and emotions.
- Identify claim type:
Political, Financial, Health, Sports, Technology, Entertainment, General.
- Extract important keywords.
- Detect misinformation risk.
- Normal news should not automatically be misinformation.
- Confidence 0-100.
- Risk score 0-100.
- No markdown.

"""



        try:


            response = groq_client.chat.completions.create(

                model="llama-3.1-8b-instant",

                temperature=0,

                max_tokens=700,

                messages=[

                    {
                        "role":"system",
                        "content":
                        "You are an expert NLP misinformation analysis system."
                    },

                    {
                        "role":"user",
                        "content":prompt
                    }

                ]

            )



            output = response.choices[0].message.content.strip()



            output = (
                output
                .replace("```json","")
                .replace("```","")
                .strip()
            )



            result = json.loads(output)



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

                "confidence":float(
                    result.get(
                        "confidence",
                        0
                    )
                ),

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

                "entities":self.extract_entities(text),


                "manipulation_signals":result.get(
                    "manipulation_signals",
                    []
                )

            }



        except Exception as e:


            print(
                "NLP ERROR:",
                e
            )


            return {

                "status":"error",
                "claim":text[:200],
                "claim_type":"General",
                "prediction":"Needs Verification",
                "confidence":50,
                "risk_score":0,
                "language":"English",
                "keywords":[],
                "entities":[],
                "manipulation_signals":[]

            }



nlp_service = NLPService()