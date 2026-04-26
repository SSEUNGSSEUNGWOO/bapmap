"""
YouTube Shorts 업로드
- 사용법: python3 upload_youtube.py [video_path]
          python3 upload_youtube.py  (최신 output 영상 자동 선택)
"""

import os, sys, pickle, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from anthropic import Anthropic

ROOT = Path(__file__).parent.parent.parent
CLIENT_SECRET = ROOT / "client_secret_857701025189-p50v85jqql10t06vrtk9pv2jcqti677l.apps.googleusercontent.com.json"
TOKEN_FILE = ROOT / "youtube_token.pickle"
OUTPUT_DIR = Path(__file__).parent / "output"

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_metadata(slug: str) -> dict:
    prompt = f"""You are a YouTube SEO expert writing metadata for a Korean food Shorts video.

The video is from Bapmap (bapmap.com) — a curated guide to local Korean food spots for foreign travelers.
Video slug: "{slug}"

Write YouTube-optimized metadata. Return JSON only:
{{
  "title": "under 70 chars. Hook first. Specific, searchable. No generic phrases. Example: 'Best Samgyeopsal in Seoul That Locals Actually Eat'",
  "description": "3-4 sentences. First sentence = hook with main keyword. Include: what the video covers, bapmap.com link, call to action. End with hashtags (15-20 tags).",
  "tags": ["15-20 tags. Mix of: high-volume (Seoul food, Korean BBQ, what to eat in Seoul), mid-volume (samgyeopsal Seoul, best Korean restaurants), long-tail (best samgyeopsal near Hongdae). Always include: bapmap, Seoul food guide, Korean food 2025"]
}}

Rules:
- Title must include at least one high-search keyword (Seoul food, Korean BBQ, what to eat in Seoul, etc.)
- No clickbait. Specific > generic.
- Tags should be a mix of English keywords tourists actually search"""

    res = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    text = res.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


def get_youtube():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0, prompt="select_account")
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)

    return build("youtube", "v3", credentials=creds)


def upload(video_path: Path, title: str, description: str, tags: list):
    yt = get_youtube()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",  # People & Blogs
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")

    print(f"[Upload] 업로드 중: {video_path.name}")
    request = yt.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[Upload] {int(status.progress() * 100)}%...")

    video_id = response["id"]
    print(f"[Upload] 완료: https://youtube.com/shorts/{video_id}")
    return video_id


if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_path = Path(sys.argv[1])
    else:
        videos = sorted(OUTPUT_DIR.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not videos:
            print("영상 없음")
            sys.exit(1)
        video_path = videos[0]

    print(f"[Upload] 대상: {video_path}")

    slug = video_path.stem
    print("[Upload] 메타데이터 생성 중...")
    meta = generate_metadata(slug)
    print(f"[Upload] 제목: {meta['title']}")
    print(f"[Upload] 태그: {', '.join(meta['tags'][:5])}...")

    upload(video_path, meta["title"], meta["description"], meta["tags"])
