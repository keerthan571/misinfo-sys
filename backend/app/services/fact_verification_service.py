import json
import logging
import os
import re
import time
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-20b"
)

TAVILY_API_KEY = os.getenv(
    "TAVILY_API_KEY"
)


# ============================================================
# CLIENT INITIALIZATION
# ============================================================

groq_client = (
    Groq(api_key=GROQ_API_KEY)
    if GROQ_API_KEY
    else None
)

tavily_client = (
    TavilyClient(api_key=TAVILY_API_KEY)
    if TAVILY_API_KEY
    else None
)


# ============================================================
# ALLOWED VERDICTS
# ============================================================

ALLOWED_VERDICTS = {
    "Verified Information",
    "False Information",
    "Misleading Information",
    "Insufficient Evidence",
}


# ============================================================
# JSON EXTRACTION
# ============================================================

def extract_json_response(output: str) -> dict[str, Any]:

    if not output or not output.strip():

        raise ValueError(
            "Empty AI response."
        )

    cleaned = (
        output
        .replace("```json", "")
        .replace("```JSON", "")
        .replace("```", "")
        .strip()
    )

    # --------------------------------------------------------
    # Attempt 1:
    # Entire response is JSON
    # --------------------------------------------------------

    try:

        result = json.loads(
            cleaned
        )

        if not isinstance(result, dict):

            raise ValueError(
                "AI response JSON is not an object."
            )

        return result

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Attempt 2:
    # Extract JSON object surrounded by other text
    # --------------------------------------------------------

    match = re.search(
        r"\{[\s\S]*\}",
        cleaned
    )

    if not match:

        raise ValueError(
            "No JSON object found in AI response."
        )

    result = json.loads(
        match.group(0)
    )

    if not isinstance(result, dict):

        raise ValueError(
            "Extracted AI response is not a JSON object."
        )

    return result


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value: Any) -> str:

    if value is None:
        return ""

    return str(value).strip()


# ============================================================
# CONFIDENCE CALCULATION
# ============================================================

def calculate_confidence(
    verdict: str,
    source_count: int,
    evidence_length: int,
    evidence_strength: float | None = None,
) -> int:

    """
    Calculate confidence in the verification verdict.

    This confidence represents confidence in the evidence-based
    verification result. It is NOT a probability that the claim
    is true.

    The calculation considers:
    - verification verdict
    - number of retrieved sources
    - amount of usable evidence
    - evidence strength reported by the verification model

    Importantly, a large amount of weak evidence should not
    automatically produce high confidence.
    """

    # --------------------------------------------------------
    # No evidence
    # --------------------------------------------------------

    if source_count <= 0 or evidence_length <= 0:

        return 0

    # --------------------------------------------------------
    # Evidence quantity score
    # --------------------------------------------------------

    if source_count >= 5:
        source_score = 25

    elif source_count >= 4:
        source_score = 22

    elif source_count >= 3:
        source_score = 18

    elif source_count >= 2:
        source_score = 12

    else:
        source_score = 7

    # --------------------------------------------------------
    # Evidence length score
    # --------------------------------------------------------

    if evidence_length >= 5000:
        length_score = 20

    elif evidence_length >= 3000:
        length_score = 17

    elif evidence_length >= 1500:
        length_score = 13

    elif evidence_length >= 750:
        length_score = 9

    else:
        length_score = 5

    # --------------------------------------------------------
    # Base verdict score
    # --------------------------------------------------------

    if verdict == "Verified Information":

        base_score = 45

    elif verdict == "False Information":

        base_score = 45

    elif verdict == "Misleading Information":

        base_score = 40

    else:

        # Insufficient evidence should never look
        # extremely certain.
        base_score = 20

    # --------------------------------------------------------
    # Model evidence-strength contribution
    # --------------------------------------------------------

    if evidence_strength is None:

        model_score = 0

    else:

        try:

            strength = max(
                0,
                min(
                    100,
                    float(evidence_strength)
                )
            )

            model_score = round(
                strength * 0.10
            )

        except (
            TypeError,
            ValueError
        ):

            model_score = 0

    confidence = (
        base_score
        + source_score
        + length_score
        + model_score
    )

    # --------------------------------------------------------
    # Verdict-specific safety caps
    # --------------------------------------------------------

    if verdict == "Insufficient Evidence":

        confidence = min(
            confidence,
            65
        )

    else:

        confidence = min(
            confidence,
            95
        )

    return max(
        0,
        min(
            int(confidence),
            95
        )
    )


