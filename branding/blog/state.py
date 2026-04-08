from typing import TypedDict, Optional


class BlogState(TypedDict):
    post_type: str               # "spot" | "list" | "guide"
    topic: str
    spot_ids: list[str]
    spots_data: list[dict]
    draft: str
    title: str
    meta_description: str
    slug: str
    keywords: list[str]
    eval_score: float
    eval_feedback: str
    approved: bool
    revision_count: int
    published_url: Optional[str]
