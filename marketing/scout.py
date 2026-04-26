"""
Reddit JSON 엔드포인트로 신규 글 크롤링 (API 키 불필요)
실행: python -m marketing.scout
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from marketing.db import get_conn, init_db

SUBREDDITS = ["koreatravel", "seoul", "Korea"]

KEYWORDS = [
    "where to eat", "restaurant", "food", "where should i eat",
    "eat in", "dining", "dinner", "lunch", "breakfast", "cafe",
    "first time", "vegetarian", "vegan", "halal", "no english",
    "recommendation", "suggest", "local food", "street food",
    "korean food", "k-food", "itinerary", "what to eat",
]

BLOCKLIST = [
    "hiring", "visa", "apartment", "rent", "job", "roommate",
    "moving to", "living in", "dating", "relationship",
]

HEADERS = {"User-Agent": "bapmap-scout/1.0 (personal use)"}


def _fetch(subreddit: str, limit: int = 50) -> list[dict]:
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return [p["data"] for p in data["data"]["children"]]


def _matches(post: dict) -> bool:
    text = (post.get("title", "") + " " + post.get("selftext", "")).lower()
    if any(b in text for b in BLOCKLIST):
        return False
    return any(k in text for k in KEYWORDS)


def _already_seen(conn, post_id: str) -> bool:
    row = conn.execute("SELECT id FROM opportunities WHERE id = ?", (post_id,)).fetchone()
    return row is not None


def run(max_per_sub: int = 50) -> list[dict]:
    init_db()
    conn = get_conn()
    new_posts = []

    for sub in SUBREDDITS:
        try:
            posts = _fetch(sub, max_per_sub)
            time.sleep(1)
        except Exception as e:
            print(f"[Scout] {sub} 크롤링 실패: {e}")
            continue

        for p in posts:
            if not _matches(p):
                continue
            if _already_seen(conn, p["id"]):
                continue

            row = {
                "id": p["id"],
                "subreddit": sub,
                "title": p.get("title", ""),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "author": p.get("author", ""),
                "body": p.get("selftext", "")[:2000],
                "created_utc": int(p.get("created_utc", 0)),
                "score": p.get("score", 0),
            }
            conn.execute("""
                INSERT OR IGNORE INTO opportunities
                (id, subreddit, title, url, author, body, created_utc, score)
                VALUES (:id, :subreddit, :title, :url, :author, :body, :created_utc, :score)
            """, row)
            new_posts.append(row)

        print(f"[Scout] r/{sub}: {len(posts)}개 중 신규 {sum(1 for p in posts if _matches(p))}개 후보")

    conn.commit()
    conn.close()
    print(f"[Scout] 신규 후보 총 {len(new_posts)}개 저장")
    print(json.dumps(new_posts, ensure_ascii=False))
    return new_posts


if __name__ == "__main__":
    run()
