import os
import re
import pathlib


def publish(state: dict) -> dict:
    out_dir = pathlib.Path(__file__).parent.parent / "output"
    out_dir.mkdir(exist_ok=True)

    slug = state.get("slug", "post")
    path = out_dir / f"{slug}.md"

    BRAND_HEADER = "*BAPMAP - Recommended by a Korean who actually eats well.*\n\n"

    # 커버 이미지: 가이드 cover_image 우선, 없으면 첫 스팟 이미지
    guide = state.get("guide_data") or {}
    spots = state.get("spots_data") or []
    cover_image = guide.get("cover_image") or (spots[0].get("image_url") if spots else None)
    cover_md = f"![]({cover_image})\n\n" if cover_image else ""

    # 본문에 스팟 이미지 삽입
    draft = state.get("draft", "")
    draft = _inject_spot_images(draft, spots)

    content = f"""---
title: {state.get('title', '')}
meta_description: {state.get('meta_description', '')}
keywords: {', '.join(state.get('keywords', []))}
eval_score: {state.get('eval_score', 0)}/50
---

{BRAND_HEADER}{cover_md}{draft}
"""
    path.write_text(content, encoding="utf-8")
    print(f"[Publish] 저장 완료: {path}")
    return {**state, "published_url": str(path)}


def _inject_spot_images(draft: str, spots: list[dict]) -> str:
    for spot in spots:
        img = (spot.get("image_urls") or [None])[0] or spot.get("image_url")
        if not img:
            continue
        name = spot.get("english_name") or spot.get("name", "")
        # 스팟 이름이 ## 헤더로 나오면 그 아래에 이미지 삽입
        pattern = rf"(##[^\n]*{re.escape(name.split()[0])}[^\n]*\n)"
        replacement = rf"\1\n![]({img})\n\n"
        draft = re.sub(pattern, replacement, draft, flags=re.IGNORECASE)
    return draft
