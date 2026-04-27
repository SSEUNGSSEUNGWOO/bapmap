"""
가이드 임베딩 (OpenAI text-embedding-3-small, 1536d)
title + subtitle + intro + body 합쳐서 임베딩 → guides.embedding 저장.

실행:
  .venv/bin/python -m pipeline.rag.embed_guides              # 누락분만 (default)
  .venv/bin/python -m pipeline.rag.embed_guides --slugs slug1,slug2
  .venv/bin/python -m pipeline.rag.embed_guides --rebuild-all  # 모든 가이드 재임베딩
"""
import os
import time
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

EMBED_MODEL = "text-embedding-3-small"
MAX_CHARS = 8000  # text-embedding-3-small 입력 한도 충분 여유


def _build_embed_text(guide: dict) -> str:
    parts = []
    if guide.get("title"):
        parts.append(f"Title: {guide['title']}")
    if guide.get("subtitle"):
        parts.append(f"Subtitle: {guide['subtitle']}")
    if guide.get("category_tag"):
        parts.append(f"Tags: {guide['category_tag']}")
    if guide.get("intro"):
        parts.append(f"Intro: {guide['intro']}")
    if guide.get("body"):
        parts.append(f"Body: {guide['body']}")
    text = "\n\n".join(parts).replace("\n", " ").strip()
    return text[:MAX_CHARS]


def embed_guide(guide: dict) -> bool:
    text = _build_embed_text(guide)
    if not text:
        print(f"  skip: {guide.get('slug')} (본문 비어있음)")
        return False

    res = openai_client.embeddings.create(input=[text], model=EMBED_MODEL)
    embedding = res.data[0].embedding

    sb.table("guides").update({"embedding": embedding}).eq("id", guide["id"]).execute()
    print(f"  ✓ {guide['slug']} — {len(text)}자 임베딩 저장")
    return True


def _load_targets(mode: str, slugs: list[str] | None) -> list[dict]:
    if slugs:
        return sb.table("guides").select("*").in_("slug", slugs).execute().data
    if mode == "all":
        return sb.table("guides").select("*").execute().data
    # default: missing
    return sb.table("guides").select("*").is_("embedding", "null").execute().data


def run(mode: str = "missing", slugs: list[str] | None = None):
    guides = _load_targets(mode, slugs)
    print(f"\n모드: {mode if not slugs else 'slugs'} | 대상 가이드: {len(guides)}개\n")

    if not guides:
        print("처리할 가이드 없음. 종료.")
        return

    success = 0
    for i, guide in enumerate(guides):
        print(f"[{i+1}/{len(guides)}] {guide.get('slug', '(no slug)')}")
        try:
            if embed_guide(guide):
                success += 1
        except Exception as e:
            print(f"  ❌ 오류: {e}")
        if i > 0 and i % 20 == 0:
            time.sleep(1)

    print(f"\n완료: {success}/{len(guides)}개 임베딩 저장")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="가이드 임베딩 (OpenAI 1536d). 기본은 incremental(누락분만)."
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=None,
        help="콤마로 구분된 slug들만 재임베딩",
    )
    parser.add_argument(
        "--rebuild-all",
        action="store_true",
        help="모든 가이드를 재임베딩 (덮어쓰기)",
    )
    args = parser.parse_args()

    if args.slugs:
        slug_list = [s.strip() for s in args.slugs.split(",") if s.strip()]
        run(slugs=slug_list)
    elif args.rebuild_all:
        run(mode="all")
    else:
        run(mode="missing")
