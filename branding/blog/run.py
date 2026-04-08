import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
load_dotenv(Path(__file__).parent.parent.parent / ".env")

from branding.blog.graph import build_graph


def main():
    parser = argparse.ArgumentParser(description="Bapmap Blog Agent")
    parser.add_argument("--type", choices=["spot", "list", "guide"], default="spot")
    parser.add_argument("--topic", type=str, default="")
    parser.add_argument("--spot-ids", nargs="*", default=[])
    args = parser.parse_args()

    initial_state = {
        "post_type": args.type,
        "topic": args.topic,
        "spot_ids": args.spot_ids,
        "spots_data": [],
        "draft": "",
        "title": "",
        "meta_description": "",
        "slug": "",
        "keywords": [],
        "eval_score": 0.0,
        "eval_feedback": "",
        "approved": False,
        "revision_count": 0,
        "published_url": None,
    }

    print(f"\n🍖 Bapmap Blog Agent 시작")
    print(f"   type: {args.type} | topic: {args.topic or '(스팟 기반)'}\n")

    graph = build_graph()
    result = graph.invoke(initial_state)

    print(f"\n✅ 완료!")
    print(f"   제목: {result.get('title')}")
    print(f"   점수: {result.get('eval_score')}/50")
    print(f"   저장: {result.get('published_url')}")


if __name__ == "__main__":
    main()