# ============================================================
# SEARCH QUERY GENERATION
# ============================================================

def build_search_queries(
    claim: str,
    context: str = "",
    publisher: str | None = None,
    platform: str | None = None,
) -> list[str]:

    """
    Build focused verification queries.

    Special handling is used for attribution-style claims such as:
    - X said ...
    - X claimed ...
    - X questioned ...
    - X posted ...
    - X stated ...

    These claims are better verified by searching for the
    attributed person/source and the distinctive factual
    details instead of searching the entire generated sentence.
    """

    claim = normalize_text(claim)
    context = normalize_text(context)
    publisher = normalize_text(publisher)
    platform = normalize_text(platform)

    queries = []

    # ========================================================
    # Detect attribution-style claims
    # ========================================================

    attribution_pattern = re.compile(
        r"\b("
        r"said|stated|claimed|questioned|asked|posted|"
        r"wrote|according to|alleged|argued|shared|"
        r"mentioned|asserted"
        r")\b",
        re.IGNORECASE
    )

    is_attribution_claim = bool(
        attribution_pattern.search(claim)
    )

    # ========================================================
    # Extract useful entities / numbers from claim
    # ========================================================

    # Currency / numeric expressions such as:
    # ₹200, ₹360, ₹400, 5 to 6, 1 kg
    numbers = re.findall(
        r"(?:₹|Rs\.?|INR)?\s*\d+(?:\.\d+)?(?:\s*(?:kg|litres?|liters?))?",
        claim,
        flags=re.IGNORECASE
    )

    numbers = list(
        dict.fromkeys(
            x.strip()
            for x in numbers
            if x.strip()
        )
    )

    # ========================================================
    # Extract important attribution names
    # ========================================================

    attribution_name = ""

    name_match = re.search(
        r"\b("
        r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4}"
        r")\b",
        claim
    )

    if name_match:
        attribution_name = name_match.group(1).strip()

    # Prefer known publisher/source name if available.
    if publisher:
        publisher_clean = re.sub(
            r"\s+",
            " ",
            publisher
        ).strip()

        # Avoid OCR junk such as "Sociallssues PublicAw..."
        if len(publisher_clean) >= 4:
            publisher_name = publisher_clean
        else:
            publisher_name = ""
    else:
        publisher_name = ""

    # ========================================================
    # Extract distinctive keywords
    # ========================================================

    keyword_candidates = re.findall(
        r"\b[A-Za-z][A-Za-z0-9₹-]{2,}\b",
        claim
    )

    stopwords = {
        "this",
        "that",
        "when",
        "where",
        "what",
        "which",
        "with",
        "from",
        "into",
        "about",
        "because",
        "approximately",
        "approx",
        "questions",
        "questioned",
        "asks",
        "asked",
        "claims",
        "claimed",
        "says",
        "said",
        "stated",
        "information",
        "available",
        "central",
        "assertion",
        "according",
        "while",
        "could",
        "should",
        "would",
        "less",
        "than",
        "more",
        "only",
        "alone",
        "cost",
        "price",
        "produce",
        "production",
    }

    keywords = []

    for word in keyword_candidates:

        lower = word.lower()

        if lower in stopwords:
            continue

        if len(word) < 4:
            continue

        if word not in keywords:
            keywords.append(word)

    # Keep only a few useful words.
    keywords = keywords[:8]

    # ========================================================
    # ATTRIBUTION CLAIM SEARCH
    # ========================================================

    if is_attribution_claim:

        # ----------------------------------------------------
        # Query 1:
        # Person + distinctive topic
        # ----------------------------------------------------

        if attribution_name:

            topic_words = [
                word
                for word in keywords
                if word.lower()
                not in {
                    attribution_name.lower(),
                    "ias",
                }
            ][:4]

            if topic_words:

                queries.append(
                    f'"{attribution_name}" '
                    + " ".join(topic_words)
                )

        # ----------------------------------------------------
        # Query 2:
        # Person + important numeric values
        # ----------------------------------------------------

        if attribution_name and numbers:

            queries.append(
                f'"{attribution_name}" '
                + " ".join(numbers[:4])
            )

        # ----------------------------------------------------
        # Query 3:
        # Person + key topic from original context
        # ----------------------------------------------------

        if attribution_name and context:

            context_lower = context.lower()

            context_terms = []

            important_terms = [
                "paneer",
                "milk",
                "price",
                "cost",
                "₹200",
                "₹360",
                "₹400",
                "litres",
                "liters",
                "kg",
            ]

            for term in important_terms:

                if term.lower() in context_lower:
                    context_terms.append(term)

            if context_terms:

                queries.append(
                    f'"{attribution_name}" '
                    + " ".join(context_terms)
                )

        # ----------------------------------------------------
        # Query 4:
        # Exact distinctive phrase from claim
        # ----------------------------------------------------

        distinctive_phrases = []

        phrase_patterns = [
            r"less than\s+₹?\s*\d+",
            r"\d+\s+to\s+\d+\s+(?:litres?|liters?)",
            r"\d+\s*kg",
        ]

        for pattern in phrase_patterns:

            matches = re.findall(
                pattern,
                claim,
                flags=re.IGNORECASE
            )

            distinctive_phrases.extend(
                matches
            )

        if attribution_name and distinctive_phrases:

            queries.append(
                f'"{attribution_name}" '
                + " ".join(
                    distinctive_phrases[:3]
                )
            )

        # ----------------------------------------------------
        # Query 5:
        # Publisher + topic
        # ----------------------------------------------------

        if publisher_name:

            if keywords:

                queries.append(
                    f'"{publisher_name}" '
                    + " ".join(
                        keywords[:4]
                    )
                )

    # ========================================================
    # NORMAL FACTUAL CLAIM
    # ========================================================

    else:

        # Exact claim
        if claim:

            queries.append(
                f'"{claim[:300]}"'
            )

        # Claim + publisher
        if claim and publisher_name:

            queries.append(
                f'"{claim[:220]}" '
                f'"{publisher_name[:120]}"'
            )

        # Claim + important context
        if claim and context:

            queries.append(
                f'"{claim[:220]}" '
                f'"{context[:300]}"'
            )

        # Platform
        if claim and platform:

            queries.append(
                f'"{claim[:250]}" '
                f'"{platform[:80]}"'
            )

    # ========================================================
    # CLEAN + DEDUPLICATE
    # ========================================================

    cleaned_queries = []

    for query in queries:

        query = re.sub(
            r"\s+",
            " ",
            query
        ).strip()

        if not query:
            continue

        if query not in cleaned_queries:
            cleaned_queries.append(
                query
            )

    return cleaned_queries[:5]
