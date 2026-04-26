"""
어제 채택/거절 피드백 저장
실행: python -m marketing.feedback <opportunity_id> <draft_id> <adopted: 1/0> [reason]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from marketing.db import get_conn, init_db


def save_feedback(opportunity_id: str, draft_id: int, adopted: bool, reason: str = ""):
    init_db()
    conn = get_conn()
    conn.execute("""
        INSERT INTO feedback (opportunity_id, draft_id, adopted, reject_reason)
        VALUES (?, ?, ?, ?)
    """, (opportunity_id, draft_id, int(adopted), reason))
    conn.execute(
        "UPDATE opportunities SET status = ? WHERE id = ?",
        ("adopted" if adopted else "rejected", opportunity_id)
    )
    conn.commit()
    conn.close()
    print(f"피드백 저장: {opportunity_id} → {'채택' if adopted else '거절'}")


def get_recent_feedback(days: int = 7) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT f.*, o.title, o.subreddit
        FROM feedback f
        JOIN opportunities o ON f.opportunity_id = o.id
        WHERE f.created_at >= datetime('now', ?)
        ORDER BY f.created_at DESC
    """, (f"-{days} days",)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("사용법: python -m marketing.feedback <opp_id> <draft_id> <1/0> [reason]")
        sys.exit(1)
    save_feedback(sys.argv[1], int(sys.argv[2]), sys.argv[3] == "1",
                  sys.argv[4] if len(sys.argv) > 4 else "")
