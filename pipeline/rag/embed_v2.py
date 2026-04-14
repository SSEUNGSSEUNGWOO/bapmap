"""
BGE-M3 임베딩 + spot_chunks 테이블 저장 (단일 청크)
실행: python3 -m pipeline.rag.embed_v2 --cap 512
"""
import os
import argparse
from dotenv import load_dotenv
from supabase import create_client
from sentence_transformers import SentenceTransformer
from pipeline.rag.parse import parse_spot

load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

print("BGE-M3 모델 로딩...")
model = SentenceTransformer("BAAI/bge-m3")

BATCH_SIZE = 8


def _approx_tokens(text: str) -> int:
    return len(text.split())


def _truncate(text: str, max_tokens: int) -> str:
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens])


def make_single_chunk(spot: dict, cap: int) -> dict | None:
    parsed = parse_spot(spot)
    if not parsed["metadata_text"]:
        return None

    if parsed["content_text"]:
        text = parsed["metadata_text"] + "\n\n" + parsed["content_text"]
    else:
        text = parsed["metadata_text"]

    text = _truncate(text, cap)

    return {
        "spot_id": parsed["id"],
        "chunk_type": "single",
        "content": text,
    }


def embed_batch(texts: list[str]) -> list[list[float]]:
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vecs.tolist()


def run(cap: int):
    spots = sb.table("spots").select("*").execute().data
    print(f"스팟 {len(spots)}개 로드, 토큰 cap: {cap}")

    chunks = []
    for spot in spots:
        c = make_single_chunk(spot, cap)
        if c:
            chunks.append(c)
    print(f"청크 {len(chunks)}개 생성")

    if not chunks:
        return

    print("기존 spot_chunks 삭제...")
    sb.table("spot_chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings = embed_batch(texts)

        rows = []
        for c, emb in zip(batch, embeddings):
            rows.append({
                "spot_id": c["spot_id"],
                "chunk_type": c["chunk_type"],
                "content": c["content"],
                "embedding": emb,
            })

        sb.table("spot_chunks").insert(rows).execute()
        print(f"  [{i + len(batch)}/{total}]")

    print(f"\n완료: {total}개 청크 (cap={cap})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cap", type=int, default=512)
    args = parser.parse_args()
    run(args.cap)
