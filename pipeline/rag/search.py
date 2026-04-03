"""
Stage 4: Search
자연어 쿼리 → 임베딩 → pgvector 유사도 검색 → Claude 답변 생성
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from supabase import create_client

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

EMBED_MODEL = "text-embedding-3-small"


def embed_query(query: str) -> list[float]:
    res = openai_client.embeddings.create(
        input=[query.replace("\n", " ")],
        model=EMBED_MODEL,
    )
    return res.data[0].embedding


def similarity_search(query_embedding: list[float], threshold: float = 0.3, count: int = 8) -> list[dict]:
    res = sb.rpc("match_spots", {
        "query_embedding": query_embedding,
        "match_threshold": threshold,
        "match_count": count,
    }).execute()
    return res.data or []


def build_context(spots: list[dict]) -> str:
    lines = []
    for s in spots:
        name = s.get("english_name") or s.get("name", "")
        status = s.get("status", "")
        sim = round(s.get("similarity", 0), 3)

        if status == "업로드완료":
            lines.append(
                f"[{name}] ({s.get('category', '')} · {s.get('region') or s.get('city')} · "
                f"★{s.get('rating', '')} · {s.get('price_level', '')} · 🚇{s.get('subway', '')})\n"
                f"  slug: {name.lower().replace(' ', '-')}\n"
                f"  similarity: {sim}"
            )
        else:
            lines.append(
                f"[{name}] — NOT YET PUBLISHED (coming soon)\n"
                f"  Location: {s.get('region') or s.get('city')}\n"
                f"  Category: {s.get('category', '')}\n"
                f"  similarity: {sim}"
            )
    return "\n\n".join(lines)


SYSTEM_PROMPT = """You are Bapmap's food concierge — a Korean local food expert helping English-speaking tourists find the best places to eat in Korea.

You have access to a curated list of spots retrieved from the Bapmap database.

Rules:
- Recommend spots from the retrieved results. Don't make up places.
- For published spots (has full info): give specific, helpful details (what to order, vibe, subway stop)
- For "coming soon" spots: mention them briefly as "📍 [Name] — on Bapmap soon" without details
- Be friendly, direct, and specific. No fluff.
- If nothing matches well, say so honestly and suggest browsing /spots
- Links: for published spots, format as /spots/[slug] (lowercase, hyphenated)
- Keep it to 150-250 words"""


def search(query: str, stream: bool = False):
    print(f"\n🔍 검색: {query}\n")

    # 1. 쿼리 임베딩
    q_embedding = embed_query(query)

    # 2. 유사도 검색
    results = similarity_search(q_embedding)
    print(f"검색 결과: {len(results)}개\n")

    if not results:
        return "No matching spots found. Try browsing all spots at /spots"

    # 3. 컨텍스트 빌드
    context = build_context(results)

    # 4. Claude 답변
    user_msg = f"User query: {query}\n\nRetrieved spots:\n{context}"

    if stream:
        with anthropic_client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        ) as s:
            full = ""
            for text in s.text_stream:
                print(text, end="", flush=True)
                full += text
            print()
            return full
    else:
        res = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return res.content[0].text


if __name__ == "__main__":
    import sys
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "I want korean bbq near hongdae"
    result = search(query, stream=True)
