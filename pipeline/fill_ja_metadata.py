"""
what_to_order 일본어 번역 일괄 생성
실행: python -m pipeline.fill_ja_metadata
"""
import os
import time
import json
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def translate_what_to_order(items: list) -> list:
    if not items:
        return []
    text = "\n".join(f"- {item}" for item in items)
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=300,
        messages=[{"role": "user", "content": f"""Translate these Korean restaurant menu recommendations into Japanese.
Keep the format: Japanese description + Korean name in parentheses if present.
Return as JSON array of strings only.

{text}"""}]
    )
    content = res.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())


def run():
    data = sb.table("spots").select("id, english_name, name, what_to_order").eq("status", "업로드완료").is_("what_to_order_ja", "null").execute()
    spots = data.data
    print(f"what_to_order_ja 미생성: {len(spots)}개\n")

    for i, spot in enumerate(spots):
        name = spot.get("english_name") or spot["name"]
        items = spot.get("what_to_order") or []
        if not items:
            print(f"[{i+1}/{len(spots)}] {name} — what_to_order 없음, 스킵")
            continue
        print(f"[{i+1}/{len(spots)}] {name} 번역 중...")
        try:
            translated = translate_what_to_order(items)
            sb.table("spots").update({"what_to_order_ja": translated}).eq("id", spot["id"]).execute()
            print(f"  ✅ 완료")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print("\n전체 완료!")


if __name__ == "__main__":
    run()
