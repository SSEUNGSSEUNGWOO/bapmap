import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "bapmap_marketing.db"


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            url TEXT,
            author TEXT,
            body TEXT,
            created_utc INTEGER,
            score INTEGER,
            fetched_at TEXT DEFAULT (datetime('now')),
            fit_score INTEGER,
            fit_reason TEXT,
            status TEXT DEFAULT 'pending'
        );

        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT,
            draft TEXT,
            reviewer_score INTEGER,
            reviewer_notes TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (opportunity_id) REFERENCES opportunities(id)
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            opportunity_id TEXT,
            draft_id INTEGER,
            adopted INTEGER,
            reject_reason TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS daily_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            report_path TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("DB 초기화 완료:", DB_PATH)