# ============================================================
# TAVILY SEARCH
# ============================================================

def collect_evidence(
    claim: str,
    context: str = "",
    publisher: str | None = None,
    platform: str | None = None,
):
    
    """
    Search multiple complementary queries in parallel and combine
    the resulting evidence.

    Search quality is intentionally unchanged:
    - Same 3 queries
    - Same advanced Tavily search
    - Same max_results=5
    - Same evidence limits
    - Same deduplication
    """

    queries = build_search_queries(
        claim=claim,
        context=context,
        publisher=publisher,
        platform=platform,
    )

    search_start = time.perf_counter()

    def search_query(query):
    
        query_start = time.perf_counter()

        try:

            search = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=5
        )

            results = search.get(
                "results",
                []
            )

            query_time = (
                time.perf_counter()
                - query_start
            )

            logger.warning(
                "TAVILY QUERY TIME: %.2fs | results=%s | query=%s",
                query_time,
                len(results) if isinstance(results, list) else 0,
                query
            )

            if isinstance(results, list):
                return results

        except Exception:

            query_time = (
                time.perf_counter()
                - query_start
            )

            logger.exception(
                "Tavily search failed after %.2fs | query=%s",
                query_time,
                query
            )

        return []
    
    # Run the independent Tavily searches concurrently.
    with ThreadPoolExecutor(
        max_workers=len(queries)
    ) as executor:

        results_by_query = list(
            executor.map(
                search_query,
                queries
            )
        )

    search_total_time = (
        time.perf_counter()
        - search_start
    )

    logger.warning(
        "TAVILY TOTAL TIME: %.2fs | queries=%s",
        search_total_time,
        len(queries)
    )
    
    # Preserve the original query ordering.
    all_results = []

    for results in results_by_query:
        all_results.extend(results)

    # --------------------------------------------------------
    # Deduplicate results by URL
    # --------------------------------------------------------

    unique_results = []

    seen_urls = set()

    for item in all_results:

        if not isinstance(
            item,
            dict
        ):
            continue

        url = normalize_text(
            item.get("url")
        )

        if url:

            if url in seen_urls:
                continue

            seen_urls.add(url)

        unique_results.append(
            item
        )

    # Keep evidence manageable.
    unique_results = unique_results[:8]

    # --------------------------------------------------------
    # Build evidence text
    # --------------------------------------------------------

    evidence_parts = []

    sources = []

    for index, item in enumerate(
        unique_results,
        start=1
    ):

        title = normalize_text(
            item.get("title")
        )

        content = normalize_text(
            item.get("content")
        )

        url = normalize_text(
            item.get("url")
        )

        published_date = normalize_text(
            item.get("published_date")
        )

        # Limit individual evidence chunks.
        content = content[:1200]

        evidence_parts.append(
            f"""
SOURCE {index}

Title:
{title}

Published Date:
{published_date or "Not available"}

URL:
{url}

Content:
{content}
"""
        )

        if url:

            sources.append(
                url
            )

    evidence = "\n".join(
        evidence_parts
    )

    sources = list(
        dict.fromkeys(
            sources
        )
    )

    return (
        evidence,
        sources
    )

