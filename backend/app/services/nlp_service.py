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


# Lightweight NER model for production deployment
nlp_model = spacy.load("en_core_web_sm")


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

            entities.append(
                {
                    "name": value,
                    "type": entity_map[ent.label_]
                }
            )

            seen.add(value_lower)

        return entities[:10]


    # ==========================================================
    # ROBUST JSON PARSER
    # ==========================================================

    def parse_json_response(self, output):

        # Remove markdown code fences if present
        cleaned = (
            output
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        # First try parsing the complete response
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Extract the JSON object from surrounding text
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start != -1 and end != -1 and end > start:

            json_text = cleaned[start:end + 1]

            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Could not parse valid JSON from model response: {cleaned[:300]}"
        )


    def analyze_text(self, text):

        if not text or len(text.strip()) < 5:

            return {

                "status": "error",
                "claim": "Unknown",
                "claim_type": "Unknown",
                "prediction": "Needs Verification",
                "confidence": 0,
                "risk_score": 0,
                "keywords": [],
                "entities": [],
                "language": "Unknown",
                "manipulation_signals": []

            }


        prompt = f"""
Analyze this social media content for misinformation risk.

Text:
{text[:2000]}

Return ONLY one valid JSON object.

IMPORTANT:
- Do not include markdown.
- Do not include ```json.
- Do not include explanations before or after the JSON.
- All JSON strings must be properly closed.
- Return every field shown below.

Format:

{{
  "claim": "main factual claim",
  "claim_type": "Political",
  "prediction": "Misinformation",
  "confidence": 0,
  "risk_score": 0,
  "language": "English",
  "keywords": [],
  "manipulation_signals": []
}}

Rules:

- Extract only the main factual claim.
- Ignore opinions and emotions.
- claim_type must be one of:
  Political, Financial, Health, Sports, Technology,
  Entertainment, General.
- prediction must be exactly one of:
  Misinformation, Not Misinformation, Needs Verification.
- Extract important keywords.
- Detect misinformation risk.
- Normal news should not automatically be misinformation.
- Confidence must be a number from 0 to 100.
- Risk score must be a number from 0 to 100.
- No markdown.
"""


        try:

            response = groq_client.chat.completions.create(

                model="openai/gpt-oss-20b",

                temperature=0,

                max_tokens=700,

                messages=[

                    {
                        "role": "system",
                        "content": (
                            "You are an expert NLP misinformation analysis "
                            "system. Follow the requested JSON format exactly. "
                            "Return valid JSON only."
                        )
                    },

                    {
                        "role": "user",
                        "content": prompt
                    }

                ]

            )


            output = response.choices[0].message.content.strip()


            # Use robust parser
            result = self.parse_json_response(output)


            return {

                "status": "success",

                "claim": result.get(
                    "claim",
                    "Unknown"
                ),

                "claim_type": result.get(
                    "claim_type",
                    "General"
                ),

                "prediction": result.get(
                    "prediction",
                    "Needs Verification"
                ),

                "confidence": float(
                    result.get(
                        "confidence",
                        0
                    )
                ),

                "risk_score": int(
                    result.get(
                        "risk_score",
                        0
                    )
                ),

                "language": result.get(
                    "language",
                    "English"
                ),

                "keywords": result.get(
                    "keywords",
                    []
                ),

                "entities": self.extract_entities(text),

                "manipulation_signals": result.get(
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

                "status": "error",
                "claim": text[:200],
                "claim_type": "General",
                "prediction": "Needs Verification",
                "confidence": 50,
                "risk_score": 0,
                "language": "English",
                "keywords": [],
                "entities": [],
                "manipulation_signals": []

            }


nlp_service = NLPService()