"""
기존 가이드 일본어 번역 일괄 생성
실행: python -m pipeline.fill_ja_guides
"""
import os
import time
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


TRANSLATE_PROMPT = """Translate the following Korean restaurant guide content into natural Japanese.

Rules:
- Keep all markdown formatting (headings, bold, lists, tables, etc.)
- Keep [spot:Name] markers exactly as-is — do NOT translate them
- Keep restaurant names in romanized form + Korean in parentheses on first mention
- Keep the tone warm and local
- Do NOT add or remove content. Translate faithfully.
- Output Japanese only. No wrappers, no extra labels.

--- ORIGINAL ---
{content}
--- END ---"""

TRANSLATE_TITLE_PROMPT = """Translate this title into Japanese. Output the Japanese title only — plain text, no markdown, no quotes, no extra text.

Title: {content}"""


def translate(text: str, title_mode: bool = False) -> str:
    if not text or not text.strip():
        return ""
    prompt = TRANSLATE_TITLE_PROMPT if title_mode else TRANSLATE_PROMPT
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt.format(content=text)}]
    )
    return res.choices[0].message.content.strip()


def run():
    data = sb.table("guides").select("id, title, subtitle, intro, body").eq("status", "published").is_("title_ja", "null").execute()
    guides = data.data
    print(f"미번역 가이드: {len(guides)}개\n")

    for i, g in enumerate(guides):
        print(f"[{i+1}/{len(guides)}] {g['title']} 번역 중...")
        try:
            update = {}
            if g.get("title"):
                update["title_ja"] = translate(g["title"], title_mode=True)
                print(f"  title_ja: {update['title_ja'][:40]}")
            if g.get("subtitle"):
                update["subtitle_ja"] = translate(g["subtitle"], title_mode=True)
            if g.get("intro"):
                update["intro_ja"] = translate(g["intro"])
            if g.get("body"):
                print("  body 번역 중...")
                update["body_ja"] = translate(g["body"])

            sb.table("guides").update(update).eq("id", g["id"]).execute()
            print(f"  ✅ 완료")
            time.sleep(1)
        except Exception as e:
            print(f"  ❌ 오류: {e}")

    print("\n전체 완료!")


if __name__ == "__main__":
    run()
