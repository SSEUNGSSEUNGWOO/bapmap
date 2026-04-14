"""
RAG v2 평가
실행: python3 -m pipeline.rag.eval_run_v2
"""
import json
import time
from pathlib import Path
from pipeline.rag.search_v2 import search_top5

EVAL_FILE = Path(__file__).parent / "eval_set.json"


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

        hit = 1 if any(r in relevant for r in results) else 0
        hits.append(hit)

        found = sum(1 for e in expected if e in results)
        recall = found / len(expected) if expected else 0
        recalls.append(recall)

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
