"""
Korean memo → English one-liner tagline 생성
"""
import os, time, json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import anthropic
from supabase import create_client

sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
claude = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

PROMPT = """You write one-liner taglines for a Korean food guide targeting English-speaking travelers.

Rules:
- 1 sentence, max 8 words
- Punchy and specific — no generic praise
- Focus on ONE thing: timing, vibe, price, wait, what to order
- Sounds like a friend's tip, not a review
- No emojis, no exclamation marks

Examples of good taglines:
- "Always a line. Always worth it."
- "Order the bone broth. Skip everything else."
- "Cheap, fast, no-frills. Perfect after midnight."
- "Locals only. No English menu."
- "The pork belly hits different here."

Spot info:
Name: {name}
City: {city}
Category: {category}
Memo (Korean): {memo}

Return ONLY the tagline, nothing else."""


def generate_tagline(spot: dict) -> str:
    msg = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=60,
        messages=[{
            "role": "user",
            "content": PROMPT.format(
                name=spot.get('english_name') or spot['name'],
                city=spot['city'],
                category=spot['category'],
                memo=spot['memo'].strip()
            )
        }]
    )
    return msg.content[0].text.strip().strip('"')


def main():
    res = sb.table('spots') \
        .select('id, name, english_name, city, category, memo, tagline') \
        .not_.is_('memo', 'null') \
        .eq('status', '업로드완료') \
        .execute()

    spots = res.data
    # 이미 tagline 있는 건 스킵
    todo = [s for s in spots if not s.get('tagline')]
    print(f"총 {len(spots)}개 중 {len(todo)}개 생성 필요")

    for i, spot in enumerate(todo):
        try:
            tagline = generate_tagline(spot)
            sb.table('spots').update({'tagline': tagline}).eq('id', spot['id']).execute()
            print(f"[{i+1}/{len(todo)}] {spot.get('english_name') or spot['name']} → {tagline}")
            time.sleep(0.3)
        except Exception as e:
            print(f"[ERROR] {spot['name']}: {e}")

    print("완료")


if __name__ == '__main__':
    main()
