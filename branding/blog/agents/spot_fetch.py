import os
import sys
from dotenv import load_dotenv
from supabase import create_client

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent.parent.parent))
load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))


def spot_fetch(state: dict) -> dict:
    ids = state.get("spot_ids", [])

    if ids:
        res = sb.table("spots").select("*").in_("id", ids).execute()
    else:
        res = sb.table("spots") \
            .select("*") \
            .eq("status", "업로드완료") \
            .limit(5) \
            .execute()

    spots = res.data or []
    print(f"[SpotFetch] {len(spots)}개 스팟 로드")
    return {**state, "spots_data": spots}
