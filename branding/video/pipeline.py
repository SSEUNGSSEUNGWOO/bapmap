"""
Bapmap 영상 자동 파이프라인
- 사용법: python3 pipeline.py [guide_slug]
          python3 pipeline.py  (최신 published 가이드 자동 선택)
"""

import os, sys, json, pickle
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from supabase import create_client
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from anthropic import Anthropic

ROOT = Path(__file__).parent.parent.parent
CLIENT_SECRET = ROOT / "client_secret_857701025189-p50v85jqql10t06vrtk9pv2jcqti677l.apps.googleusercontent.com.json"
TOKEN_FILE = ROOT / "youtube_token.pickle"
OUTPUT_DIR = Path(__file__).parent / "output"

sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def step_generate(slug: str) -> Path:
    print(f"\n[1/3] 영상 생성: {slug}")
    from generate_guide import generate_guide_video
    out = generate_guide_video(slug)
    if not out:
        raise RuntimeError("영상 생성 실패")
    print(f"[1/3] 완료: {out}")
    return out


def step_metadata(slug: str) -> dict:
    print(f"\n[2/3] SEO 메타데이터 + 캡션 생성...")
    res = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": f"""YouTube/Instagram SEO expert. Korean food Shorts video from Bapmap (bapmap.com).
Video slug: "{slug}"

Return JSON only:
{{
  "title": "under 70 chars. Hook first. Specific, searchable. Example: 'Best Samgyeopsal in Seoul That Locals Actually Eat'",
  "description": "3-4 sentences. First sentence = hook with main keyword. Include what the video covers, bapmap.com link, CTA. End with 15-20 hashtags.",
  "tags": ["15-20 tags mixing high-volume (Seoul food, Korean BBQ, what to eat in Seoul), mid-volume, long-tail. Always include: bapmap, Seoul food guide, Korean food 2025"],
  "instagram_caption": "2-3 punchy sentences. Hook first. No fluff. End with bapmap.com and 10-15 hashtags on separate lines. Tone: cool local friend, not a food blogger."
}}

Rules: specific > generic. No clickbait. Tags tourists actually search."""}]
    )
    text = res.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    meta = json.loads(text)
    print(f"[2/3] 제목: {meta['title']}")

    caption_path = OUTPUT_DIR / f"{slug}_caption.txt"
    caption_path.write_text(
        f"=== YouTube ===\n{meta['title']}\n\n{meta['description']}\n\n"
        f"=== Instagram ===\n{meta['instagram_caption']}\n",
        encoding="utf-8"
    )
    print(f"[2/3] 캡션 저장: {caption_path}")
    return meta


def step_upload(video_path: Path, meta: dict) -> str:
    print(f"\n[3/3] YouTube 업로드...")
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

    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": "22",
            "defaultLanguage": "en",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = yt.videos().insert(part=",".join(body.keys()), body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  업로드 {int(status.progress() * 100)}%...")

    video_id = response["id"]
    url = f"https://youtube.com/shorts/{video_id}"
    print(f"[3/3] 완료: {url}")
    return url


def step_save_url(slug: str, youtube_url: str):
    sb.table("guides").update({"youtube_url": youtube_url}).eq("slug", slug).execute()
    print(f"[DB] youtube_url 저장 완료")


def run(slug: str):
    print(f"=== Bapmap Pipeline: {slug} ===")
    video_path = step_generate(slug)
    meta = step_metadata(slug)
    youtube_url = step_upload(video_path, meta)
    step_save_url(slug, youtube_url)
    print(f"\n=== 완료 ===\n{youtube_url}")


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug:
        r = sb.table("guides").select("slug").eq("status", "published").order("created_at", desc=True).limit(1).execute()
        slug = r.data[0]["slug"] if r.data else None
    if not slug:
        print("가이드 없음")
        sys.exit(1)
    run(slug)
