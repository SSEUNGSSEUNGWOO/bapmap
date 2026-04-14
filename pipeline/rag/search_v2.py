"""
RAG v2 Search Pipeline
- BGE-M3 dense embedding + fulltext (RRF)
- 단일 청크 (512 token cap)
- Query rewriting (Claude Haiku)
"""
import os
import json
from anthropic import Anthropic
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

_embed_model = None


def _get_embed_model():
    global _embed_model
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer
        _embed_model = SentenceTransformer("BAAI/bge-m3")
    return _embed_model


# ── 1. Query Rewriting ──

REWRITE_PROMPT = """You are a search query optimizer for Bapmap, a Korean restaurant guide.

Given a user's casual query, extract:
1. "query": clean, specific search query (English, max 20 words)
2. "region": specific area if mentioned (e.g. "Gangnam", "Hongdae", "Itaewon", "Seongsu") — null if not
3. "category": food type if clearly mentioned — null if not

Return JSON only.

User: "i go gangnam i want korean food"
{"query": "Korean restaurant in Gangnam Seoul", "region": "Gangnam", "category": null}

User: "좋은 카페 추천해줘 성수동"
{"query": "cafe in Seongsu Seoul", "region": "Seongsu", "category": "Cafe"}"""


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


# ── 2. Embedding ──

def embed_query(text: str) -> list[float]:
    model = _get_embed_model()
    vec = model.encode([text], normalize_embeddings=True)
    return vec[0].tolist()


# ── 3. Hybrid Search (dense + fulltext RRF) ──

def search_chunks(query_text: str, query_embedding: list[float], count: int = 20) -> list[dict]:
    res = sb.rpc("hybrid_search_chunks_v2", {
        "query_text": query_text,
        "query_embedding": query_embedding,
        "match_count": count,
    }).execute()
    return res.data or []


def dedupe_by_spot(chunks: list[dict], top_k: int = 5) -> list[str]:
    seen = set()
    spot_ids = []
    for c in chunks:
        sid = c["spot_id"]
        if sid not in seen:
            seen.add(sid)
            spot_ids.append(sid)
        if len(spot_ids) >= top_k:
            break
    return spot_ids


def get_parent_spots(spot_ids: list[str]) -> list[dict]:
    if not spot_ids:
        return []
    res = sb.table("spots").select("*").in_("id", spot_ids).execute()
    order = {sid: i for i, sid in enumerate(spot_ids)}
    return sorted(res.data, key=lambda s: order.get(s["id"], 99))


# ── 4. Answer ──

ANSWER_PROMPT = """You are Bapmap's food concierge — helping English-speaking tourists find the best places to eat in Korea.

Rules:
- Recommend only from the retrieved spots below. Never make up places.
- Be direct and friendly. No fluff. Like a tip from a Korean friend.
- For published spots include a link: /spots/[slug]
- If nothing matches, say so honestly and suggest browsing /spots
- 150-250 words max"""


def build_context(spots: list[dict]) -> str:
    parts = []
    for s in spots:
        name = s.get("english_name") or s.get("name", "")
        slug = name.lower().replace(" ", "-").replace("/", "-")
        wto = s.get("what_to_order") or []
        wto_str = ", ".join(str(w)[:80] for w in wto[:3])
        parts.append(
            f"{name}\n"
            f"  Category: {s.get('category', '')} | Location: {s.get('region', '')} | "
            f"★{s.get('rating', '')} | {s.get('price_level', '')} | 🚇{s.get('subway', '')}\n"
            f"  What to order: {wto_str}\n"
            f"  Curator: {(s.get('memo') or '')[:300]}\n"
            f"  Link: /spots/{slug}"
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


# ── Pipeline ──

def search(raw_query: str, stream: bool = False) -> str:
    print(f"\n🔍 원본 쿼리: {raw_query}")

    rewritten = rewrite_query(raw_query)
    query_text = rewritten["query"]
    print(f"✏️  정제된 쿼리: {query_text}")

    query_emb = embed_query(query_text)

    chunks = search_chunks(query_text, query_emb, count=20)
    print(f"🔎 검색 결과: {len(chunks)}개")

    spot_ids = dedupe_by_spot(chunks, top_k=5)
    spots = get_parent_spots(spot_ids)
    print(f"📦 최종 스팟: {len(spots)}개\n")
    for s in spots:
        print(f"  - {s.get('english_name') or s.get('name')}")
    print()

    return answer(raw_query, spots, stream=stream)


def search_top5(raw_query: str) -> list[str]:
    rewritten = rewrite_query(raw_query)
    query_text = rewritten["query"]
    query_emb = embed_query(query_text)
    chunks = search_chunks(query_text, query_emb, count=20)
    spot_ids = dedupe_by_spot(chunks, top_k=5)
    spots = get_parent_spots(spot_ids)
    return [s.get("english_name") or s.get("name", "") for s in spots]


if __name__ == "__main__":
    import sys
    raw = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "i want ramen near hongdae"
    search(raw, stream=True)
