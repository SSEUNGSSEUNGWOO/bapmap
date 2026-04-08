import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent.parent))
load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))


def spot_fetch(state: dict) -> dict:
    guide_id = state.get("guide_id")
    spot_ids = state.get("spot_ids", [])

    if guide_id:
        # 가이드에서 spot_slugs 가져와서 스팟 조회
        guide_res = sb.table("guides").select("*").eq("id", guide_id).single().execute()
        guide = guide_res.data
        if not guide:
            print(f"[SpotFetch] 가이드 없음: {guide_id}")
            return {**state, "spots_data": [], "guide_data": None}

        spot_names = guide.get("spot_slugs", [])
        spots = []
        for name in spot_names:
            # 영어 이름 우선, 없으면 한국어 이름으로
            res = sb.table("spots").select("*").ilike("english_name", f"%{name}%").limit(1).execute()
            if not res.data:
                res = sb.table("spots").select("*").ilike("name", f"%{name}%").limit(1).execute()
            if res.data:
                spots.append(res.data[0])

        print(f"[SpotFetch] 가이드 '{guide['title']}' → {len(spots)}개 스팟 로드")
        return {**state, "spots_data": spots, "guide_data": guide}

    elif spot_ids:
        res = sb.table("spots").select("*").in_("id", spot_ids).execute()
        spots = res.data or []
    else:
        res = sb.table("spots").select("*").eq("status", "업로드완료").limit(5).execute()
        spots = res.data or []

    print(f"[SpotFetch] {len(spots)}개 스팟 로드")
    return {**state, "spots_data": spots, "guide_data": None}
