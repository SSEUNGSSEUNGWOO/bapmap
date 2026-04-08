import os


def publish(state: dict) -> dict:
    # Phase 2에서 Medium/Reddit API 연동 예정
    # 지금은 로컬 파일로 저장
    import pathlib
    out_dir = pathlib.Path(__file__).parent.parent / "output"
    out_dir.mkdir(exist_ok=True)

    slug = state.get("slug", "post")
    path = out_dir / f"{slug}.md"

    BRAND_HEADER = "*BAPMAP - Recommended by a Korean who actually eats well.*\n\n"

    content = f"""---
title: {state.get('title', '')}
meta_description: {state.get('meta_description', '')}
keywords: {', '.join(state.get('keywords', []))}
eval_score: {state.get('eval_score', 0)}/50
---

{BRAND_HEADER}{state.get('draft', '')}
"""
    path.write_text(content, encoding="utf-8")
    print(f"[Publish] 저장 완료: {path}")
    return {**state, "published_url": str(path)}