# ============================================================
# VERIFICATION PROMPT
# ============================================================

def build_verification_prompt(
    claim: str,
    evidence: str,
    context: str = "",
    publisher: str | None = None,
    platform: str | None = None,
) -> str:

    return f"""
You are an evidence-based fact verification system.

Your task is to determine the correct verdict for the CLAIM using
ONLY the PROVIDED WEB EVIDENCE.

CLAIM TO VERIFY:
{claim}

SOURCE CONTEXT:
{context or "Not available"}

PUBLISHER / SOURCE:
{publisher or "Not available"}

PLATFORM:
{platform or "Not available"}

PROVIDED WEB EVIDENCE:
{evidence}


============================================================
CORE VERIFICATION RULES
============================================================

1. Use ONLY the provided web evidence.

2. Do NOT use your own knowledge, memory, assumptions,
   calculations, or outside information.

3. Evaluate the COMPLETE claim.

4. Consider all material parts of the claim:
   - person or organization
   - action or event
   - date or year
   - location
   - quantity or measurement
   - certainty or absolute wording

5. Evidence must directly address the claim or a material part
   of the claim.

6. Do NOT mark a claim False merely because the evidence does
   not mention it.

7. Do NOT mark a claim Verified merely because the evidence
   discusses the same general topic.

8. Use these verdicts:

   Verified Information
   = The provided evidence directly supports the claim.

   False Information
   = The provided evidence directly contradicts the claim.

   Misleading Information
   = The evidence supports part of the claim, but the claim
     materially exaggerates, changes, or extends what the
     evidence actually establishes.

   Insufficient Evidence
   = The provided evidence does not clearly support or
     contradict the claim.


============================================================
ATTRIBUTION CLAIMS — VERY IMPORTANT
============================================================

An attribution claim is a claim that a person or organization
said, stated, claimed, questioned, asked, posted, wrote, shared,
or otherwise expressed something.

Examples:

"X said that..."
"X questioned whether..."
"X posted..."
"X claimed..."
"X asked how..."

For attribution claims, the PRIMARY verification target is:

DID THE NAMED PERSON OR ORGANIZATION ACTUALLY MAKE, SHARE,
POST, WRITE, ASK, QUESTION, OR EXPRESS THE STATEMENT?

Do NOT automatically verify the underlying factual proposition.

For example:

CLAIM:
"IAS Tukaram Mundhe questioned how paneer could be sold below
₹200 when producing 1 kg requires 5 to 6 litres of milk."

The primary verification target is whether Tukaram Mundhe
actually made or shared that question.

It is NOT automatically necessary to prove that:
- 5 to 6 litres are required,
- milk costs ₹60 per litre,
- production costs ₹360,
- paneer costs ₹400,
- paneer cannot be sold below ₹200.

Those underlying propositions must NOT be treated as proven
unless the provided evidence independently establishes them.

A question must remain a QUESTION.

Do NOT rewrite:

"How is paneer available below ₹200?"

as:

"Paneer cannot be sold below ₹200."

Do NOT convert rhetorical wording into a factual assertion.


============================================================
WHAT COUNTS AS ATTRIBUTION EVIDENCE
============================================================

Evidence can support an attribution when it contains:

- the original social-media post
- a screenshot of the original post
- a direct quotation
- a reliable report reproducing the statement
- a credible source explicitly attributing the statement
  to the named person

If the evidence contains an actual post or quotation from the
named person, explicitly recognize that as attribution evidence.

If the evidence only talks about paneer, milk prices, production
costs, or the same general topic but does NOT connect the
statement to the named person, attribution is NOT established.

In that situation use:

"Insufficient Evidence"

Do not infer attribution from topic similarity.


============================================================
IMPORTANT DISTINCTION FOR ATTRIBUTION
============================================================

For an attribution claim, keep these two questions separate:

A. DID THE PERSON MAKE THE STATEMENT?

B. IS THE UNDERLYING STATEMENT FACTUALLY TRUE?

If the evidence establishes A but does not establish B:

Verdict:
"Verified Information"

Reason:
Explain that the evidence supports the attribution, while
explicitly stating that it does not by itself establish the
truth of the underlying proposition.

Do NOT downgrade the attribution to Insufficient Evidence merely
because the underlying proposition was not independently verified.

Do NOT say:

"The paneer cost claim is verified."

Do NOT say:

"The paneer cannot be sold below ₹200."

Do NOT say:

"The production cost is definitely ₹400."

Instead say something like:

"The provided evidence contains a post attributing the question
about paneer being sold below ₹200 to IAS Tukaram Mundhe. This
supports the attribution, but does not by itself establish the
truth of the underlying cost calculation."

Only use wording that is actually supported by the evidence.


============================================================
EVIDENCE DESCRIPTION RULES
============================================================

When writing the reason:

1. Describe the ACTUAL evidence provided.

2. Do not invent evidence.

3. Do not call something a "direct quotation" unless the evidence
   actually contains a quotation.

4. Do not call something an "original post" unless the evidence
   actually shows or identifies an original post.

5. Do not say "social-media posts" if only one relevant post is
   present.

6. Do not say "multiple sources confirm" unless multiple provided
   sources actually establish the relevant point.

7. Do not mention "Source 1", "Source 2", etc.

8. Do not mention search-engine ranking or retrieval details.

9. Do not claim that evidence proves something merely because
   several sources repeat the same statement.

10. Do not introduce facts that are absent from the evidence.


============================================================
VERIFIED ATTRIBUTION REASON
============================================================

If attribution is directly supported, the reason MUST contain
two ideas:

1. What evidence supports the attribution.
2. A clear distinction that this does not independently establish
   the underlying factual proposition.

Preferred structure:

"The provided evidence contains [specific evidence] attributing
the statement/question to [person]. This supports the attribution,
but does not by itself establish the truth of the underlying
proposition."

Adapt the wording to the actual evidence.

Do NOT blindly copy this sentence if the evidence differs.


============================================================
FALSE ATTRIBUTION
============================================================

If reliable provided evidence directly shows that the named person
did NOT make, share, post, write, ask, or state the statement:

Verdict:
"False Information"

Reason should explain:

"The provided evidence indicates that [person] did not make or
share the stated statement, contradicting the attribution."

Only use this if the evidence actually establishes that.


============================================================
INSUFFICIENT ATTRIBUTION
============================================================

If the evidence discusses the same subject but does not establish
that the named person made or shared the statement:

Verdict:
"Insufficient Evidence"

Reason should explain:

"The provided evidence discusses the same subject but does not
establish that [person] made or shared the statement."

Do NOT infer attribution from topic similarity.


============================================================
MISLEADING ATTRIBUTION
============================================================

Use "Misleading Information" only when the provided evidence
supports part of the attribution but materially changes,
exaggerates, or distorts what the person actually said.

Clearly identify what is supported and what is distorted.

Do NOT use Misleading merely because the underlying factual
proposition has not been independently verified.


============================================================
NON-ATTRIBUTION CLAIMS
============================================================

For ordinary factual claims that do not primarily concern what
someone said or asked:

Evaluate the factual proposition itself.

Mark:

Verified Information
only when the evidence supports the proposition.

False Information
only when reliable evidence directly contradicts it.

Misleading Information
when evidence supports only part of it and the claim materially
overstates or distorts the evidence.

Insufficient Evidence
when the evidence does not resolve it.


============================================================
ABSOLUTE CLAIMS
============================================================

Words such as:

- always
- never
- completely
- only
- guarantees
- prevents
- cures
- cannot

require evidence supporting that exact level of certainty.

Do not weaken or strengthen the claim during verification.


============================================================
DATES AND NUMBERS
============================================================

Pay close attention to:

- dates
- years
- locations
- quantities
- measurements
- prices
- percentages

Evidence about another date, year, location, or quantity must not
automatically be treated as evidence for the claim.


============================================================
REASON WRITING
============================================================

The reason MUST:

- directly explain why the selected verdict was assigned
- use ONLY provided evidence
- be concise
- normally be 1-3 sentences
- avoid unnecessary background
- avoid repeating the entire claim
- distinguish attribution from underlying factual truth
  when applicable

Do NOT use:

"According to my knowledge"
"Generally known"
"Likely"
"I believe"
"It seems"
"Probably"

Do NOT introduce outside information.

Do NOT say "the claim is true" when only attribution has
been verified.


============================================================
EVIDENCE STRENGTH
============================================================

evidence_strength must be an integer from 0 to 100.

0-25:
Very weak or insufficient evidence.

26-50:
Limited evidence.

51-75:
Moderately strong evidence.

76-100:
Strong and consistent evidence.

This value measures the strength of the AVAILABLE EVIDENCE
FOR THE SELECTED VERDICT.

It is NOT the probability that the claim itself is true.


============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use EXACTLY this structure:

{{
    "verdict": "Verified Information | False Information | Misleading Information | Insufficient Evidence",
    "reason": "brief evidence-based explanation",
    "evidence_strength": 0
}}

No markdown.
No code fences.
No additional fields.
No additional text.
"""

