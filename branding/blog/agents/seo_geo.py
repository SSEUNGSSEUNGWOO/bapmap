import os
import json
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPT = """You are an SEO and GEO (Generative Engine Optimization) specialist for a Korean food travel blog.

Given this blog post draft, return a JSON object with:
- "title": SEO-optimized title (50-60 chars, include main keyword)
- "meta_description": 150-160 chars, compelling, includes keyword
- "slug": URL-friendly slug (lowercase, hyphens)
- "keywords": list of 5 target keywords
- "geo_suggestions": list of 2-3 specific improvements to make the post more likely to be cited by AI engines (ChatGPT, Perplexity, etc.) — e.g. add specific facts/numbers, ensure prices are mentioned, make the opening sentence answer a common question directly. DO NOT add FAQ sections or bullet point lists — keep the prose style intact.
- "revised_draft": the full post with geo_suggestions applied. Keep the human voice and prose structure. Do NOT add FAQ sections, bullet lists, or any templated boxes.

Post type: {post_type}
Topic: {topic}

Draft:
{draft}

Return JSON only."""


def seo_geo(state: dict) -> dict:
    print("[SEO/GEO] 최적화 중...")
    res = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT.format(
            post_type=state.get("post_type", ""),
            topic=state.get("topic", ""),
            draft=state.get("draft", ""),
        )}],
    )
    try:
        text = res.content[0].text
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
    except Exception:
        print("[SEO/GEO] JSON 파싱 실패, 원본 유지")
        return state

    return {
        **state,
        "title": data.get("title", ""),
        "meta_description": data.get("meta_description", ""),
        "slug": data.get("slug", ""),
        "keywords": data.get("keywords", []),
        "draft": data.get("revised_draft", state.get("draft", "")),
    }
