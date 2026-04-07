# # """
# # SEO Analyzer Service
# # --------------------
# # Computes keyword density, heading hierarchy, readability scores.
# # Strips markdown before textstat analysis to fix 0-score bug.
# # """
# # import re
# # from collections import Counter


# # def _strip_markdown(text: str) -> str:
# #     """Remove markdown so textstat reads prose only."""
# #     # Remove tables (lines with |)
# #     text = re.sub(r'\|[^\n]+\|', '', text)
# #     # Remove markdown bold/italic
# #     text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
# #     # Remove headings #
# #     text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
# #     # Remove bullet points
# #     text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
# #     # Remove [INSERT DATA] placeholders
# #     text = re.sub(r'\[INSERT[^\]]*\]', '', text)
# #     # Remove URLs
# #     text = re.sub(r'https?://\S+', '', text)
# #     # Remove extra symbols
# #     text = re.sub(r'[`|>_~]', '', text)
# #     # Collapse multiple spaces/newlines
# #     text = re.sub(r'\n{2,}', '\n', text)
# #     text = re.sub(r'[ \t]{2,}', ' ', text)
# #     return text.strip()


# # def compute_readability(text: str) -> dict:
# #     """Return Flesch, FK-Grade, Gunning Fog, and estimated reading time."""
# #     try:
# #         import textstat
# #         clean = _strip_markdown(text)
# #         if len(clean.split()) < 30:
# #             raise ValueError("Not enough words")
# #         words = len(clean.split())
# #         return {
# #             "flesch_reading_ease": round(textstat.flesch_reading_ease(clean), 2),
# #             "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(clean), 2),
# #             "gunning_fog": round(textstat.gunning_fog(clean), 2),
# #             "reading_time_minutes": round(words / 200, 2),
# #         }
# #     except Exception as e:
# #         print(f"Readability error: {e}")
# #         return {
# #             "flesch_reading_ease": 0.0,
# #             "flesch_kincaid_grade": 0.0,
# #             "gunning_fog": 0.0,
# #             "reading_time_minutes": 0.0,
# #         }


# # def compute_keyword_density(text: str, keywords: list[str]) -> dict:
# #     if not text or not keywords:
# #         return {}
# #     clean = _strip_markdown(text)
# #     words = re.findall(r"\b\w+\b", clean.lower())
# #     total = len(words)
# #     if total == 0:
# #         return {}
# #     result = {}
# #     for kw in keywords:
# #         kw_lower = kw.lower()
# #         kw_parts = kw_lower.split()
# #         if len(kw_parts) == 1:
# #             count = words.count(kw_parts[0])
# #         else:
# #             count = clean.lower().count(kw_lower)
# #         result[kw] = round((count / total) * 100, 3)
# #     return result


# # def score_keyword_density(densities: dict) -> float:
# #     if not densities:
# #         return 0.0
# #     ideal = sum(1 for d in densities.values() if 0.5 <= d <= 2.5)
# #     low = sum(1 for d in densities.values() if 0.2 <= d < 0.5)
# #     score = (ideal * 100 + low * 50) / len(densities)
# #     return round(min(100, score), 1)


# # def validate_heading_hierarchy(sections: list[dict]) -> tuple:
# #     issues = []
# #     if not sections:
# #         return 0.0, ["No sections found"]

# #     sorted_sections = sorted(sections, key=lambda s: s["order_index"])
# #     levels = [s["heading_level"] for s in sorted_sections]

# #     if levels[0] != 1:
# #         issues.append("⚠ Post should start with an H1 heading")

# #     h1_count = levels.count(1)
# #     if h1_count == 0:
# #         issues.append("⚠ No H1 heading found")
# #     elif h1_count > 1:
# #         issues.append(f"⚠ Multiple H1 headings ({h1_count}). Use only one H1.")

# #     for i in range(1, len(levels)):
# #         if levels[i] - levels[i - 1] > 1:
# #             issues.append(f"⚠ Heading jump at section {i+1}: H{levels[i-1]} → H{levels[i]}")

# #     score = max(0.0, 100.0 - (len(issues) * 20))
# #     return round(score, 1), issues