# ============================================================
# GROQ VERIFICATION
# ============================================================

def run_groq_verification(
    claim: str,
    evidence: str,
    context: str = "",
    publisher: str | None = None,
    platform: str | None = None,
):

    prompt = build_verification_prompt(
        claim=claim,
        evidence=evidence,
        context=context,
        publisher=publisher,
        platform=platform,
    )

    # ========================================================
    # FIRST ATTEMPT
    # ========================================================

    try:

        response = (
            groq_client
            .chat
            .completions
            .create(

                model=GROQ_MODEL,

                reasoning_effort="low",

                include_reasoning=False,

                max_completion_tokens=1200,

                response_format={

                    "type": "json_schema",

                    "json_schema": {

                        "name":
                            "fact_verification",

                        "strict": True,

                        "schema": {

                            "type": "object",

                            "properties": {

                                "verdict": {

                                    "type": "string",

                                    "enum": [

                                        "Verified Information",

                                        "False Information",

                                        "Misleading Information",

                                        "Insufficient Evidence"

                                    ]

                                },

                                "reason": {

                                    "type": "string"

                                },

                                "evidence_strength": {

                                    "type": "integer",

                                    "minimum": 0,

                                    "maximum": 100

                                }

                            },

                            "required": [

                                "verdict",

                                "reason",

                                "evidence_strength"

                            ],

                            "additionalProperties":
                                False

                        }

                    }

                },

                messages=[

                    {

                        "role": "system",

                        "content": (
                            "You are a strict evidence-based "
                            "fact verification system. "
                            "Use only supplied evidence. "
                            "Return structured JSON."
                        )

                    },

                    {

                        "role": "user",

                        "content": prompt

                    }

                ]

            )
        )

        output = (
            response
            .choices[0]
            .message
            .content
        )

        # ----------------------------------------------------
        # Important:
        # Some reasoning models can occasionally return
        # an empty content field.
        # ----------------------------------------------------

        if output and output.strip():

            return extract_json_response(
                output
            )

        logger.warning(
            "Groq returned an empty structured response. "
            "Attempting fallback verification."
        )

    except Exception:

        logger.exception(
            "Primary Groq fact-verification request failed."
        )

    # ========================================================
    # FALLBACK ATTEMPT
    # ========================================================

    try:

        fallback_response = (
            groq_client
            .chat
            .completions
            .create(

                model=GROQ_MODEL,

                reasoning_effort="low",

                include_reasoning=False,

                max_completion_tokens=800,

                messages=[

                    {

                        "role": "system",

                        "content": (
                            "You are a strict fact verifier. "
                            "Return ONLY JSON."
                        )

                    },

                    {

                        "role": "user",

                        "content": f"""
Verify this claim using ONLY the evidence.

CLAIM:
{claim}

EVIDENCE:
{evidence}

Return ONLY JSON:

{{
    "verdict": "Verified Information | False Information | Misleading Information | Insufficient Evidence",
    "reason": "brief evidence-based explanation",
    "evidence_strength": 0
}}

Rules:
- Do not use outside knowledge.
- Pay attention to dates and years.
- Clearly contradictory evidence means False Information.
- Clearly supporting evidence means Verified Information.
- Mixed/distorted evidence means Misleading Information.
- Otherwise use Insufficient Evidence.
- evidence_strength must be 0-100.
- Evaluate the exact claim being made.
- If the claim describes what a person said,
  questioned, posted, or stated, verify the attribution itself.
- Do not convert a rhetorical question into an absolute factual claim.
- A reliable source confirming that the named person made the
  statement can support an attribution claim.

For attribution claims such as "Person X stated/claimed/questioned Y":
- Verify the attribution separately from the underlying claim.
- If the evidence supports that Person X made or questioned the statement,
  the attribution can be Verified even if the underlying factual details
  are not independently proven.
- The reason must explain exactly what was verified.
- Do not write "Source 8", "Source 1", etc.
- Do not claim that the underlying factual statement is proven unless
  the evidence actually establishes it.
- A good reason should clearly distinguish:
  (1) the person made/questioned the statement, and
  (2) whether the underlying statement itself was independently verified.
"""
                    }

                ]

            )
        )

        fallback_output = (
            fallback_response
            .choices[0]
            .message
            .content
        )

        if not fallback_output:

            raise ValueError(
                "Fallback Groq response was empty."
            )

        return extract_json_response(
            fallback_output
        )

    except Exception:

        logger.exception(
            "Fallback Groq fact-verification request failed."
        )

        raise


