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
        print(f"\n{i+1}. [{c['theme']}]")
        print(f"   제목: {c.get('title', '')}")
        print(f"   스팟: {', '.join(c['spots'])}")
        print(f"   이유: {c['reason']}")

    print("\n0. 직접 입력")
    choice = input("\n번호 선택: ").strip()

    if choice == "0":
        spot_input = input("스팟 english_name (쉼표로 구분): ")
        spot_names = [s.strip() for s in spot_input.split(",") if s.strip()]
        title = input("제목: ").strip()
    else:
        selected = clusters[int(choice) - 1]
        spot_names = selected["spots"]
        title = selected.get("title", selected["theme"])
        print(f"\n선택: {title}")

    cover = input("커버 이미지 URL (없으면 엔터): ").strip()
    status = input("상태 [draft/published] (기본 draft): ").strip() or "draft"

    print()
    state = run(title=title, spot_names=spot_names, cover_image=cover, status=status, auto_publish=True)
    d = state["guide_draft"]
    print(f"\n✅ 저장 완료")
    print(f"   제목: {d['title']}")
    print(f"   슬러그: {d['slug']}")
    print(f"   점수: {state.get('eval_score', 0)}/50")
