"""
BGE-M3 임베딩 + spot_chunks 테이블 저장 (단일 청크)
실행: python3 -m pipeline.rag.embed_v2 --cap 512
"""
import os
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

BATCH_SIZE = 8
DEFAULT_CAP = 512
HF_MODEL = "BAAI/bge-m3"
HF_API_URL = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{HF_MODEL}"

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(HF_MODEL)
    return _model


def _truncate(text: str, max_tokens: int) -> str:
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens])


def _parse_spot(spot: dict) -> dict:
    parts = []
    name = spot.get("english_name") or spot.get("name") or ""
    if name:
        parts.append(f"Name: {name}")
    if spot.get("category"):
        parts.append(f"Category: {spot['category']}")
    if spot.get("city"):
        parts.append(f"City: {spot['city']}")
    if spot.get("region"):
        parts.append(f"Region: {spot['region']}")
    if spot.get("subway"):
        parts.append(f"Subway: {spot['subway']}")
    if spot.get("rating"):
        parts.append(f"Rating: {spot['rating']}")
    if spot.get("tagline"):
        parts.append(f"Tagline: {spot['tagline']}")
    if spot.get("what_to_order"):
        wto = spot["what_to_order"]
        if isinstance(wto, list):
            parts.append("Menu: " + ", ".join(wto))
    if spot.get("good_for"):
        gf = spot["good_for"]
        if isinstance(gf, list):
            parts.append("Good for: " + ", ".join(gf))
    if spot.get("google_reviews"):
        reviews = spot["google_reviews"]
        if isinstance(reviews, list):
            parts.append("Reviews: " + " | ".join(reviews[:2]))

    return {
        "id": spot.get("id"),
        "metadata_text": "\n".join(parts),
        "content_text": spot.get("content") or "",
    }


def make_single_chunk(spot: dict, cap: int = DEFAULT_CAP) -> dict | None:
    parsed = _parse_spot(spot)
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
    model = _get_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vecs.tolist()


def embed_api(text: str) -> list[float]:
    hf_token = os.getenv("HF_API_TOKEN")
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    res = requests.post(HF_API_URL, headers=headers, json={"inputs": text})
    res.raise_for_status()
    return res.json()


def embed_spot(spot: dict, cap: int = DEFAULT_CAP) -> bool:
    chunk = make_single_chunk(spot, cap)
    if not chunk:
        return False

    emb = embed_batch([chunk["content"]])[0]
    spot_id = chunk["spot_id"]

    sb.table("spot_chunks").delete().eq("spot_id", spot_id).execute()
    sb.table("spot_chunks").insert({
        "spot_id": spot_id,
        "chunk_type": "single",
        "content": chunk["content"],
        "embedding": emb,
    }).execute()
    return True


def _load_target_spots(mode: str, spot_ids: list[str] | None) -> list[dict]:
    """모드별로 대상 spots 로드.
    - mode="missing": spot_chunks에 아직 없는 spots만
    - mode="ids": 주어진 spot_ids 만
    - mode="all": 전체 spots
    """
    if mode == "ids":
        if not spot_ids:
            return []
        return sb.table("spots").select("*").in_("id", spot_ids).execute().data

    all_spots = sb.table("spots").select("*").execute().data

    if mode == "all":
        return all_spots

    # mode == "missing"
    existing = sb.table("spot_chunks").select("spot_id").execute().data
    embedded_ids = {row["spot_id"] for row in existing}
    return [s for s in all_spots if s["id"] not in embedded_ids]


def _embed_and_upsert(chunks: list[dict]) -> None:
    """청크들을 배치로 임베딩하고, spot_id별 delete-then-insert로 안전하게 저장."""
    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        texts = [c["content"] for c in batch]
        embeddings = embed_batch(texts)

        for c, emb in zip(batch, embeddings):
            sb.table("spot_chunks").delete().eq("spot_id", c["spot_id"]).execute()
            sb.table("spot_chunks").insert({
                "spot_id": c["spot_id"],
                "chunk_type": c["chunk_type"],
                "content": c["content"],
                "embedding": emb,
            }).execute()

        print(f"  [{i + len(batch)}/{total}]")


def run(cap: int, mode: str = "missing", spot_ids: list[str] | None = None):
    spots = _load_target_spots(mode, spot_ids)
    print(f"모드: {mode} | 대상 스팟 {len(spots)}개 | 토큰 cap: {cap}")

    chunks = []
    for spot in spots:
        c = make_single_chunk(spot, cap)
        if c:
            chunks.append(c)
    print(f"청크 {len(chunks)}개 생성")

    if not chunks:
        print("처리할 청크 없음. 종료.")
        return

    if mode == "all":
        # 전체 재구축: 명시적 confirm 후 전체 삭제 → 전체 재임베딩
        print("⚠️  --rebuild-all: 기존 spot_chunks 전체 삭제 → 전체 재임베딩")
        sb.table("spot_chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    _embed_and_upsert(chunks)
    print(f"\n완료: {len(chunks)}개 청크 (cap={cap}, mode={mode})")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="BGE-M3 임베딩. 기본은 incremental(누락분만). 안전을 위해 전체 재구축은 명시 플래그 필요."
    )
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP)
    parser.add_argument(
        "--spot-ids",
        type=str,
        default=None,
        help="콤마로 구분된 spot_id 들만 재임베딩 (delete-then-insert per id)",
    )
    parser.add_argument(
        "--rebuild-all",
        action="store_true",
        help="⚠️  전체 spot_chunks 삭제 후 전체 재임베딩. 사용 전 데이터 백업 권장.",
    )
    args = parser.parse_args()

    if args.spot_ids:
        ids = [s.strip() for s in args.spot_ids.split(",") if s.strip()]
        run(args.cap, mode="ids", spot_ids=ids)
    elif args.rebuild_all:
        run(args.cap, mode="all")
    else:
        run(args.cap, mode="missing")