# # def compute_overall_seo_score(
# #     keyword_density_score: float,
# #     heading_hierarchy_score: float,
# #     flesch_reading_ease: float,
# #     word_count: int,
# #     meta_description,
# #     meta_title,
# # ) -> float:
# #     readability_score = max(0, min(100, 100 - abs(flesch_reading_ease - 60))) if flesch_reading_ease else 50

# #     if 800 <= word_count <= 2500:
# #         wc_score = 100.0
# #     elif word_count < 800:
# #         wc_score = (word_count / 800) * 100
# #     else:
# #         wc_score = max(60, 100 - ((word_count - 2500) / 100))

# #     meta_score = 0.0
# #     if meta_title and 30 <= len(meta_title) <= 60:
# #         meta_score += 50
# #     elif meta_title:
# #         meta_score += 25
# #     if meta_description and 120 <= len(meta_description) <= 160:
# #         meta_score += 50
# #     elif meta_description:
# #         meta_score += 25

# #     overall = (
# #         keyword_density_score * 0.25
# #         + heading_hierarchy_score * 0.20
# #         + readability_score * 0.20
# #         + wc_score * 0.15
# #         + meta_score * 0.20
# #     )
# #     return round(min(100, overall), 1)


# # def analyze_post(full_text, keywords, sections, meta_title=None, meta_description=None):
# #     readability = compute_readability(full_text)
# #     densities = compute_keyword_density(full_text, keywords)
# #     kd_score = score_keyword_density(densities)
# #     hh_score, hh_issues = validate_heading_hierarchy(sections)
# #     word_count = len(_strip_markdown(full_text).split()) if full_text else 0

# #     overall = compute_overall_seo_score(
# #         kd_score, hh_score,
# #         readability["flesch_reading_ease"],
# #         word_count, meta_description, meta_title,
# #     )

# #     return {
# #         **readability,
# #         "keyword_density_score": kd_score,
# #         "heading_hierarchy_score": hh_score,
# #         "overall_seo_score": overall,
# #         "keyword_densities": densities,
# #         "heading_issues": hh_issues,
# #     }


# """
# SEO Analyzer Service
# --------------------
# Computes keyword density, heading hierarchy, readability scores.
# Strips markdown before textstat analysis to fix 0-score bug.
# """
# import re
# from collections import Counter


# def _strip_markdown(text: str) -> str:
#     """Remove markdown so textstat reads prose only."""
#     text = re.sub(r'\|[^\n]+\|', '', text)
#     text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
#     text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
#     text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
#     text = re.sub(r'\[INSERT[^\]]*\]', '', text)
#     text = re.sub(r'https?://\S+', '', text)
#     text = re.sub(r'[`|>_~]', '', text)
#     text = re.sub(r'\n{2,}', '\n', text)
#     text = re.sub(r'[ \t]{2,}', ' ', text)
#     return text.strip()


# def _build_full_text(sections: list[dict]) -> str:
#     """
#     Concatenate ALL section content in order to get the true full blog text.
#     Each section contributes its heading + content.
#     """
#     sorted_sections = sorted(sections, key=lambda s: s.get("order_index", 0))
#     parts = []
#     for s in sorted_sections:
#         heading = s.get("heading", "")
#         content = s.get("content", "") or ""
#         if heading:
#             parts.append(f"{'#' * s.get('heading_level', 2)} {heading}")
#         if content:
#             parts.append(content)
#     return "\n\n".join(parts)


# def compute_readability(text: str) -> dict:
#     """Return Flesch, FK-Grade, Gunning Fog, and estimated reading time."""
#     try:
#         import textstat
#         clean = _strip_markdown(text)
#         if len(clean.split()) < 30:
#             raise ValueError("Not enough words")
#         words = len(clean.split())
#         return {
#             "flesch_reading_ease": round(textstat.flesch_reading_ease(clean), 2),
#             "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(clean), 2),
#             "gunning_fog": round(textstat.gunning_fog(clean), 2),
#             "reading_time_minutes": round(words / 200, 2),
#         }
#     except Exception as e:
#         print(f"Readability error: {e}")
#         return {
#             "flesch_reading_ease": 0.0,
#             "flesch_kincaid_grade": 0.0,
#             "gunning_fog": 0.0,
#             "reading_time_minutes": 0.0,
#         }


