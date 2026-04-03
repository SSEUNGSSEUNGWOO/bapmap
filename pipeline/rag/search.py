"""
RAG Search Pipeline
1. Query Rewriting  — Claude가 쿼리 정제 + 필터 추출
2. Hybrid Search    — pgvector(voyage-3) + Supabase 풀텍스트 (RRF 결합)
3. Reranking        — voyage-3 reranker로 최종 순위 조정
4. Answer           — Claude Haiku가 자연어 답변 생성
"""
import os
import json
from openai import OpenAI
from anthropic import Anthropic
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

EMBED_MODEL = "text-embedding-3-small"


# ── 1. Query Rewriting ──────────────────────────────────────────────────────

REWRITE_PROMPT = """You are a search query optimizer for Bapmap, a Korean restaurant guide.

Given a user's casual query, extract:
1. "query": clean, specific search query (English, max 20 words)
2. "region": specific area in Korea if mentioned (e.g. "Gangnam", "Hongdae", "Itaewon", "Seongsu") — null if not mentioned
3. "category": food type if clearly mentioned (e.g. "Ramen", "Korean BBQ", "Cafe") — null if not mentioned

Return JSON only. No explanation.

Examples:
User: "i go gangnam i want korean food"
{"query": "Korean restaurant in Gangnam Seoul", "region": "Gangnam", "category": null}

User: "spicy ramen near hongdae"
{"query": "spicy ramen Hongdae Seoul", "region": "Hongdae", "category": "Ramen"}

User: "좋은 카페 추천해줘 성수동"
{"query": "cafe in Seongsu Seoul", "region": "Seongsu", "category": "Cafe"}

User: "where should i eat"
{"query": "best Korean restaurant Seoul local pick", "region": null, "category": null}"""


def rewrite_query(raw_query: str) -> dict:
    res = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=REWRITE_PROMPT,
        messages=[{"role": "user", "content": raw_query}],
    )
    try:
        return json.loads(res.content[0].text)
    except Exception:
        return {"query": raw_query, "region": None, "category": None}


# ── 2. Hybrid Search ────────────────────────────────────────────────────────

def embed_query(text: str) -> list[float]:
    res = openai_client.embeddings.create(input=[text.replace("\n", " ")], model=EMBED_MODEL)
    return res.data[0].embedding


def hybrid_search(query: str, region: str | None, category: str | None, count: int = 10) -> list[dict]:
    embedding = embed_query(query)
    res = sb.rpc("hybrid_search_spots", {
        "query_text": query,
        "query_embedding": embedding,
        "match_count": count,
        "filter_region": region,
        "filter_category": category,
    }).execute()
    return res.data or []


# ── 3. Reranking ────────────────────────────────────────────────────────────

def rerank(query: str, spots: list[dict], top_k: int = 5) -> list[dict]:
    if not spots:
        return []
    if len(spots) <= top_k:
        return spots

    docs = []
    for s in spots:
        name = s.get("english_name") or s.get("name", "")
        doc = f"{name} | {s.get('category', '')} | {s.get('region') or s.get('city', '')} | ★{s.get('rating', '')}"
        if s.get("content"):
            doc += " | " + s["content"][:200]
        docs.append(doc)

    numbered = "\n".join(f"{i}: {d}" for i, d in enumerate(docs))
    res = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=60,
        messages=[{"role": "user", "content":
            f"Query: {query}\n\nSpots:\n{numbered}\n\n"
            f"Return the {top_k} most relevant spot indices as JSON array only. Example: [2,0,4,1,3]"
        }],
    )
    try:
        import json as _json
        indices = _json.loads(res.content[0].text.strip())
        return [spots[i] for i in indices if i < len(spots)]
    except Exception:
        return spots[:top_k]


# ── 4. Answer Generation ────────────────────────────────────────────────────

ANSWER_PROMPT = """You are Bapmap's food concierge — helping English-speaking tourists find the best places to eat in Korea.

Rules:
- Recommend only from the retrieved spots below. Never make up places.
- Published spots (status=업로드완료): give specific details — what to order, vibe, subway stop, price
- Unpublished spots (other status): mention briefly as "📍 [Name] — coming soon on Bapmap"
- Be direct and friendly. No fluff. Like a tip from a Korean friend.
- For published spots include a link: /spots/[slug]
- If nothing matches, say so honestly and suggest browsing /spots
- 150-250 words max"""


def build_context(spots: list[dict]) -> str:
    parts = []
    for s in spots:
        name = s.get("english_name") or s.get("name", "")
        slug = name.lower().replace(" ", "-")
        status = s.get("status", "")

        if status == "업로드완료":
            parts.append(
                f"[PUBLISHED] {name}\n"
                f"  Category: {s.get('category', '')} | Location: {s.get('region') or s.get('city')} | "
                f"★{s.get('rating', '')} | {s.get('price_level', '')} | 🚇{s.get('subway', '')}\n"
                f"  Link: /spots/{slug}\n"
                f"  Preview: {(s.get('content') or '')[:200]}"
            )
        else:
            parts.append(
                f"[COMING SOON] {name}\n"
                f"  Category: {s.get('category', '')} | Location: {s.get('region') or s.get('city')}"
            )
    return "\n\n".join(parts)


def answer(query: str, spots: list[dict], stream: bool = False) -> str:
    context = build_context(spots)
    user_msg = f"User query: {query}\n\nSpots:\n{context}"

    if stream:
        with anthropic_client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=ANSWER_PROMPT,
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
            system=ANSWER_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        return res.content[0].text


# ── 메인 파이프라인 ──────────────────────────────────────────────────────────

def search(raw_query: str, stream: bool = False) -> str:
    print(f"\n🔍 원본 쿼리: {raw_query}")

    # 1. Query Rewriting
    rewritten = rewrite_query(raw_query)
    print(f"✏️  정제된 쿼리: {rewritten['query']}")
    print(f"📍 지역 필터: {rewritten['region']} | 카테고리 필터: {rewritten['category']}\n")

    # 2. Hybrid Search
    results = hybrid_search(
        query=rewritten["query"],
        region=rewritten["region"],
        category=rewritten["category"],
        count=10,
    )
    print(f"🔎 하이브리드 검색 결과: {len(results)}개")

    if not results:
        return "No matching spots found. Try browsing all spots at /spots"

    # 3. Reranking
    reranked = rerank(rewritten["query"], results, top_k=5)
    print(f"🏆 리랭킹 후: {len(reranked)}개\n")
    for r in reranked:
        print(f"  - {r.get('english_name') or r.get('name')} ({r.get('status')})")
    print()

    # 4. Answer
    return answer(raw_query, reranked, stream=stream)


if __name__ == "__main__":
    import sys
    raw = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "i want ramen near hongdae"
    search(raw, stream=True)
