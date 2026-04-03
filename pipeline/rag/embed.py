"""
Stage 3: Embedding (voyage-3)
청크 텍스트 → Voyage AI 벡터 생성 → Supabase 저장

실행: python -m pipeline.rag.embed
옵션:
  --all     : 전체 스팟 재임베딩
  --missing : embedding이 없는 스팟만 (기본값)
  --id <uuid>
"""
import os
import sys
import time
import argparse
import voyageai
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

voyage_client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

EMBED_MODEL = "voyage-3"


def get_embedding(text: str) -> list[float]:
    result = voyage_client.embed([text], model=EMBED_MODEL, input_type="document")
    return result.embeddings[0]


def embed_spot(spot: dict) -> bool:
    from pipeline.rag.chunk import chunk_spot

    chunk = chunk_spot(spot)
    if not chunk:
        print(f"  skip: {spot.get('english_name') or spot.get('name')} (청크 없음)")
        return False

    embedding = get_embedding(chunk["embed_text"])
    sb.table("spots").update({"embedding": embedding}).eq("id", spot["id"]).execute()
    status_label = "✅" if chunk["has_content"] else "📋"
    print(f"  {status_label} {chunk['name']} — 임베딩 저장 ({len(chunk['embed_text'])}자)")
    return True


def run(mode: str = "missing", spot_id: str | None = None):
    if spot_id:
        spots = sb.table("spots").select("*").eq("id", spot_id).execute().data
    elif mode == "all":
        spots = sb.table("spots").select("*").execute().data
    else:
        spots = sb.table("spots").select("*").is_("embedding", "null").execute().data

    print(f"\n임베딩 대상: {len(spots)}개\n")
    success = 0
    for i, spot in enumerate(spots):
        name = spot.get("english_name") or spot.get("name")
        print(f"[{i+1}/{len(spots)}] {name}")
        try:
            if embed_spot(spot):
                success += 1
        except Exception as e:
            print(f"  ❌ 오류: {e}")
        if i > 0 and i % 20 == 0:
            time.sleep(0.5)

    print(f"\n완료: {success}/{len(spots)}개 임베딩 저장")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--missing", action="store_true")
    parser.add_argument("--id", type=str)
    args = parser.parse_args()

    if args.id:
        run(spot_id=args.id)
    elif args.all:
        run(mode="all")
    else:
        run(mode="missing")
