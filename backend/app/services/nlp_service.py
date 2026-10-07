import json
import logging
import os
import re


from dotenv import load_dotenv
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

class NLPService:

    @staticmethod
    def extract_json_response(output):
        if not output or not output.strip():
            raise ValueError("Empty AI response.")

        cleaned = (
            output
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        try:
            result = json.loads(cleaned)

            if not isinstance(result, dict):
                raise ValueError("AI response is not a JSON object.")

            return result

        except json.JSONDecodeError:
            pass

        match = re.search(r"\{[\s\S]*\}", cleaned)

        if not match:
            raise ValueError("No JSON object found in AI response.")

        result = json.loads(match.group(0))

        if not isinstance(result, dict):
            raise ValueError(
                "Extracted AI response is not a JSON object."
            )

        return result

    @staticmethod
    def clamp_number(value, minimum, maximum, default=0):
        try:
            number = float(value)
            return max(minimum, min(maximum, number))
        except (TypeError, ValueError):
            return default

    def is_question_only(self, text):
        """
        Detect content that consists only of questions / question-like
        prompts, without any factual assertion.

        Examples:

            "Why did this happen?"
                -> True

            "What is the reason for this?"
                -> True

            "Why did this happen?\nThey changed the policy yesterday."
                -> False

            "Why did this happen? The policy changed yesterday."
                -> False

            "Answer the real questions!"
                -> True (non-factual instruction)

        Important:
        A post containing at least one clear factual/assertive sentence
        must NOT be classified as question-only.
        """

        if not text:
            return False

        text = str(text).strip()

        if not text:
            return False

        # ---------------------------------------------------------
        # NORMALIZE WHITESPACE
        # ---------------------------------------------------------

        normalized = re.sub(r"\s+", " ", text).strip()

        if not normalized:
            return False

        # ---------------------------------------------------------
        # SPLIT INTO SENTENCE-LIKE UNITS
        # ---------------------------------------------------------
        #
        # We intentionally keep this simple.
        # The translated NLP text may contain:
        #
        #   ?
        #   !
        #   .
        #   ...
        #
        # We do NOT want one question to hide a factual statement
        # elsewhere in the post.
        # ---------------------------------------------------------

        parts = re.split(
            r"(?<=[?!।])\s+|(?<=[.!?])\s*(?=\n)",
            text
        )

        sentences = []

        for part in parts:
            part = re.sub(r"\s+", " ", part).strip()

            if part:
                sentences.append(part)

        if not sentences:
            return False

        # ---------------------------------------------------------
        # QUESTION STARTERS
        # ---------------------------------------------------------

        question_starters = (
            "who ",
            "what ",
            "when ",
            "where ",
            "why ",
            "how ",
            "which ",
            "whose ",
            "whom ",
            "is ",
            "are ",
            "am ",
            "was ",
            "were ",
            "do ",
            "does ",
            "did ",
            "can ",
            "could ",
            "will ",
            "would ",
            "should ",
            "has ",
            "have ",
            "had ",
            "may ",
            "might ",
            "shall ",
        )

        # ---------------------------------------------------------
        # NON-ASSERTIVE / INSTRUCTIONAL STARTERS
        # ---------------------------------------------------------
        #
        # These are not factual claims.
        #
        # Example:
        # "Answer the real questions, Anna!"
        #
        # This should not turn a question-only post into a factual
        # claim.
        # ---------------------------------------------------------

        non_assertive_starters = (
            "answer ",
            "please answer ",
            "tell me ",
            "tell us ",
            "explain ",
            "please explain ",
            "look at ",
            "see ",
            "consider ",
            "listen ",
            "check ",
        )

        has_question = False
        has_assertion = False

        # ---------------------------------------------------------
        # ANALYZE EACH SENTENCE
        # ---------------------------------------------------------

        for sentence in sentences:

            sentence_normalized = (
                sentence.strip().lower()
            )

            if not sentence_normalized:
                continue

            # ---------------------------------------------
            # Explicit question mark
            # ---------------------------------------------

            if "?" in sentence:
                has_question = True
                continue

            # ---------------------------------------------
            # Question-like grammatical starter
            # ---------------------------------------------

            if sentence_normalized.startswith(
                question_starters
            ):
                has_question = True
                continue

            # ---------------------------------------------
            # Instruction / imperative
            # ---------------------------------------------

            if sentence_normalized.startswith(
                non_assertive_starters
            ):
                continue

            # ---------------------------------------------
            # Everything else is potentially an assertion.
            #
            # This is the important part.
            #
            # If we have:
            #
            # "Why did this happen?"
            # "The policy changed yesterday."
            #
            # the second sentence reaches here and causes:
            #
            # has_assertion = True
            #
            # Therefore the whole post is NOT question-only.
            # ---------------------------------------------

            has_assertion = True

        # ---------------------------------------------------------
        # FINAL DECISION
        # ---------------------------------------------------------

        if has_question and not has_assertion:
            print(
                "Simple question-only content detected - "
                "not a factual claim.",
                flush=True
            )
            return True

        return False
    
    @staticmethod
    def is_opinion_only(text):
        text = (text or "").strip().lower()

        opinion_starters = (
            "i think ",
            "i feel ",
            "i believe ",
            "in my opinion ",
            "imo ",
            "personally ",
            "i would say ",
            "i consider ",
        )

        return text.startswith(opinion_starters)
    def analyze_text(self, text):
        text = (text or "").strip()

        print("\n========== NLP TEXT RECEIVED ==========")
        print(repr(text))
        print("=======================================\n")

        # ============================================================
        # QUESTION HANDLING
        # ============================================================
        # Do NOT automatically classify a question as "Not a Factual Claim".
        #
        # A question can contain an implicit factual claim.
        # Example:
        # "Why do they not consume cow urine?"
        #
        # This is a question grammatically, but it contains an
        # assertion that "they do not consume cow urine".
        #
        # Therefore, questions must continue through the normal
        # claim-analysis pipeline.

        if self.is_question_only(text):
            print("Question detected - checking for implicit factual claim.")

    # DO NOT return here.
    # Allow the normal NLP/LLM claim analysis below to process it.
        if self.is_opinion_only(text):
            return {
                "status": "success",
                "claim": "",
                "claim_type": "Opinion",
                "prediction": "Not a Factual Claim",
                "confidence": 0,
                "risk_score": 0,
                "keywords": [],
                "language": "English",
                "manipulation_signals": [],
            }
        
        if len(text) < 5:
            return {
                "status": "error",
                "claim": "Unknown",
                "claim_type": "Unknown",
                "prediction": "Needs Verification",
                "confidence": None,
                "risk_score": None,
                "keywords": [],
                 
                "language": "Unknown",
                "manipulation_signals": [],
            }

        if not GROQ_API_KEY or not groq_client:
            logger.error("Groq is not configured.")

            return {
                "status": "error",
                "claim": text[:200],
                "claim_type": "General",
                "prediction": "Verification Unavailable",
                "confidence": None,
                "risk_score": None,
                "language": "Unknown",
                "keywords": [],
                "manipulation_signals": [],
            }

        prompt = f"""
Analyze the following submitted social-media content.

The submitted content may come from OCR of a screenshot.
Therefore, it may contain OCR errors, social-media interface
text, usernames, hashtags, engagement counts, publisher
information, unrelated text, and text in languages unrelated
to the main claim.

OCR / SUBMITTED TEXT:
{text[:2000]}

Your task is NLP analysis, NOT factual verification.

Do not decide whether a factual claim is true or false.
Do not use outside knowledge to determine whether the claim
is correct. Current events may have changed.

The separate Fact Verification module verifies factual claims
using external evidence.
IMPORTANT QUESTION AND ATTRIBUTION RULE:

- A standalone question is NOT automatically a factual assertion.

- If the submitted content is ONLY a question, with no attribution,
  context, or reported action, return:
    claim = ""
    prediction = "Not a Factual Claim"

- HOWEVER, social-media posts frequently contain questions that are
  part of a reported statement, quotation, interview, speech, or
  political/news report.

- If a question is explicitly attributed to a person, organization,
  speaker, journalist, politician, or other identifiable source,
  DO NOT discard the question.

- In such cases, extract the COMPLETE attributed statement as the
  claim.

- The claim MUST preserve:
    1. WHO made/asked the statement,
    2. WHO the statement was directed toward, if available,
    3. the COMPLETE question or statement,
    4. the surrounding context needed to understand it.

- NEVER convert an attributed question into a positive or negative
  factual assertion.

- For example:

  Content:
  "Why don't they consume cow urine? — Priyank Kharge"

  WRONG:
  claim = "They do not consume cow urine."

  CORRECT:
  claim = "Priyank Kharge asked why they do not consume cow urine."

- Another example:

  Content:
  "Why haven't you worn the uniform? Why aren't you consuming cow
  urine in the cow shed? Answer the real questions, Anna! — Priyank Kharge"

  WRONG:
  claim = "They do not consume cow urine."

  CORRECT:
  claim = "Priyank Kharge asked Ashok Anna why he had not worn the
  uniform and why he was not consuming cow urine in the cow shed,
  and asked him to answer the real questions."

- If the post contains a person attribution such as:
    "X asked Y..."
    "X said..."
    "X questioned Y..."
    "According to X..."
    "X stated..."
    "— X"
  preserve that attribution in the claim.

- When an attributed question contains multiple questions, preserve
  ALL of the important questions. Do not extract only one sentence.

- Do NOT transform a question into an assertion merely because the
  question contains words such as:
    "don't"
    "didn't"
    "why"
    "how"
    "not"
    "never"

- The claim should describe what was said or asked, not assume that
  the underlying proposition is true.

- Therefore, distinguish between:

  Standalone question:
  "Did X happen?"
  -> claim = ""
  -> prediction = "Not a Factual Claim"

  Attributed question:
  "Priyank Kharge asked Ashok Anna, 'Why did X happen?'"
  -> claim = "Priyank Kharge asked Ashok Anna why X happened."
  -> prediction = "Needs Verification"

  Reported statement:
  "Priyank Kharge said that X happened."
  -> claim = "Priyank Kharge said that X happened."
  -> prediction = "Needs Verification"
  
Your responsibilities:

1. Identify whether the submitted content contains at least
   one independently verifiable factual assertion.

2. If one or more factual assertions are present, identify the
   CENTRAL factual claim of the post.

   The central claim is the main proposition that the post is
   trying to establish, question, challenge, or communicate.

   Do NOT automatically select the first factual sentence.

    When several factual statements support one larger claim,
    combine them into one coherent central claim.

    IMPORTANT:
    Do NOT describe the social-media post itself as the subject
    of the claim.

    Do NOT introduce phrases such as:
    - "the post states that"
    - "the post claims that"
    - "the post says that"
    - "the content states that"
    - "the submitted post mentions that"
    - "according to the post"

    unless the original content explicitly makes the post itself
    the subject of the claim.

    Instead, express the actual proposition contained in the
    content directly.

    If the content attributes the statement to a named person,
    preserve that attribution naturally.

    For example, if the content says:

    "It takes 5 to 6 litres of milk to make 1 kg of paneer.
    Even at ₹60 per litre, the milk alone costs around ₹360.
    Adding processing and packaging, the price cannot be less
    than ₹400. Then how is paneer available for less than ₹200?

    — IAS Tukaram Mundhe"

    DO NOT extract:

    "IAS Tukaram Mundhe questioned how paneer could be sold
    below ₹200 when the post states that producing 1 kg of
    paneer requires 5 to 6 litres of milk..."

    Instead extract:

    "IAS Tukaram Mundhe questioned how paneer could be sold
    below ₹200, citing that producing 1 kg of paneer requires
    5 to 6 litres of milk costing approximately ₹300-₹360
    before processing and packaging."

    The extracted claim should describe the proposition itself,
    not the fact that it appeared in a post.

   For example, if a post says:

   "It takes 5 to 6 litres of milk to make 1 kg of paneer.
   Milk costs ₹60 per litre. Therefore the milk alone costs
   around ₹300-₹360, excluding processing and packaging.
   Then how is paneer available below ₹200?"

   The central claim should preserve the attribution:

    "IAS Tukaram Mundhe questioned how paneer could be sold below
    ₹200 when the post states that producing 1 kg of paneer requires
    5 to 6 litres of milk costing approximately ₹300-₹360 before
    processing and packaging."

    The attribution and question are important parts of the claim.
    Do not convert the question into the absolute factual assertion:

    "Paneer cannot be sold below ₹200."

    The NLP module should preserve what the person actually
    questioned or stated. The Fact Verification module will determine
    whether the attribution is supported by the retrieved evidence.

   Do NOT extract only:
   "It takes 5 to 6 litres of milk to make 1 kg of paneer."

   Do NOT extract only:
   "Milk costs ₹60 per litre."

   Do NOT extract only:
   "Paneer is available below ₹200."

   Those are supporting details.

   The extracted claim should represent the main factual
   proposition being communicated by the post.
   
ATTRIBUTION + SUPPORTING DETAILS:

When a named person is associated with a larger factual statement,
preserve the attribution naturally while keeping the supporting
details as part of the statement attributed to that person.

Use structures such as:

"[Person] questioned whether..."
"[Person] stated that..."
"[Person] claimed that..."
"[Person] reported that..."

The attributed statement may contain supporting factual details
when those details are clearly part of what the person is saying,
claiming, questioning, or reporting.

For example, if the content says:

"It takes 5 to 6 litres of milk to make 1 kg of paneer.
Milk costs ₹60 per litre. Therefore the milk alone costs
around ₹300-₹360. Adding processing and packaging costs,
the price cannot be less than ₹400. Then how is paneer
available for less than ₹200?

— IAS Tukaram Mundhe"

Prefer:

"IAS Tukaram Mundhe questioned how paneer could be sold for
less than ₹200, arguing that producing 1 kg of paneer requires
5 to 6 litres of milk costing approximately ₹300-₹360 before
processing and packaging."

Do NOT produce:

"IAS Tukaram Mundhe questioned how paneer could be sold below
₹200 when the post states that producing 1 kg of paneer requires
5 to 6 litres of milk costing approximately ₹300-₹360 before
processing and packaging."

Do NOT use phrases such as:
- "when the post states that..."
- "the post claims that..."
- "the post says that..."
- "according to the post..."

merely to connect supporting details to an attribution.

The social-media post is the evidence container. It is not
automatically part of the factual proposition.

IMPORTANT:
If the supporting details are clearly presented as part of the
named person's statement, question, claim, or report, preserve
them as part of the attributed proposition.

Do not add supporting details that are unrelated to what the
person actually said or that are not present in the submitted
content.

The extracted claim must distinguish between:
(a) what the named person said, questioned, claimed, or reported,
and
(b) whether the underlying factual proposition is actually true.

The verification module will separately determine whether the
underlying factual details are supported by evidence.

CLAIM EXTRACTION RULE FOR OCR:

The submitted text may contain OCR noise, UI elements,
hashtags, usernames, engagement counts, page names, and
unrelated text.

Before extracting the claim:

1. Ignore Instagram/Facebook/Twitter interface text.
2. Ignore engagement numbers such as likes, comments and shares.
3. Ignore usernames and hashtags unless they are necessary
   to identify an attribution.
4. Ignore obvious OCR corruption.
5. Identify the coherent textual passage containing the main
   factual proposition.
6. Preserve important numerical values when they are part of
   the central claim.
7. Do not invent missing values or silently correct uncertain
   OCR values.
8. Do not combine unrelated OCR fragments merely because they
   contain numbers.
9. If multiple sentences clearly form one argument, combine
   them into one central claim.
10. Keep the claim concise enough for external fact verification,
    but detailed enough that the verifier can search for the
    exact proposition being asserted.
11. If the coherent passage contains an attribution to a named
    person or organization, preserve the attribution in the claim.
12. If the attributed content is a question or rhetorical
    question, preserve it as a question or use "questioned how..."
    / "asked whether..." rather than turning it into a definitive
    factual assertion.
13. The named person is part of the claim when the post presents
    the statement as something said, asked, questioned, posted,
    written, or shared by that person.
14. Do not remove attribution merely because the underlying
    proposition is easier to search without it.
    
2A. QUESTIONS, ATTRIBUTIONS, AND RHETORICAL STATEMENTS

A question may contain an implicit factual proposition.

However, do NOT automatically convert a question into a factual
assertion.

First determine whether the post is primarily communicating:
(a) a factual assertion,
(b) a question/rhetorical question,
(c) an attribution of a statement/question to a person,
or (d) a combination of these.

SPECIAL RULE FOR ATTRIBUTION:

If the post explicitly attributes a statement, question, claim,
opinion, or remark to a named person or organization, PRESERVE
THAT ATTRIBUTION in the extracted claim.

Examples of attribution language include:

- "X said..."
- "X stated..."
- "X claimed..."
- "X questioned..."
- "X asked..."
- "X posted..."
- "X wrote..."
- "X shared..."
- "According to X..."
- "X questioned how..."
- "X asked why..."

Do NOT remove the named person and reduce the claim to only the
underlying proposition.

For example, if the post says:

"It takes 5 to 6 litres of milk to make 1 kg of paneer.
Milk costs ₹60 per litre. The milk alone costs around
₹300-₹360. Then how is paneer available below ₹200?
— IAS Tukaram Mundhe"

The extracted claim should preserve the attribution and the
central question, for example:

"IAS Tukaram Mundhe questioned how paneer could be sold below
₹200 when the post states that producing 1 kg of paneer requires
5 to 6 litres of milk costing approximately ₹300-₹360 before
processing and packaging."

Do NOT extract only:

"Producing 1 kg of paneer costs more than its selling price."

Do NOT extract only:

"Paneer cannot be sold below ₹200."

Those statements convert a question or attributed statement
into an independent factual assertion that the original post
did not necessarily make.

When an attribution is present, preserve the distinction between:

1. WHAT THE PERSON SAID, ASKED, CLAIMED, OR QUESTIONED
2. WHAT THE UNDERLYING PROPOSITION IS

The extracted claim should include the attribution when it is
material to understanding what the post is communicating.

If the post contains a rhetorical question attributed to a named
person, retain the wording as a question or use wording such as
"questioned how..." rather than converting it into a definitive
statement.

If the post contains both an attribution and independently stated
facts, combine them only when they clearly form one coherent
argument.

Do not invent an attribution that is not present in the submitted
content.

Do not assume that a person's question means that the person
asserted the proposition contained in that question.

The separate Fact Verification module will determine whether the
attribution is supported by evidence and, where relevant, whether
the underlying factual proposition is supported.

However, do not automatically treat every question as an
assertion.

If the question is rhetorical and clearly depends on factual
premises stated elsewhere in the same post, extract the central
factual proposition supported by those premises.

Preserve the distinction between:
- what the post explicitly claims,
- what the post asks,
- and what the post merely suggests.

Do not invent a factual conclusion that is not supported by
the submitted text.

3. If the content contains both non-factual content and factual
   assertions, extract the factual assertion rather than
   classifying the entire post as non-factual.

4. Classify the claim type.

5. Determine the language of the MAIN CLAIM.

6. Extract important keywords from the MAIN CLAIM.

7. Identify manipulation signals actually present in the
   submitted content.

8. Estimate linguistic/manipulation risk.

IMPORTANT LANGUAGE RULES:

- Determine language from the MAIN CLAIM, not from the entire
  OCR text.
- Ignore social-media UI text, usernames, hashtags,
  engagement numbers, publisher names, OCR artifacts,
  unrelated text, and unrelated multilingual text.
- First identify the MAIN factual claim.
- Then determine the language in which that MAIN claim is
  written.
- If the MAIN claim is entirely English, return "English".
- If the MAIN claim is entirely Hindi, return "Hindi".
- If the MAIN claim is entirely Kannada, return "Kannada".
- Return "Mixed" ONLY when the MAIN CLAIM itself genuinely
  contains two or more languages in a meaningful way.
- Do NOT return "Mixed" merely because unrelated OCR text
  contains another script or language.
- OCR noise or isolated words from another language must not
  cause the result to become "Mixed".

The language value MUST be exactly one of:
English
Hindi
Kannada
Mixed

Claim types must be exactly one of:
Political
Financial
Health
Sports
Technology
Entertainment
General

PREDICTION RULES:

- If the submitted content contains at least one independently
  verifiable factual assertion, prediction MUST be:
  "Needs Verification"

- If the submitted content contains no independently verifiable
  factual assertion, prediction MUST be:
  "Not a Factual Claim"

- A post does NOT become "Not a Factual Claim" merely because
  it also contains greetings, wishes, opinions, emotions,
  praise, criticism, questions, hashtags, or other non-factual
  content.

- If a post contains both emotional/non-factual content and a
  factual assertion, extract the factual assertion and return:
  "Needs Verification".

- Do not decide whether the factual assertion is true or false.
  That is the responsibility of the separate Fact Verification
  module.

Risk score:
0 = no meaningful linguistic/manipulation risk.
100 = very strong linguistic/manipulation signals.

Risk score must NOT represent factual truth.
Do not increase risk merely because a claim is unusual,
recent, future-dated, controversial, or unknown.

Confidence represents confidence in this NLP analysis only.
It is NOT the probability that the claim is true or false.

Possible manipulation signals include:
- sensational language
- excessive urgency
- fear appeal
- unsupported certainty
- fabricated authority
- emotionally manipulative wording
- conspiracy framing
- misleading calls to action

Only report a signal when supported by the submitted text.
EXAMPLES:

Example 1:

Content:
"Happy birthday! Wishing you health, happiness and success
always."

Result:
- claim = ""
- prediction = "Not a Factual Claim"

Reason:
The content contains only a birthday wish and no independently
verifiable factual assertion.


Example 2:

Content:
"Happy birthday! He has acted in more than 20 films and has
also directed several movies."

Result:
- claim = "He has acted in more than 20 films and has also
  directed several movies."
- prediction = "Needs Verification"

Reason:
The birthday greeting is non-factual, but the post contains
verifiable factual assertions.


Example 3:

Content:
"I think this is the greatest movie ever made."

Result:
- claim = ""
- prediction = "Not a Factual Claim"

Reason:
This is an opinion rather than an independently verifiable
factual assertion.


Example 4:

Content:
"The company announced a 20% increase in revenue this year."

Result:
- claim = "The company announced a 20% increase in revenue
  this year."
- prediction = "Needs Verification"

Reason:
This is a factual assertion that can be checked against
evidence.


Example 5:

Content:
"This medicine completely cures diabetes."

Result:
- claim = "This medicine completely cures diabetes."
- prediction = "Needs Verification"

Reason:
This is a factual/medical assertion requiring external
verification.


Example 6:

Content:
"Congratulations to the team! They won yesterday's match
by 7 wickets."

Result:
- claim = "The team won yesterday's match by 7 wickets."
- prediction = "Needs Verification"

Reason:
The congratulatory text is non-factual, but the match result
is a verifiable factual assertion.


IMPORTANT:
These examples demonstrate the distinction between the PURPOSE
or tone of a post and the presence of verifiable factual
assertions. Always extract a factual assertion when one exists,
even when it appears inside a greeting, opinion, emotional post,
advertisement, or social-media caption.

Return ONLY valid JSON.
"""

        try:
            response = (
                groq_client.chat.completions.create(
                    model=GROQ_MODEL,
                    reasoning_effort="low",
                    include_reasoning=False,
                    max_completion_tokens=1000,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": "nlp_misinformation_analysis",
                            "strict": True,
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "claim": {
                                        "type": "string"
                                    },
                                    "claim_type": {
                                        "type": "string",
                                        "enum": [
                                            "Political",
                                            "Financial",
                                            "Health",
                                            "Sports",
                                            "Technology",
                                            "Entertainment",
                                            "General",
                                        ],
                                    },
                                    "prediction": {
                                        "type": "string"
                                    },
                                    "confidence": {
                                        "type": "number"
                                    },
                                    "risk_score": {
                                        "type": "number"
                                    },
                                    "language": {
                                        "type": "string",
                                        "enum": [
                                            "English",
                                            "Hindi",
                                            "Kannada",
                                            "Mixed",
                                        ],
                                    },
                                    "keywords": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                    },
                                    "manipulation_signals": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        },
                                    },
                                },
                                "required": [
                                    "claim",
                                    "claim_type",
                                    "prediction",
                                    "confidence",
                                    "risk_score",
                                    "language",
                                    "keywords",
                                    "manipulation_signals",
                                ],
                                "additionalProperties": False,
                            },
                        },
                    },
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert NLP analysis system. "
                                "Analyze linguistic and manipulation signals. "
                                "Determine language from the MAIN CLAIM only. "
                                "Ignore unrelated OCR text and social-media "
                                "interface text when determining language. "
                                "Do not determine factual truth. "
                                "Return only structured JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
            )

            output = response.choices[0].message.content

            if not output or not output.strip():
                raise ValueError("Groq returned an empty AI response.")

            result = self.extract_json_response(output)

            claim = str(
                    result.get("claim", "")
                ).strip()

            invalid_claims = {
                    "",
                    "unknown",
                    "n/a",
                    "none",
                    "null",
                    "not a factual claim",
                }

            if claim.lower() in invalid_claims:
    
                prediction = str(
                    result.get(
                        "prediction",
                        "Not a Factual Claim"
                    )
                ).strip()

                # Preserve only valid prediction values.
                if prediction not in {
                    "Needs Verification",
                    "Not a Factual Claim",
                }:
                    prediction = "Not a Factual Claim"

                return {
                    "status": "success",
                    "claim": "",
                    "claim_type": "General",
                    "prediction": prediction,
                    "confidence": 0,
                    "risk_score": 0,
                    "keywords": [],
                    "language": str(
                        result.get(
                            "language",
                            "Unknown"
                        )
                    ).strip(),
                    "manipulation_signals": [],
                }
            
            if not claim:
                    return {
                        "status": "error",
                        "claim": "Unknown",
                        "claim_type": "General",
                        "prediction": "Verification Unavailable",
                        "confidence": None,
                        "risk_score": None,
                        "language": "Unknown",
                        "keywords": [],
                         
                        "manipulation_signals": [],
                    }

            allowed_claim_types = {
                "Political",
                "Financial",
                "Health",
                "Sports",
                "Technology",
                "Entertainment",
                "General",
            }

            claim_type = str(
                result.get("claim_type", "General")
            ).strip()

            if claim_type not in allowed_claim_types:
                claim_type = "General"

            prediction = str(
                result.get(
                    "prediction",
                    "Needs Verification"
                )
            ).strip()

            if prediction not in {
                "Needs Verification",
                "Not a Factual Claim",
            }:
                prediction = "Needs Verification"

            confidence = self.clamp_number(
                result.get("confidence"),
                0,
                100,
                0,
            )

            risk_score = self.clamp_number(
                result.get("risk_score"),
                0,
                100,
                0,
            )

            confidence = (
                int(confidence)
                if confidence.is_integer()
                else confidence
            )

            risk_score = (
                int(risk_score)
                if risk_score.is_integer()
                else risk_score
            )

            # ---------------------------------------------
            # LANGUAGE VALIDATION
            # ---------------------------------------------

            language = str(
                result.get("language", "English")
            ).strip()

            allowed_languages = {
                "English",
                "Hindi",
                "Kannada",
                "Mixed",
            }

            if language not in allowed_languages:
                language = "English"

            # ---------------------------------------------
            # KEYWORDS
            # ---------------------------------------------

            keywords = result.get("keywords", [])

            if not isinstance(keywords, list):
                keywords = []

            keywords = [
                str(keyword).strip()
                for keyword in keywords
                if str(keyword).strip()
            ][:15]

            # ---------------------------------------------
            # MANIPULATION SIGNALS
            # ---------------------------------------------

            manipulation_signals = result.get(
                "manipulation_signals",
                [],
            )

            if not isinstance(manipulation_signals, list):
                manipulation_signals = []

            manipulation_signals = [
                str(signal).strip()
                for signal in manipulation_signals
                if str(signal).strip()
            ][:10]

            # ---------------------------------------------
            # FINAL RESULT
            # ---------------------------------------------

            return {
                "status": "success",
                "claim": claim,
                "claim_type": claim_type,
                "prediction": prediction,
                "confidence": confidence,
                "risk_score": risk_score,
                "language": language,
                "keywords": keywords,
                 
                "manipulation_signals": manipulation_signals,
            }

        except Exception:
            logger.exception("NLP analysis failed.")

            return {
                "status": "error",
                "claim": text[:200],
                "claim_type": "General",
                "prediction": "Verification Unavailable",
                "confidence": None,
                "risk_score": None,
                "language": "Unknown",
                "keywords": [],
                 
                "manipulation_signals": [],
            }


nlp_service = NLPService()
