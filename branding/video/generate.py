"""
Bapmap 스팟 홍보 영상 자동 생성기
- DB에서 스팟 이미지 가져와서 9:16 쇼츠/릴스 형태로 출력
- 사용법: python generate.py [spot_name]
          python generate.py  (대기중 스팟 자동 선택)
"""

import os
import sys
import json
import tempfile
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import ImageClip, VideoClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx import CrossFadeIn
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from supabase import create_client
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

# 9:16 해상도
W, H = 1080, 1920
SLIDE_DURATION = 2.5   # 이미지당 초
FADE_DURATION = 0.4    # 페이드 시간
FPS = 30

OUTPUT_DIR = Path(__file__).parent / "output"
ASSETS_DIR = Path(__file__).parent / "assets"


def download_image(url: str) -> Image.Image | None:
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        img = Image.open(BytesIO(res.content)).convert("RGB")
        return img
    except Exception as e:
        print(f"[Video] 이미지 다운로드 실패: {url} — {e}")
        return None


def crop_to_916(img: Image.Image) -> Image.Image:
    """이미지를 9:16 비율로 중앙 크롭"""
    iw, ih = img.size
    target_ratio = W / H

    if iw / ih > target_ratio:
        # 좌우 크롭
        new_w = int(ih * target_ratio)
        left = (iw - new_w) // 2
        img = img.crop((left, 0, left + new_w, ih))
    else:
        # 상하 크롭
        new_h = int(iw / target_ratio)
        top = (ih - new_h) // 2
        img = img.crop((0, top, iw, top + new_h))

    return img.resize((W, H), Image.LANCZOS)


FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_BOLD_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(FONT_BOLD_PATH if bold else FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()

def _pill(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, font, bg=(245, 166, 35, 230), fg=(255, 255, 255, 255)):
    """텍스트 필(pill) 버튼 그리기 — 수직 중앙 정렬"""
    pad_x, pad_y = 28, 14
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    rx0, ry0 = x, y
    rx1, ry1 = x + tw + pad_x * 2, y + th + pad_y * 2
    draw.rounded_rectangle([(rx0, ry0), (rx1, ry1)], radius=40, fill=bg)
    draw.text((rx0 + pad_x, ry0 + pad_y - bbox[1]), text, font=font, fill=fg)
    return rx1 - rx0  # 너비 반환

def make_text_overlay(
    name: str, region: str, rating: float, category: str,
    tagline: str = "", price: str = "", subway: str = ""
) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 하단 그라데이션 (600px)
    grad_h = 650
    for i in range(grad_h):
        alpha = int(220 * (i / grad_h) ** 0.6)
        draw.rectangle([(0, H - grad_h + i), (W, H - grad_h + i + 1)], fill=(0, 0, 0, alpha))

    PAD = 72
    y = H - 560

    # 카테고리 필
    f_tag = _font(34, bold=True)
    _pill(draw, category.upper(), PAD, y, f_tag)
    y += 80

    # 스팟 이름
    f_name = _font(80, bold=True)
    draw.text((PAD, y), name, font=f_name, fill=(255, 255, 255, 255))
    bbox = draw.textbbox((PAD, y), name, font=f_name)
    y += bbox[3] - bbox[1] + 16

    # 태그라인
    if tagline:
        f_tag2 = _font(38)
        draw.text((PAD, y), f'"{tagline}"', font=f_tag2, fill=(255, 255, 255, 170))
        bbox = draw.textbbox((PAD, y), f'"{tagline}"', font=f_tag2)
        y += bbox[3] - bbox[1] + 24
    else:
        y += 8

    # 지역 | 별점
    f_info = _font(42)
    info_parts = [f"★ {rating}"]
    if price:
        info_parts.append(price)
    info_parts.append(region)
    draw.text((PAD, y), "  ·  ".join(info_parts), font=f_info, fill=(255, 255, 255, 200))
    bbox = draw.textbbox((PAD, y), "  ·  ".join(info_parts), font=f_info)
    y += bbox[3] - bbox[1] + 16

    # 지하철
    if subway:
        f_sub = _font(36)
        draw.text((PAD, y), f"⬡ {subway}", font=f_sub, fill=(180, 220, 255, 200))
        bbox = draw.textbbox((PAD, y), f"⬡ {subway}", font=f_sub)
        y += bbox[3] - bbox[1] + 20

    # bapmap.com
    f_brand = _font(34, bold=True)
    draw.text((PAD, y), "bapmap.com", font=f_brand, fill=(245, 166, 35, 210))

    # 상단 우측 워터마크
    f_wm = _font(30)
    draw.text((W - 220, 60), "BAPMAP", font=f_wm, fill=(255, 255, 255, 120))

    return overlay


def make_slide(img_pil: Image.Image, duration: float) -> VideoClip:
    """PIL 이미지 → MoviePy 클립 (Ken Burns 줌인 효과)"""
    arr = np.array(img_pil)

    def make_frame(t):
        zoom = 1.0 + 0.08 * (t / duration)
        new_w = int(W * zoom)
        new_h = int(H * zoom)
        resized = Image.fromarray(arr).resize((new_w, new_h), Image.LANCZOS)
        x = (new_w - W) // 2
        y = (new_h - H) // 2
        return np.array(resized.crop((x, y, x + W, y + H)))

    return VideoClip(make_frame, duration=duration)


def generate_video(spot: dict, lang: str = "en") -> Path:
    name = spot.get("english_name") or spot["name"]
    region = spot.get("region") or spot.get("city", "")
    rating = spot.get("rating", 0)
    category = spot.get("category", "")
    tagline = spot.get("tagline") or ""
    price = spot.get("price_level") or ""
    subway = spot.get("subway") or ""

    # 이미지 URL 수집
    urls = []
    if isinstance(spot.get("image_urls"), list):
        urls = spot["image_urls"][:5]
    if not urls and spot.get("image_url"):
        urls = [spot["image_url"]]

    if not urls:
        print(f"[Video] 이미지 없음: {name}")
        return None

    print(f"[Video] 이미지 {len(urls)}장 다운로드 중...")
    images = [download_image(u) for u in urls]
    images = [img for img in images if img]

    if not images:
        print("[Video] 유효한 이미지 없음")
        return None

    # 텍스트 오버레이
    overlay_pil = make_text_overlay(name, region, rating, category, tagline, price, subway)
    overlay_arr = np.array(overlay_pil)

    # 슬라이드 클립 생성
    clips = []
    for i, img in enumerate(images):
        cropped = crop_to_916(img)
        slide = make_slide(cropped, SLIDE_DURATION)
        if i > 0:
            slide = slide.with_effects([CrossFadeIn(FADE_DURATION)])
        clips.append(slide)

    video = concatenate_videoclips(clips, method="compose", padding=-FADE_DURATION)

    # 오버레이 합성
    overlay_clip = ImageClip(overlay_arr, duration=video.duration)
    final = CompositeVideoClip([video, overlay_clip])

    # BGM (assets/bgm.mp3 있으면 사용)
    bgm_path = ASSETS_DIR / "bgm.mp3"
    if bgm_path.exists():
        audio = AudioFileClip(str(bgm_path)).with_duration(final.duration).audio_fadein(0.5).audio_fadeout(1.0)
        final = final.with_audio(audio)

    slug = name.lower().replace(" ", "-").replace("/", "-")
    out_path = OUTPUT_DIR / f"{slug}.mp4"
    print(f"[Video] 렌더링 중: {out_path}")
    final.write_videofile(str(out_path), fps=FPS, codec="libx264", audio_codec="aac", logger=None)
    print(f"[Video] 완료: {out_path}")
    return out_path


if __name__ == "__main__":
    spot_name = sys.argv[1] if len(sys.argv) > 1 else None

    if spot_name:
        res = sb.table("spots").select("*").ilike("name", f"%{spot_name}%").limit(1).execute()
    else:
        res = sb.table("spots").select("*").eq("status", "업로드완료").order("created_at", desc=True).limit(1).execute()

    if not res.data:
        print("스팟 없음")
        sys.exit(1)

    spot = res.data[0]
    print(f"[Video] 생성 시작: {spot.get('english_name') or spot['name']}")
    generate_video(spot)
