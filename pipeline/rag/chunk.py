"""
Stage 2: Chunking
파싱된 텍스트 → 임베딩할 청크 리스트

전략:
- 업로드완료 스팟: metadata + content 합쳐서 1개 청크 (정보 풍부)
- 미완성 스팟: metadata만 1개 청크 (이름/위치/카테고리 정도)
"""
from pipeline.rag.parse import parse_spot


def chunk_spot(spot: dict) -> dict | None:
    """
    spot 1개 → chunk 1개 반환
    embedding이 None이어야 하는 경우(lat/lng 없는 등) → None 반환
    """
    parsed = parse_spot(spot)

    if not parsed["metadata_text"]:
        return None

    # 최종 임베딩 텍스트 조합
    if parsed["content_text"]:
        # 본문 있으면 metadata + content 합치기
        embed_text = parsed["metadata_text"] + "\n\n" + parsed["content_text"]
    else:
        embed_text = parsed["metadata_text"]

    # voyage-3 최대 16K 토큰, 대략 12000자 안전선
    embed_text = embed_text[:12000]

    return {
        "id": parsed["id"],
        "name": parsed["name"],
        "status": parsed["status"],
        "embed_text": embed_text,
        "has_content": bool(parsed["content_text"]),
    }


def chunk_all(spots: list[dict]) -> list[dict]:
    chunks = []
    for spot in spots:
        chunk = chunk_spot(spot)
        if chunk:
            chunks.append(chunk)
    print(f"청킹 완료: {len(chunks)}개 (전체 {len(spots)}개 중)")
    return chunks


# ── v2: parent-child chunking ──

MAX_TOKENS = 512
OVERLAP_TOKENS = 128


def _approx_tokens(text: str) -> int:
    return len(text.split())


def _truncate(text: str, max_tokens: int = MAX_TOKENS) -> str:
    words = text.split()
    if len(words) <= max_tokens:
        return text
    return " ".join(words[:max_tokens])


def _split_content(text: str, max_tokens: int = MAX_TOKENS, overlap: int = OVERLAP_TOKENS) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    segments = []
    current = []
    current_len = 0

    for para in paragraphs:
        para_len = _approx_tokens(para)
        if current_len + para_len > max_tokens and current:
            segments.append("\n\n".join(current))
            # overlap: keep last paragraph(s) up to overlap tokens
            overlap_parts = []
            overlap_len = 0
            for p in reversed(current):
                plen = _approx_tokens(p)
                if overlap_len + plen > overlap:
                    break
                overlap_parts.insert(0, p)
                overlap_len += plen
            current = overlap_parts
            current_len = overlap_len
        current.append(para)
        current_len += para_len

    if current:
        segments.append("\n\n".join(current))

    return segments


def chunk_spot_v2(spot: dict) -> list[dict]:
    from pipeline.rag.parse import parse_spot_v2
    parsed = parse_spot_v2(spot)
    if not parsed["chunks"]:
        return []

    chunks = []
    spot_id = parsed["id"]

    for ctype in ["profile", "location", "memo", "menu", "reviews"]:
        text = parsed["chunks"].get(ctype)
        if text:
            chunks.append({
                "spot_id": spot_id,
                "chunk_type": ctype,
                "content": _truncate(text),
            })

    content = parsed["chunks"].get("content")
    if content:
        segments = _split_content(content)
        for i, seg in enumerate(segments):
            chunks.append({
                "spot_id": spot_id,
                "chunk_type": f"content_{i}",
                "content": seg,
            })

    return chunks


def chunk_all_v2(spots: list[dict]) -> list[dict]:
    all_chunks = []
    for spot in spots:
        all_chunks.extend(chunk_spot_v2(spot))
    print(f"v2 청킹 완료: {len(all_chunks)}개 청크 (스팟 {len(spots)}개)")
    return all_chunks
