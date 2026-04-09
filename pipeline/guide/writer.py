"""가이드 본문 작성 agent."""
import json
from .utils import generate

PROMPT = """You are a travel guide writer for Bapmap — a Seoul food guide for English-speaking travelers who love K-culture.

Write guide content for the spots below. The title is already set.

VOICE:
- Like a well-traveled friend who actually lives in Seoul, not a tour guide
- Specific and honest — name dishes, mention prices, note wait times or quirks
- Short punchy sentences for key facts. Longer when setting context
- K-pop/celebrity connections: mention them matter-of-factly, not breathlessly

BANNED:
- "hidden gem", "must-visit", "culinary journey", "vibrant", "nestled"
- "Our first stop takes us to", "a stone's throw", "a haven for"
- Any sentence that could appear on every food blog ever
- Generic closing encouragement

FORMAT:
- Use [spot:English Name] to embed each spot card
- Write 3-4 sentences of context BEFORE each [spot:] tag
- End with one practical tip paragraph (timing, reservations, logistics)

Title: {title}

Spots:
{spots_info}

Return JSON only:
{{
  "slug": "url-friendly-slug",
  "subtitle": "1-2 sentences. Specific hook.",
  "category_tag": "1-3 tags e.g. K-pop, Bakery, Celebrity",
  "intro": "2-3 sentences. Why this guide. What connects these spots.",
  "body": "full body with [spot:] tags"
}}"""


def writer(state: dict) -> dict:
    title = state.get("title", "")
    spots = state.get("spots_data", [])
    feedback = state.get("eval_feedback", "")

    spots_info = "\n\n".join(
        f"- {s.get('english_name') or s['name']} ({s.get('category','')}, {s.get('region','')})\n  memo: {s.get('memo','')}"
        for s in spots
    )

    prompt = PROMPT.format(title=title, spots_info=spots_info)
    if feedback:
        prompt += f"\n\nPrevious eval feedback to fix:\n{feedback}"

    provider = state.get("provider", "anthropic")
    revision = state.get("revision_count", 0)
    print(f"[Writer] 가이드 작성 중... (revision #{revision}, {provider})")

    raw = generate(prompt, provider, max_tokens=2500)
    raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(raw)
    data["title"] = title

    return {**state, "guide_draft": data, "revision_count": revision + 1}
