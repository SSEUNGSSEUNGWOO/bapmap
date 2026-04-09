"""
가이드 생성 파이프라인
실행: python -m pipeline.guide.pipeline
"""
import os
from dotenv import load_dotenv
from supabase import create_client
from .recommender import recommender
from .writer import writer
from .eval import eval_agent
from .publish import publish

load_dotenv()

MAX_REVISIONS = 2


def run(
    title: str,
    spot_names: list[str],
    provider: str = "anthropic",
    cover_image: str = "",
    status: str = "draft",
    auto_publish: bool = False,
) -> dict:
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    spots = sb.table("spots").select(
        "english_name, name, category, region, memo, what_to_order, tagline, image_url, subway, price_level, rating"
    ).in_("english_name", spot_names).execute().data

    state = {
        "title": title,
        "spots_data": spots,
        "provider": provider,
        "cover_image": cover_image,
        "status": status,
        "revision_count": 0,
        "eval_feedback": "",
    }

    for attempt in range(MAX_REVISIONS + 1):
        state = writer(state)
        state = eval_agent(state)
        if state.get("approved"):
            break
        if attempt == MAX_REVISIONS:
            print(f"[Pipeline] 최대 재작성 횟수 도달, 마지막 버전 사용")

    if auto_publish:
        state = publish(state)

    return state


def recommend(provider: str = "anthropic", count: int = 5) -> list[dict]:
    state = recommender({"provider": provider, "cluster_count": count})
    return state.get("clusters", [])


if __name__ == "__main__":
    clusters = recommend()
    print("\n추천 클러스터:")
    for i, c in enumerate(clusters):
        print(f"{i+1}. [{c['theme']}] {', '.join(c['spots'])}")
        print(f"   → {c['reason']}")
