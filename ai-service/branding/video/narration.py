"""
나레이션 생성 + TTS 변환
- Claude로 슬라이드별 스크립트 생성
- edge-tts로 음성 파일 생성
"""

import asyncio
import json
import tempfile
from pathlib import Path
from pathlib import Path as _Path
from dotenv import load_dotenv as _load
_load(_Path(__file__).parent.parent.parent / ".env")

from anthropic import Anthropic
import os
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

VOICE = "en-US-GuyNeural"  # 자연스러운 남성 목소리

NARRATION_PROMPT = """You are writing short, punchy narration for a 35-second Instagram Reel / YouTube Shorts about Korean food spots.

Tone: like a cool local friend — confident, specific, no fluff. NOT a food blogger, NOT a tourist guide.
Style: short sentences. Impact over information. Make people want to go.

Guide info:
{guide}

Spots:
{spots}

Write narration for each slide. Return JSON only:
{{
  "intro": "2 sentences max. Hook. Why these spots.",
  "spots": [
    {{
      "name_slide": "1 sentence. Spot name + one sharp fact.",
      "order_slide": "1-2 sentences. What to get. Be specific."
    }}
  ],
  "outro": "1-2 sentences. CTA. bapmap.com."
}}

Rules:
- Intro: MAX 6 words. One punchy hook sentence.
- name_slide: MAX 7 words. Spot name + one sharp fact.
- order_slide: MAX 7 words. One dish. One reason.
- Outro: MAX 6 words. CTA only.
- Total target: 50-55 seconds spoken aloud.
- No "hidden gem", "must-try", "culinary journey"
- Use the spot's actual dish names
- Make it feel like insider knowledge"""


def generate_narration(guide: dict, spots: list) -> dict:
    guide_info = {
        "title": guide["title"],
        "subtitle": guide["subtitle"],
    }
    spots_info = [
        {
            "name": s.get("english_name") or s["name"],
            "category": s.get("category", ""),
            "region": s.get("region") or s.get("city", ""),
            "tagline": s.get("tagline") or "",
            "what_to_order": s.get("what_to_order") or [],
            "memo": (s.get("memo") or "")[:200],
        }
        for s in spots
    ]

    res = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": NARRATION_PROMPT.format(
                guide=json.dumps(guide_info, ensure_ascii=False),
                spots=json.dumps(spots_info, ensure_ascii=False, indent=2),
            )
        }]
    )
    text = res.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)


async def _tts(text: str, path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(path))


def text_to_speech(text: str, path: Path):
    asyncio.run(_tts(text, path))


def get_audio_duration(path: Path) -> float:
    """음성 파일 길이 (초)"""
    from moviepy import AudioFileClip
    clip = AudioFileClip(str(path))
    dur = clip.duration
    clip.close()
    return dur


def build_narrations(guide: dict, spots: list, tmp_dir: Path) -> list:
    """
    나레이션 생성 + TTS 변환
    반환: [{"text": ..., "audio": Path, "duration": float, "slide": "intro"|"spot_a_0"|"spot_b_0"|"outro"}]
    """
    print("[TTS] 나레이션 생성 중...")
    script = generate_narration(guide, spots)
    print(f"[TTS] 스크립트:\n{json.dumps(script, indent=2, ensure_ascii=False)}")

    items = []

    MAX_DUR = {"intro": 5.0, "outro": 4.0, "spot": 5.5}

    def add(slide_id, text):
        audio_path = tmp_dir / f"{slide_id}.mp3"
        print(f"[TTS] 음성 생성: {slide_id} — \"{text}\"")
        text_to_speech(text, audio_path)
        raw = get_audio_duration(audio_path)
        kind = "intro" if slide_id == "intro" else "outro" if slide_id == "outro" else "spot"
        dur = min(raw + 0.6, MAX_DUR[kind])
        items.append({"slide": slide_id, "text": text, "audio": audio_path, "duration": dur})

    add("intro", script["intro"])

    for i, spot_script in enumerate(script["spots"]):
        add(f"spot_a_{i}", spot_script["name_slide"])
        add(f"spot_b_{i}", spot_script["order_slide"])

    add("outro", script["outro"])

    return items