# def compute_keyword_density(text: str, keywords: list[str]) -> dict:
#     if not text or not keywords:
#         return {}
#     clean = _strip_markdown(text)
#     words = re.findall(r"\b\w+\b", clean.lower())
#     total = len(words)
#     if total == 0:
#         return {}
#     result = {}
#     for kw in keywords:
#         kw_lower = kw.lower()
#         kw_parts = kw_lower.split()
#         if len(kw_parts) == 1:
#             count = words.count(kw_parts[0])
#         else:
#             count = clean.lower().count(kw_lower)
#         result[kw] = round((count / total) * 100, 3)
#     return result


# def score_keyword_density(densities: dict) -> float:
#     if not densities:
#         return 0.0
#     ideal = sum(1 for d in densities.values() if 0.5 <= d <= 2.5)
#     low = sum(1 for d in densities.values() if 0.2 <= d < 0.5)
#     score = (ideal * 100 + low * 50) / len(densities)
#     return round(min(100, score), 1)


# def validate_heading_hierarchy(sections: list[dict]) -> tuple:
#     issues = []
#     if not sections:
#         return 0.0, ["No sections found"]

#     sorted_sections = sorted(sections, key=lambda s: s["order_index"])
#     levels = [s["heading_level"] for s in sorted_sections]

#     if levels[0] != 1:
#         issues.append("⚠ Post should start with an H1 heading")

#     h1_count = levels.count(1)
#     if h1_count == 0:
#         issues.append("⚠ No H1 heading found")
#     elif h1_count > 1:
#         issues.append(f"⚠ Multiple H1 headings ({h1_count}). Use only one H1.")

#     for i in range(1, len(levels)):
#         if levels[i] - levels[i - 1] > 1:
#             issues.append(f"⚠ Heading jump at section {i+1}: H{levels[i-1]} → H{levels[i]}")

#     score = max(0.0, 100.0 - (len(issues) * 20))
#     return round(score, 1), issues


# def compute_overall_seo_score(
#     keyword_density_score: float,
#     heading_hierarchy_score: float,
#     flesch_reading_ease: float,
#     word_count: int,
#     meta_description,
#     meta_title,
# ) -> float:
#     readability_score = max(0, min(100, 100 - abs(flesch_reading_ease - 60))) if flesch_reading_ease else 50

#     if 800 <= word_count <= 2500:
#         wc_score = 100.0
#     elif word_count < 800:
#         wc_score = (word_count / 800) * 100
#     else:
#         wc_score = max(60, 100 - ((word_count - 2500) / 100))

#     meta_score = 0.0
#     if meta_title and 30 <= len(meta_title) <= 60:
#         meta_score += 50
#     elif meta_title:
#         meta_score += 25
#     if meta_description and 120 <= len(meta_description) <= 160:
#         meta_score += 50
#     elif meta_description:
#         meta_score += 25

#     overall = (
#         keyword_density_score * 0.25
#         + heading_hierarchy_score * 0.20
#         + readability_score * 0.20
#         + wc_score * 0.15
#         + meta_score * 0.20
#     )
#     return round(min(100, overall), 1)


# def analyze_post(full_text, keywords, sections, meta_title=None, meta_description=None):
#     """
#     Analyze the full blog post.
#     - full_text: may be a single section or partial — we always rebuild from sections
#     - sections: list of all section dicts with heading, content, order_index, heading_level
#     """
#     # Always build complete text from ALL sections so word count is accurate
#     if sections:
#         combined_text = _build_full_text(sections)
#     else:
#         combined_text = full_text or ""

#     readability = compute_readability(combined_text)
#     densities = compute_keyword_density(combined_text, keywords)
#     kd_score = score_keyword_density(densities)
#     hh_score, hh_issues = validate_heading_hierarchy(sections)

#     # Word count from full combined text (all sections, markdown stripped)
#     word_count = len(_strip_markdown(combined_text).split()) if combined_text else 0

#     overall = compute_overall_seo_score(
#         kd_score, hh_score,
#         readability["flesch_reading_ease"],
#         word_count, meta_description, meta_title,
#     )

