"""
구글 리뷰 일본어 번역 일괄 생성
실행: python -m pipeline.fill_ja_reviews
"""
import os
import time
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT = """Translate the following English restaurant review snippets into natural Japanese.
Output a JSON array of strings only — same order, same count as input. No extra text.

Reviews:
{reviews}"""


def translate_reviews(reviews: list[str]) -> list[str]:
    combined = "\n".join(f"{i+1}. {r}" for i, r in enumerate(reviews))
    resp = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT.format(reviews=combined)}],
        temperature=0.3,
    )
    import json
    text = resp.choices[0].message.content.strip()
    # strip markdown code block if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def main():
    rows = (
        sb.table("spots")
        .select("id, english_name, name, google_reviews")
        .not_.is_("google_reviews", "null")
        .is_("google_reviews_ja", "null")
        .execute()
        .data
    )
    print(f"번역 대상: {len(rows)}개")

    for row in rows:
        reviews = row.get("google_reviews")
        if not isinstance(reviews, list) or not reviews:
            continue
        name = row.get("english_name") or row.get("name")
        print(f"  → {name} ({len(reviews)}개 리뷰)")
        try:
            ja = translate_reviews(reviews)
            sb.table("spots").update({"google_reviews_ja": ja}).eq("id", row["id"]).execute()
            time.sleep(0.5)
        except Exception as e:
            print(f"    오류: {e}")

    print("완료")


if __name__ == "__main__":
    main()
