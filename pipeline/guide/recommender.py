"""
DB 스팟 전체를 보고 가이드로 묶을만한 클러스터 추천.
실행: python -m pipeline.guide.recommender
"""
import os
import json
from dotenv import load_dotenv
from supabase import create_client
from .utils import generate

load_dotenv()


def recommender(state: dict) -> dict:
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    spots = sb.table("spots").select(
        "id, english_name, name, category, region, city, memo, tagline"
    ).eq("status", "업로드완료").execute().data

    # 이미 가이드에 사용된 스팟 제외
    guides = sb.table("guides").select("spot_slugs").execute().data
    used = {name for g in guides for name in (g.get("spot_slugs") or [])}
    spots = [s for s in spots if (s.get("english_name") or s["name"]) not in used]
    print(f"[Recommender] 미사용 스팟 {len(spots)}개로 추천")

    spots_summary = "\n".join(
        f"- {s.get('english_name') or s['name']} | {s.get('category','')} | {s.get('region') or s.get('city','')} | {(s.get('memo') or '')[:120]}"
        for s in spots
    )

    provider = state.get("provider", "anthropic")
    count = state.get("cluster_count", 5)

    prompt = f"""You are a Seoul travel guide editor for Bapmap.

Below is the full list of spots in the database. Group them into {count} thematic guide clusters that would make great standalone guides for English-speaking travelers interested in K-culture, food, and Seoul life.

Criteria for a good cluster:
- 3-5 spots that share a clear theme (K-pop connection, neighborhood, cuisine type, occasion, etc.)
- Each spot should add something different — avoid redundancy
- Prioritize clusters with K-pop/K-drama/celebrity connections when possible
- The theme should be specific enough to be useful, not just "good restaurants in Seoul"

Spots:
{spots_summary}

Return a JSON array of {count} clusters:
[
  {{
    "theme": "short theme name",
    "reason": "1 sentence why these spots work together",
    "spots": ["English Name 1", "English Name 2", ...]
  }}
]

Return JSON only."""

    print(f"[Recommender] 클러스터 추천 중... ({provider})")
    raw = generate(prompt, provider, max_tokens=2000)
    raw = raw.strip()
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    # JSON 배열만 추출
    start = raw.find("[")
    end = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    clusters = json.loads(raw)
    print(f"[Recommender] {len(clusters)}개 클러스터 추천됨")
    for c in clusters:
        print(f"  · {c['theme']}: {', '.join(c['spots'])}")

    return {**state, "clusters": clusters, "spots_db": spots}


if __name__ == "__main__":
    result = recommender({"provider": "anthropic", "cluster_count": 5})
    print(json.dumps(result["clusters"], ensure_ascii=False, indent=2))
