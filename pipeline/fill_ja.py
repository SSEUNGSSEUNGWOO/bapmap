"""
기존 스팟 일본어 콘텐츠 일괄 생성 (영어 글 → GPT-4o-mini 번역)
실행: python -m pipeline.fill_ja
"""
import os
import time
from supabase import create_client
from dotenv import load_dotenv
from pipeline.generator import generate_post_ja

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))


def run():
    data = sb.table("spots").select("*").eq("status", "업로드완료").is_("content_ja", "null").execute()
    spots = data.data
    print(f"일본어 미생성 스팟: {len(spots)}개\n")

    for i, spot in enumerate(spots):
        name = spot.get("english_name") or spot["name"]
        print(f"[{i+1}/{len(spots)}] {name} 생성 중...")
        try:
            english_content = spot.get("content", "")
            if not english_content:
                print(f"  ⚠️ 영어 콘텐츠 없음, 스킵")
                continue
            content_ja = generate_post_ja(english_content)
            sb.table("spots").update({"content_ja": content_ja}).eq("id", spot["id"]).execute()
            print(f"  ✅ 완료 ({len(content_ja)}자)")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print("\n전체 완료!")


if __name__ == "__main__":
    run()
