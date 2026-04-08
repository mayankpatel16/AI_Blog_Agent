"""
LLM Service — Multi-Agent Pipeline
------------------------------------
Agent 1 (Planner):   Generates structured outline with GEO targets
Agent 2 (Writer):    Writes each section with BLUF + varied structure
Agent 3 (Reviewer):  Checks content vs SEO rules, returns improved version
"""
import json
import re
import httpx
from config import get_settings

settings = get_settings()
_is_ollama = "ollama" in settings.LLM_BASE_URL.lower()
_base = settings.LLM_BASE_URL.rstrip("/")
_CHAT_URL = f"{_base}/chat" if _is_ollama else f"{_base}/chat/completions"


async def _chat(system: str, user: str, temperature: float = 0.7) -> str:
    headers = {"Content-Type": "application/json"}
    if settings.LLM_API_KEY and settings.LLM_API_KEY.lower() not in ("none", ""):
        headers["Authorization"] = f"Bearer {settings.LLM_API_KEY}"

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        **({"options": {"temperature": temperature}} if _is_ollama else {"temperature": temperature, "max_tokens": 2048}),
    }

    async with httpx.AsyncClient(verify=False, timeout=120.0) as client:
        resp = await client.post(_CHAT_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    content = data["message"]["content"].strip() if _is_ollama else data["choices"][0]["message"]["content"].strip()
    return content


def _extract_json(text: str) -> dict | list:
    text = re.sub(r"```(?:json)?", "", text).strip().rstrip("`").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
        m = re.search(pattern, text)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    raise ValueError(f"No JSON in response: {text[:200]}")


# ════════════════════════════════════════════════════════
# AGENT 1 — PLANNER
# ════════════════════════════════════════════════════════

PLANNER_SYSTEM = """You are a Lead SEO Content Planner. 
Output ONLY strict JSON. No explanation. No markdown fences. Start immediately with {"""

PLANNER_USER = """Plan a complete blog post for:

Topic: {topic}
Target Keywords: {keywords}

Return ONLY this JSON:
{{
  "title": "SEO H1 title, under 60 chars, keyword near start",
  "intent": "Informational",
  "focus_keyword": "main keyword",
  "entities": ["noun1", "noun2", "noun3", "noun4", "noun5"],
  "sections": [
    {{
      "heading": "heading text",
      "heading_level": 1,
      "order_index": 0,
      "geo_target": "specific question this answers",
      "format": "Narrative"
    }}
  ],
  "suggested_keywords": ["kw1", "kw2", "kw3"]
}}

Strict rules:
- Exactly ONE H1 (intro), four to six H2s, optionally one to two H3s
- Each heading must match a real Google search query
- Each section must clearly answer a specific user question (geo_target)
- Avoid vague or generic headings
- format choices: Narrative, BLUF+Narrative
"""

async def generate_outline(topic: str, keywords: list[str]) -> dict:
    kw_str = ", ".join(keywords) if keywords else "none"
    raw = await _chat(PLANNER_SYSTEM, PLANNER_USER.format(topic=topic, keywords=kw_str), temperature=0.5)
    return _extract_json(raw)


# ════════════════════════════════════════════════════════
# AGENT 2 — WRITER
# ════════════════════════════════════════════════════════

WRITER_SYSTEM = """You are a professional blog writer producing content for Google and AI search engines.

STRICT RULES:
- STRICTLY DO NOT repeat or include the section heading in the generated text.
- The output must start immediately with the content answering the question.
- Write for a general audience (grade 6–8 level)
- Use simple, common words. Avoid jargon and complex terms
- Use clear, natural, human-like language
- Prefer active voice
- Keep sentences mostly short (8–12 words), vary length naturally
- Break very complex ideas into smaller sentences, but add examples
- Use concrete examples and simple analogies to explain points
- Avoid repetitive phrasing; add relevant details simply and clearly
- Keep paragraphs short (2–3 sentences max)
- Ensure smooth flow and variation in sentence structure
- Use simple transition words (and, but, so) for smooth flow
- Use simple sentence structures: subject + verb + object
- Avoid all words with more than 3 syllables; prefer simple common words
- Never use placeholder text like [INSERT DATA]
- Avoid robotic phrases like "From a technical standpoint", "Industry data shows"
- Do NOT include the heading in output
- Start directly with content (no intro phrases like "Here is the section")
- There should be approximate 1.3 syllable per word not more than that and don't use hard-to-read phrasing
- avoid nested clauses
CLARITY RULE:
- Prefer clarity over detail
- Write as if explaining to a 12-year-old
- If a sentence feels long, split it into two
"""

WRITER_USER = """Write blog section:

Post Topic: {topic}
Section Heading: {heading}
Format: {format}
Keywords to use naturally: {keywords}
This section answers: {geo_target}
{extra}

IMPORTANT: If there are additional focus instructions above, follow them EXACTLY and make significant changes to improve the content accordingly.

Structure your output EXACTLY like this:

[One short sentence answering "{geo_target}".]

[Paragraph 1: 2–3 sentences. Each sentence under 12 words.]

[Paragraph 2: 2–3 sentences. Each sentence under 12 words.]

[Paragraph 3: 2–3 sentences. Each sentence under 12 words.]

[Paragraph 4: 2–3 sentences. Each sentence under 12 words.]

RULE:
- Most sentences under 12 words; allow up to 15 words for flow

RULES TO IMPROVE LENGTH AND READABILITY:
- Aim for about 300-340 words per section
- Write enough content so the full article totals at least 1200 words when all sections are combined, each section at least 300 words
- Add relevant examples or brief explanations naturally
- Keep language simple and clear, with varied sentence lengths
- Use transition sentences for smooth flow
"""

DATA_BLOCK_TABLE = ""
DATA_BLOCK_LIST = ""


async def generate_section_content(
    topic: str, heading: str, keywords: list[str],
    extra_instructions: str = "", format: str = "BLUF+Narrative", geo_target: str = "",
) -> str:
    kw_str = ", ".join(keywords) if keywords else "general"
    extra = f"Additional focus: {extra_instructions}" if extra_instructions else ""
    if not geo_target:
        geo_target = f"What is {heading} and why does it matter?"

    # Choose data block based on format
    data_block = DATA_BLOCK_TABLE if "table" in format.lower() else \
                 DATA_BLOCK_LIST if "list" in format.lower() else \
                 DATA_BLOCK_LIST  # default to list

    raw = await _chat(
        WRITER_SYSTEM,
        WRITER_USER.format(
            topic=topic, heading=heading, format=format,
            keywords=kw_str, geo_target=geo_target, extra=extra,
            data_block_instruction=data_block,
        ),
        temperature=0.7,  # Reduced for better readability balance
    )

    print(f"DEBUG: Raw writer output for {heading}: {raw[:200]}...")

    # Agent 3 — Reviewer: check and improve the content
    if extra_instructions:
        # For quick fixes, use the writer output directly without reviewer to preserve the changes
        reviewed = _strip_review_notes(raw)
    else:
        reviewed = await _review_content(raw, heading, keywords, geo_target)
    print(f"DEBUG: Reviewed content for {heading}: {reviewed[:200]}...")
    return reviewed


# ════════════════════════════════════════════════════════
# AGENT 3 — SEO REVIEWER
# ════════════════════════════════════════════════════════

REVIEWER_SYSTEM = """You are an SEO Quality Reviewer.

Your job is to improve readability, clarity, and SEO quality.
Prefer words with fewer syllables and avoid words longer than 3 syllables when simpler alternatives exist.

Focus on:
- Making content easy to read for beginners
- Using simple words and natural tone
- Improving sentence flow and structure
- Always reduce sentence length if possible
- Prefer multiple short sentences over one long sentence

Return ONLY the improved content.
No explanations. No commentary.
If you cannot improve the section without adding notes or lists, return the original content exactly.
"""

REVIEWER_USER = """Review and improve this blog section for SEO quality.

Section heading: {heading}
Target keywords: {keywords}
GEO target question: {geo_target}

CONTENT TO REVIEW:
{content}

IMPROVE by:
1. Remove placeholder text like [INSERT DATA]
2. Replace robotic phrases with natural language
3. Ensure keywords appear naturally 3-5 times, including in intro or conclusion
4. If heading is a question, answer it clearly in the first sentence but don't write heading in section content ever.
5. Vary sentence structure to avoid repetition
6. Ensure the section clearly answers: "{geo_target}"

READABILITY IMPROVEMENTS:
7. Break long sentences into shorter ones
8. Keep most sentences between 6–10 words
9. Replace complex words with simpler alternatives
10. Prefer simple sentence structure (subject + verb + object)
11. Aim for Flesch Reading Ease 80–90
12. Aim for grade level 6–8
13. Preserve section length; do not make the section noticeably shorter than the input
14. Remove any instructions, notes, or meta text from output
15. Avoid passive voice, or starting sentence abnormally

IMPORTANT:
- If a sentence is longer than 12 words, split it when it hurts readability, but keep section length intact
- Simpler is better than detailed
- Avoid words with more than 3 syllables when simpler alternatives exist
- Do not include any notes, analysis, checklists, or bullet lists in the output
- Only return the final revised section text, with no headings or commentary

Return ONLY the improved content.
Keep same structure and similar length.
"""


def _strip_review_notes(text: str) -> str:
    if not isinstance(text, str):
        return text
    cleaned = text.strip()
    if not cleaned:
        return cleaned

    if re.match(r'^(Note:|Notes:|[-*]\s|\d+\.)', cleaned):
        parts = re.split(r'\n\s*\n', cleaned)
        for part in parts:
            part_strip = part.strip()
            if not re.match(r'^(Note:|Notes:|[-*]\s|\d+\.)', part_strip):
                return part_strip
        lines = cleaned.splitlines()
        while lines and re.match(r'^(Note:|Notes:|[-*]\s|\d+\.)', lines[0].strip()):
            lines.pop(0)
        while lines and not lines[0].strip():
            lines.pop(0)
        return '\n'.join(lines).strip()
    return cleaned


async def _review_content(content: str, heading: str, keywords: list[str], geo_target: str) -> str:
    try:
        reviewed = await _chat(
            REVIEWER_SYSTEM,
            REVIEWER_USER.format(
                heading=heading,
                keywords=", ".join(keywords) if keywords else "none",
                geo_target=geo_target,
                content=content,
            ),
            temperature=0.4,
        )
        cleaned = _strip_review_notes(reviewed)
        return cleaned if len(cleaned) > 100 else content
    except Exception:
        return content  # Fall back to original if reviewer fails


# ════════════════════════════════════════════════════════
# META GENERATOR
# ════════════════════════════════════════════════════════

META_SYSTEM = """You are an SEO meta-tag specialist. Return ONLY valid JSON starting with {"""

META_USER = """Topic: {topic}
Title: {title}
Focus Keyword: {focus_keyword}
Summary: {summary}

Return ONLY this JSON:
{{
  "meta_title": "under 60 chars, focus keyword near start, no clickbait",
  "meta_description": "under 155 chars, includes keyword, ends with action",
  "og_title": "under 95 chars",
  "og_description": "under 200 chars",
  "title_variations": [
    "How-to format: How to [achieve result] with [topic]",
    "Number format: X [Things/Ways/Steps] to [result]",
    "Question format: What is [topic] and [benefit]?"
  ]
}}"""


async def generate_meta(title: str, topic: str, focus_keyword: str, content_summary: str) -> dict:
    raw = await _chat(META_SYSTEM,
        META_USER.format(title=title, topic=topic, focus_keyword=focus_keyword, summary=content_summary[:400]),
        temperature=0.4)
    return _extract_json(raw)


# ════════════════════════════════════════════════════════
# INTERNAL LINK SUGGESTER
# ════════════════════════════════════════════════════════

LINKS_SYSTEM = """You are an internal linking SEO expert. Return ONLY a JSON array starting with ["""

LINKS_USER = """Topic: {topic}
Keywords: {keywords}
Excerpt: {excerpt}

Return ONLY a JSON array:
[{{"anchor_text": "phrase to link", "suggested_slug": "/url-slug", "reason": "why this link adds value"}}]
4 items maximum."""


async def suggest_internal_links(topic: str, keywords: list[str], content_excerpt: str) -> list:
    try:
        raw = await _chat(LINKS_SYSTEM,
            LINKS_USER.format(topic=topic, keywords=", ".join(keywords), excerpt=content_excerpt[:800]),
            temperature=0.3)
        result = _extract_json(raw)
        return result if isinstance(result, list) else []
    except Exception:
        return []