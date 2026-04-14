"""
RAG 검색 품질 평가
실행: python -m pipeline.rag.eval_run
"""
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from anthropic import Anthropic

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

EMBED_MODEL = "text-embedding-3-small"
EVAL_FILE = Path(__file__).parent / "eval_set.json"


def embed_query(text: str) -> list[float]:
    res = openai_client.embeddings.create(input=[text.replace("\n", " ")], model=EMBED_MODEL)
    return res.data[0].embedding


def rewrite_query(raw_query: str) -> dict:
    res = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        messages=[{"role": "user", "content": f"""Extract search info from this query. Return JSON only:
{{"query": "clean English search query", "region": "area or null", "category": "food type or null"}}

Query: {raw_query}"""}],
    )
    try:
        return json.loads(res.content[0].text)
    except Exception:
        return {"query": raw_query, "region": None, "category": None}


def search_top5(raw_query: str) -> list[str]:
    rw = rewrite_query(raw_query)
    embedding = embed_query(rw["query"])
    res = sb.rpc("hybrid_search_spots", {
        "query_text": rw["query"],
        "query_embedding": embedding,
        "match_count": 5,
        "filter_region": rw.get("region"),
        "filter_category": rw.get("category"),
    }).execute()
    return [s.get("english_name") or s.get("name", "") for s in (res.data or [])]


def evaluate():
    cases = json.loads(EVAL_FILE.read_text())
    hits, recalls, mrrs = [], [], []

    for c in cases:
        query = c["query"]
        expected = set(c["expected"])
        acceptable = set(c.get("acceptable", []))
        relevant = expected | acceptable

        results = search_top5(query)
        time.sleep(0.3)

        # Hit@5
        hit = 1 if any(r in relevant for r in results) else 0
        hits.append(hit)

        # Recall@5
        found = sum(1 for e in expected if e in results)
        recall = found / len(expected) if expected else 0
        recalls.append(recall)

        # MRR@5
        mrr = 0.0
        for i, r in enumerate(results):
            if r in relevant:
                mrr = 1.0 / (i + 1)
                break
        mrrs.append(mrr)

        status = "✅" if hit else "❌"
        print(f"{status} [{c['type']}] \"{query}\"")
        print(f"   expected: {c['expected']}")
        print(f"   got:      {results}")
        if not hit:
            print(f"   ⚠️  MISS")
        print()

    n = len(cases)
    print("=" * 60)
    print(f"Hit@5:    {sum(hits)}/{n} = {sum(hits)/n:.1%}")
    print(f"Recall@5: {sum(recalls)/n:.1%}")
    print(f"MRR@5:    {sum(mrrs)/n:.3f}")


if __name__ == "__main__":
    evaluate()
