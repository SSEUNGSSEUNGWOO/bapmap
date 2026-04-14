"""
Stage 1: Parsing
spot dict → 임베딩용 깨끗한 텍스트로 변환
"""
import re


def strip_markdown(text: str) -> str:
    """마크다운 문법 제거, 순수 텍스트만 남김"""
    # 헤더
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # 링크
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # 굵기/이탤릭
    text = re.sub(r"\*{1,3}([^*]+)\*{1,3}", r"\1", text)
    # 테이블 구분선
    text = re.sub(r"^\|[-:| ]+\|$", "", text, flags=re.MULTILINE)
    # 테이블 셀 (| 제거)
    text = re.sub(r"\|", " ", text)
    # 코드블록
    text = re.sub(r"```[\s\S]*?```", "", text)
    # 인라인 코드
    text = re.sub(r"`[^`]+`", "", text)
    # 수평선
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # 연속 공백/줄바꿈 정리
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_spot(spot: dict) -> dict:
    """
    spot dict를 두 개의 텍스트 덩어리로 파싱:
    - metadata_text: 구조화된 핵심 정보 (항상 존재)
    - content_text: 블로그 본문 (있을 때만)
    """
    name = spot.get("english_name") or spot.get("name", "")
    category = spot.get("category", "")
    region = spot.get("region") or spot.get("city", "")
    city = spot.get("city", "")
    subway = spot.get("subway", "")
    price = spot.get("price_level", "")
    rating = spot.get("rating", "")
    hours = spot.get("hours", "")
    memo = spot.get("memo", "")
    reviews = spot.get("google_reviews") or []
    address = spot.get("english_address") or spot.get("address", "")

    attrs = []
    if spot.get("vegetarian"):
        attrs.append("vegetarian-friendly")
    if spot.get("reservable"):
        attrs.append("reservations available")
    if spot.get("good_for_groups"):
        attrs.append("good for groups")

    # --- metadata chunk ---
    meta_parts = [
        f"Restaurant: {name}",
        f"Type: {category}",
        f"Location: {region}, {city}, South Korea",
        f"Nearest subway: {subway}" if subway else "",
        f"Price range: {price}" if price else "",
        f"Rating: {rating} stars" if rating else "",
        f"Address: {address}" if address else "",
        f"Features: {', '.join(attrs)}" if attrs else "",
        f"Hours: {hours}" if hours else "",
        f"Curator note: {memo}" if memo else "",
    ]
    if reviews:
        meta_parts.append("Guest reviews: " + " | ".join(str(r) for r in reviews[:2]))

    metadata_text = "\n".join(p for p in meta_parts if p).strip()

    # --- content chunk ---
    content_text = ""
    raw_content = spot.get("content", "")
    if raw_content:
        content_text = strip_markdown(raw_content)[:2000]

    return {
        "id": spot.get("id"),
        "name": name,
        "status": spot.get("status", ""),
        "metadata_text": metadata_text,
        "content_text": content_text,
    }


def parse_spot_v2(spot: dict) -> dict:
    name = spot.get("english_name") or spot.get("name", "")
    korean_name = spot.get("name", "")
    category = spot.get("category", "")
    region = spot.get("region") or spot.get("city", "")
    city = spot.get("city", "")
    subway = spot.get("subway", "")
    price = spot.get("price_level", "")
    rating = spot.get("rating", "")
    hours = spot.get("hours", "")
    memo = spot.get("memo", "")
    reviews = spot.get("google_reviews") or []
    address = spot.get("english_address") or spot.get("address", "")
    tagline = spot.get("tagline", "")
    wto = spot.get("what_to_order") or []

    attrs = []
    if spot.get("vegetarian"):
        attrs.append("vegetarian-friendly")
    if spot.get("reservable"):
        attrs.append("reservations available")
    if spot.get("good_for_groups"):
        attrs.append("good for groups")

    profile = "\n".join(filter(None, [
        f"Restaurant: {name} ({korean_name})" if korean_name != name else f"Restaurant: {name}",
        f"Type: {category}",
        f"Location: {region}, {city}",
        f"Price: {price}" if price else None,
        f"Rating: {rating} stars" if rating else None,
        f"Features: {', '.join(attrs)}" if attrs else None,
        f"Tagline: {tagline}" if tagline else None,
    ]))

    location = "\n".join(filter(None, [
        f"Address: {address}" if address else None,
        f"Nearest subway: {subway}" if subway else None,
        f"Hours: {hours}" if hours else None,
    ]))

    menu = "\n".join(f"- {item}" for item in wto) if wto else None
    if menu:
        menu = f"What to order at {name}:\n{menu}"

    review_text = None
    if reviews:
        review_text = f"Google reviews for {name}:\n" + "\n---\n".join(str(r) for r in reviews[:3])

    memo_text = None
    if memo:
        memo_text = f"Curator note for {name}: {memo.strip()}"

    content_raw = spot.get("content", "")
    content_text = strip_markdown(content_raw) if content_raw else None

    chunks = {}
    if profile:
        chunks["profile"] = profile
    if location:
        chunks["location"] = location
    if memo_text:
        chunks["memo"] = memo_text
    if menu:
        chunks["menu"] = menu
    if review_text:
        chunks["reviews"] = review_text
    if content_text:
        chunks["content"] = content_text

    return {
        "id": spot.get("id"),
        "name": name,
        "status": spot.get("status", ""),
        "chunks": chunks,
    }