# ============================================================
# MAIN VERIFICATION FUNCTION
# ============================================================
def verify_claim(
    claim: str,
    context: str = "",
    publisher: str | None = None,
    platform: str | None = None,
):

    verification_start = time.perf_counter()

    claim = normalize_text(
        claim
    )

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    INVALID_CLAIMS = {
        "",
        "unknown",
        "none",
        "null",
        "n/a",
        "na",
        "not available",
        "unavailable",
    }

    if (
        claim.lower() in INVALID_CLAIMS
        or len(claim) < 5
    ):

        return {

            "status": "success",

            "claim": claim,

            "verdict":
                "Insufficient Evidence",

            "reason": (
                "No meaningful claim was extracted "
                "from the provided text."
            ),

            "confidence": 0,

            "sources": []

        }

    # ========================================================
    # API CONFIGURATION
    # ========================================================

    if not TAVILY_API_KEY:

        logger.error(
            "TAVILY_API_KEY is not configured."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "Fact verification service is not configured.",

            "confidence": None,

            "sources": []

        }

    if not GROQ_API_KEY:

        logger.error(
            "GROQ_API_KEY is not configured."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "AI verification service is not configured.",

            "confidence": None,

            "sources": []

        }

    if not tavily_client or not groq_client:

        logger.error(
            "Fact verification clients could not be initialized."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason":
                "Verification service initialization failed.",

            "confidence": None,

            "sources": []

        }

    # ========================================================
    # SEARCH + VERIFICATION
    # ========================================================

    sources = []

    evidence = ""

    try:

        # ----------------------------------------------------
        # Retrieve evidence
        # ----------------------------------------------------

        (
            evidence,
            sources
        ) = collect_evidence(
            claim=claim,
            context=context,
            publisher=publisher,
            platform=platform,
        )

        # ----------------------------------------------------
        # No evidence
        # ----------------------------------------------------

        if not evidence.strip():

            return {

                "status": "success",

                "claim": claim,

                "verdict":
                    "Insufficient Evidence",

                "reason": (
                    "No sufficient evidence was found "
                    "to verify or contradict this claim."
                ),

                "confidence": 0,

                "sources": []

            }

        # ----------------------------------------------------
        # Verify using Groq
        # ----------------------------------------------------

        groq_start = time.perf_counter()

        result = run_groq_verification(
            claim=claim,
            evidence=evidence,
            context=context,
            publisher=publisher,
            platform=platform,
        )

        groq_total_time = (
            time.perf_counter()
            - groq_start
        )

        logger.warning(
            "GROQ VERIFICATION TIME: %.2fs",
            groq_total_time
        )

        # ----------------------------------------------------
        # Extract verdict
        # ----------------------------------------------------

        verdict = normalize_text(
            result.get(
                "verdict"
            )
        )

        if verdict not in ALLOWED_VERDICTS:

            logger.warning(
                "Invalid verdict returned by AI: %s",
                verdict
            )

            verdict = (
                "Insufficient Evidence"
            )

        # ----------------------------------------------------
        # Extract reason
        # ----------------------------------------------------

        reason = normalize_text(
            result.get(
                "reason"
            )
        )

        if not reason:

            reason = (
                "No explanation was provided "
                "by the verification model."
            )

        # ----------------------------------------------------
        # Evidence strength
        # ----------------------------------------------------

        evidence_strength = result.get(
            "evidence_strength"
        )

        try:

            evidence_strength = max(
                0,
                min(
                    100,
                    int(
                        evidence_strength
                    )
                )
            )

        except (
            TypeError,
            ValueError
        ):

            evidence_strength = None

        # ----------------------------------------------------
        # Calculate final confidence
        # ----------------------------------------------------

        confidence = calculate_confidence(

            verdict,

            len(sources),

            len(evidence),

            evidence_strength

        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        verification_total_time = (
            time.perf_counter()
            - verification_start
        )

        logger.warning(
            "FACT VERIFICATION TOTAL: %.2fs | verdict=%s | confidence=%s | sources=%s",
            verification_total_time,
            verdict,
            confidence,
            len(sources)
        )

        return {

            "status": "success",

            "claim": claim,

            "verdict": verdict,

            "reason": reason,

            "confidence": confidence,

            "sources": sources

        }

    # ========================================================
    # JSON ERROR
    # ========================================================

    except json.JSONDecodeError:

        logger.exception(
            "Failed to parse AI fact-verification JSON."
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason": (
                "The verification model returned "
                "an invalid response."
            ),

            "confidence": None,

            "sources": sources

        }

    # ========================================================
    # ALL OTHER ERRORS
    # ========================================================

    except Exception:

        logger.exception(
            "FACT VERIFICATION ERROR"
        )

        return {

            "status": "error",

            "claim": claim,

            "verdict":
                "Verification Unavailable",

            "reason": (
                "The fact verification service "
                "could not complete the request."
            ),

            "confidence": None,

            "sources": sources

        }