#     return {
#         **readability,
#         "keyword_density_score": kd_score,
#         "heading_hierarchy_score": hh_score,
#         "overall_seo_score": overall,
#         "keyword_densities": densities,
#         "heading_issues": hh_issues,
#         "word_count": word_count,  # total across all sections
#     }

"""
SEO Analyzer Service
--------------------
Computes keyword density, heading hierarchy, readability scores.
Strips markdown before textstat analysis to fix 0-score bug.
"""

"""
SEO Analyzer Service
--------------------
Computes keyword density, heading hierarchy, readability scores.
Strips markdown before textstat analysis to fix 0-score bug.
"""

import re
import textstat
import logging
from collections import Counter

# --- Setup Console Logging ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("SEO_Analyzer")

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _strip_markdown(text: str) -> str:
    """Remove markdown formatting so textstat reads clean prose only."""
    if not text:
        return ""
    text = re.sub(r'\|[^\n]+\|', '', text)
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*[-*•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\[INSERT[^\]]*\]', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[`|>_~]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def _normalize_whitespace(text: str) -> str:
    """Flatten all whitespace to single spaces for phrase matching."""
    return re.sub(r'\s+', ' ', text).strip()


def _build_full_text(sections: list[dict]) -> str:
    """Concatenate ALL section content in order to get the true full blog text."""
    sorted_sections = sorted(sections, key=lambda s: s.get("order_index", 0))
    parts = []
    for s in sorted_sections:
        heading = s.get("heading", "")
        content = s.get("content", "") or ""
        if heading:
            level = s.get("heading_level", 2)
            parts.append(f"{'#' * level} {heading}")
        if content:
            parts.append(content)
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Readability
# ---------------------------------------------------------------------------

def compute_readability(text: str) -> dict:
    """Return Flesch, FK-Grade, Gunning Fog, and estimated reading time via textstat."""
    clean = _strip_markdown(text)
    word_list = clean.split()
    word_count = len(word_list)

    print("\n" + "="*40)
    print("READABILITY DEBUGGER")
    print("="*40)
    print(f"CLEAN TEXT SNIPPET: {clean[:150]}...")
    print(f"DEBUG WORD COUNT:   {word_count}")

    try:
        import textstat

        print(f"DEBUG SENTENCES:    {textstat.sentence_count(clean)}")
        print(f"DEBUG SYLLABLES:    {textstat.syllable_count(clean)}")

        results = {
            "flesch_reading_ease":  round(textstat.flesch_reading_ease(clean), 2),
            "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(clean), 2),
            "gunning_fog":          round(textstat.gunning_fog(clean), 2),
            "reading_time_minutes": round(word_count / 200, 2),
        }
        print(f"STATUS: Success")
        print("="*40 + "\n")
        return results

    except Exception as e:
        logger.error(f"Readability Error: {e}")
        print(f"STATUS: FAILED")
        print("="*40 + "\n")
        return {
            "flesch_reading_ease":  0.0,
            "flesch_kincaid_grade": 0.0,
            "gunning_fog":          0.0,
            "reading_time_minutes": round(word_count / 200, 2) if word_count > 0 else 0.0,
        }


# ---------------------------------------------------------------------------
# Keyword density
# ---------------------------------------------------------------------------

def compute_keyword_density(text: str, keywords: list[str]) -> dict:
    if not text or not keywords:
        return {}

    clean = _strip_markdown(text)
    clean_normalized = _normalize_whitespace(clean).lower()
    words = re.findall(r"\b\w+\b", clean_normalized)
    total = len(words)

    if total == 0:
        return {}

    result = {}
    for kw in keywords:
        kw_lower = kw.lower().strip()
        kw_parts = kw_lower.split()

        if len(kw_parts) == 1:
            count = words.count(kw_parts[0])
        else:
            count = clean_normalized.count(kw_lower)

        result[kw] = round((count / total) * 100, 3)
        logger.info(f"Keyword: '{kw}' | Density: {result[kw]}%")

    return result


