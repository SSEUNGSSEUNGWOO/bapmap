"""가이드 DB 저장 agent."""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def _translate(sb, text: str, title_mode: bool = False) -> str:
    from pipeline.fill_ja_reviews import translate_reviews
    if not text:
        return ""
    try:
        if title_mode:
            results = translate_reviews([text])
            return results[0] if results else ""
        results = translate_reviews([text])
        return results[0] if results else ""
    except Exception as e:
        print(f"[Publish] 번역 실패: {e}")
        return ""


def publish(state: dict) -> dict:
    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    draft = state.get("guide_draft", {})
    spot_names = [s.get("english_name") or s["name"] for s in state.get("spots_data", [])]

    print("[Publish] 일본어 번역 중...")
    guide_data = {
        "slug": draft.get("slug", ""),
        "title": draft.get("title", ""),
        "subtitle": draft.get("subtitle", ""),
        "cover_image": state.get("cover_image", ""),
        "category_tag": draft.get("category_tag", ""),
        "intro": draft.get("intro", ""),
        "body": draft.get("body", ""),
        "spot_slugs": spot_names,
        "status": state.get("status", "draft"),
        "title_ja": _translate(sb, draft.get("title", ""), title_mode=True),
        "subtitle_ja": _translate(sb, draft.get("subtitle", ""), title_mode=True),
        "intro_ja": _translate(sb, draft.get("intro", "")),
        "body_ja": _translate(sb, draft.get("body", "")),
    }

    sb.table("guides").upsert(guide_data).execute()
    print(f"[Publish] ✅ '{guide_data['title']}' 저장 완료 (slug: {guide_data['slug']})")
    return {**state, "published": True, "guide_data": guide_data}
