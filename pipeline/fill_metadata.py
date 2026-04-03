"""
기존 스팟들에 what_to_order, good_for 채우기
실행: python -m pipeline.fill_metadata
"""
import os
import time
from supabase import create_client
from dotenv import load_dotenv
from pipeline.generator import generate_metadata

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))


def run():
    spots = sb.table("spots").select("*").eq("status", "업로드완료").execute().data
    targets = [s for s in spots if not s.get("what_to_order") or len(s.get("what_to_order", [])) == 0]
    print(f"\n대상: {len(targets)}개\n")

    for i, spot in enumerate(targets):
        name = spot.get("english_name") or spot["name"]
        print(f"[{i+1}/{len(targets)}] {name}")
        try:
            meta = generate_metadata(spot)
            sb.table("spots").update({
                "what_to_order": meta.get("what_to_order", []),
                "good_for": meta.get("good_for", []),
            }).eq("id", spot["id"]).execute()
            print(f"  ✅ {meta.get('good_for', [])}")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ❌ {e}")

    print(f"\n완료!")


if __name__ == "__main__":
    run()