def score_keyword_density(densities: dict) -> float:
    if not densities:
        return 0.0

    ideal = sum(1 for d in densities.values() if 0.3 <= d <= 3.0)
    low   = sum(1 for d in densities.values() if 0.1 <= d < 0.3)
    score = (ideal * 100 + low * 40) / len(densities)
    return round(min(100.0, score), 1)


# ---------------------------------------------------------------------------
# Heading hierarchy
# ---------------------------------------------------------------------------

def validate_heading_hierarchy(sections: list[dict], has_separate_title: bool = False) -> tuple:
    issues = []
    if not sections:
        return 0.0, ["No sections found"]

    sorted_sections = sorted(sections, key=lambda s: s["order_index"])
    levels = [s["heading_level"] for s in sorted_sections]

    expected_start = 1 if has_separate_title else 2

    if levels[0] != expected_start:
        issues.append(f"⚠ Post should start with an H{expected_start} heading (found H{levels[0]})")

    if not has_separate_title:
        h1_count = levels.count(1)
        if h1_count == 0:
            issues.append("⚠ No H1 heading found")
        elif h1_count > 1:
            issues.append(f"⚠ Multiple H1 headings ({h1_count}). Use only one H1.")

    for i in range(1, len(levels)):
        jump = levels[i] - levels[i - 1]
        if jump > 1:
            issues.append(f"⚠ Heading jump at section {i + 1}: H{levels[i - 1]} → H{levels[i]}")

    score = max(0.0, 100.0 - (len(issues) * 20))
    return round(score, 1), issues


# ---------------------------------------------------------------------------
# Overall SEO score
# ---------------------------------------------------------------------------

def compute_overall_seo_score(
    keyword_density_score: float,
    heading_hierarchy_score: float,
    flesch_reading_ease,
    word_count: int,
    meta_description,
    meta_title,
) -> float:
    ease_val = flesch_reading_ease if flesch_reading_ease is not None else 50.0
    delta = abs(ease_val - 60.0)

    if delta <= 10:
        readability_score = 100
    elif delta <= 20:
        readability_score = 80
    else:
        readability_score = max(60, 100 - delta * 2)

    if 1100 <= word_count <= 2000:
        wc_score = 100
    elif 800 <= word_count < 1100:
        wc_score = 80
    elif 2000 < word_count <= 3000:
        wc_score = 85
    else:
        wc_score = max(50, (word_count / 1200) * 100 if word_count > 0 else 0)

    meta_score = 0.0
    if meta_title:
        meta_score += 50.0 if 30 <= len(meta_title) <= 60 else 20.0
    if meta_description:
        meta_score += 50.0 if 120 <= len(meta_description) <= 160 else 20.0

    overall = (
        keyword_density_score     * 0.25
        + heading_hierarchy_score * 0.20
        + readability_score       * 0.20
        + wc_score                * 0.15
        + meta_score              * 0.20
    )
    return round(min(100.0, overall), 1)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def analyze_post(
    full_text,
    keywords,
    sections,
    meta_title=None,
    meta_description=None,
    has_separate_title: bool = False,
):
    logger.info("--- SEO ANALYSIS START ---")

    if sections:
        combined_text = _build_full_text(sections)
    else:
        combined_text = full_text or ""

    readability      = compute_readability(combined_text)
    densities        = compute_keyword_density(combined_text, keywords)
    kd_score         = score_keyword_density(densities)
    hh_score, hh_issues = validate_heading_hierarchy(sections, has_separate_title=has_separate_title)

    word_count = len(_strip_markdown(combined_text).split()) if combined_text else 0

    overall = compute_overall_seo_score(
        kd_score,
        hh_score,
        readability["flesch_reading_ease"],
        word_count,
        meta_description,
        meta_title,
    )

    return {
        "flesch_reading_ease":     readability["flesch_reading_ease"],
        "flesch_kincaid_grade":    readability["flesch_kincaid_grade"],
        "gunning_fog":             readability["gunning_fog"],
        "reading_time_minutes":    readability["reading_time_minutes"],
        "keyword_density_score":   kd_score,
        "keyword_densities":       densities,
        "heading_hierarchy_score": hh_score,
        "heading_issues":          hh_issues,
        "overall_seo_score":       overall,
        "word_count":              word_count,
    }