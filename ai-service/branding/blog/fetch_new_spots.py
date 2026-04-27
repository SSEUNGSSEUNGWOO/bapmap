"""
discover + ingest만 실행 (LLM 호출 없음)
실행: python -m branding.blog.fetch_new_spots --max-spots 5
"""
import sys
import json
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-spots", type=int, default=5)
    args = parser.parse_args()

    from branding.blog.agents.discover import discover
    from branding.blog.agents.ingest import ingest
    from supabase import create_client

    discovered = discover(max_spots=args.max_spots)
    if not discovered:
        print(json.dumps({"new_spot_ids": [], "spots": []}, ensure_ascii=False))
        return

    new_ids = ingest(discovered)
    if not new_ids:
        print(json.dumps({"new_spot_ids": [], "spots": []}, ensure_ascii=False))
        return

    sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    spots = sb.table("spots").select("*").in_("id", new_ids).execute().data
    print(json.dumps({"new_spot_ids": new_ids, "spots": spots}, ensure_ascii=False))


if __name__ == "__main__":
    main()
