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

    # 너무 길면 자르기 (OpenAI 8191 토큰 제한, 대략 6000자 안전선)
    embed_text = embed_text[:6000]

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
