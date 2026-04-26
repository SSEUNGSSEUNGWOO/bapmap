"""
Bapmap 가이드 홍보 영상 생성기
- 가이드 1개 → 스팟별 슬라이드 → 9:16 쇼츠/릴스
- 사용법: python3 generate_guide.py [guide_slug]
          python3 generate_guide.py  (최신 가이드 자동 선택)
"""

import os, sys, json, re, tempfile
import requests
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import VideoClip, ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, concatenate_audioclips
from moviepy.video.fx import CrossFadeIn
from narration import build_narrations
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")
from supabase import create_client
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

W, H = 1080, 1920
FPS = 30
SLIDE_DUR = 4.0
FADE_DUR  = 0.35
OUTPUT_DIR = Path(__file__).parent / "output"
ASSETS_DIR = Path(__file__).parent / "assets"

ORANGE = (245, 166, 35)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)

FONT_REG  = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
LOGO_PATH = Path(__file__).parent.parent.parent / "web/public/logo.png"

def fnt(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)
    except Exception:
        return ImageFont.load_default()

def is_korean(text: str) -> bool:
    korean = len(re.findall(r'[\uAC00-\uD7A3\u3131-\u318E]', text))
    return korean > len(text) * 0.2  # 20% 이상 한국어면 스킵

def en_only(text: str) -> str:
    """한국어 문자 전부 제거, 가격 정리"""
    text = re.sub(r'\([^)]*[\uAC00-\uD7A3][^)]*\)', '', text)   # 괄호 안 한국어 블록
    text = re.sub(r'[\uAC00-\uD7A3\u3131-\u318E]+', '', text)   # 나머지 한국어 문자
    text = re.sub(r'\d+,\d+원', '', text)                         # 14,000원 형식
    text = re.sub(r'\s{2,}', ' ', text)                           # 공백 정리
    return text.strip(" ,.-—")

def paste_logo(img: Image.Image, width: int = 200, x: int = None, y: int = 52, alpha: int = 180):
    """우상단에 로고 붙이기"""
    if not LOGO_PATH.exists():
        return
    logo = Image.open(LOGO_PATH).convert("RGBA")
    ratio = width / logo.width
    logo = logo.resize((width, int(logo.height * ratio)), Image.LANCZOS)
    # 알파 조정
    r, g, b, a = logo.split()
    a = a.point(lambda p: int(p * alpha / 255))
    logo.putalpha(a)
    px = (W - width - 60) if x is None else x
    img.paste(logo, (px, y), logo)

def draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int, color):
    """5각별 직접 그리기"""
    import math
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.4
        points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    draw.polygon(points, fill=color)

def download_image(url: str):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return Image.open(BytesIO(r.content)).convert("RGB")
    except Exception:
        return None

def crop916(img: Image.Image) -> Image.Image:
    iw, ih = img.size
    ratio = W / H
    if iw / ih > ratio:
        nw = int(ih * ratio)
        img = img.crop(((iw - nw) // 2, 0, (iw + nw) // 2, ih))
    else:
        nh = int(iw / ratio)
        img = img.crop((0, (ih - nh) // 2, iw, (ih + nh) // 2))
    return img.resize((W, H), Image.LANCZOS)

def gradient(draw, top_y, height, max_alpha=210):
    for i in range(height):
        a = int(max_alpha * (i / height) ** 0.55)
        draw.rectangle([(0, top_y + i), (W, top_y + i + 1)], fill=(*BLACK, a))

def pill(draw, text, x, y, font, bg=(*ORANGE, 230), fg=(*WHITE, 255)):
    px, py = 28, 12
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.rounded_rectangle([(x, y), (x + tw + px*2, y + th + py*2)], radius=40, fill=bg)
    draw.text((x + px, y + py - bb[1]), text, font=font, fill=fg)
    return th + py * 2

def wrapped_lines(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textbbox((0,0), test, font=font)[2] <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

# ── 슬라이드 오버레이들 ──────────────────────────────────────────

def overlay_intro(title: str, subtitle: str) -> Image.Image:
    """인트로: 가이드 제목 + 부제"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 전체 반투명 다크
    gradient(draw, H // 3, H * 2 // 3, max_alpha=190)

    PAD, MAX_W = 80, W - 160
    y = H // 2 - 80

    # 로고
    paste_logo(img, width=220, x=PAD, y=y, alpha=220)
    y += 90

    # 제목 (줄바꿈)
    f_title = fnt(76, bold=True)
    lines = wrapped_lines(draw, title, f_title, MAX_W)
    for line in lines:
        draw.text((PAD, y), line, font=f_title, fill=(*WHITE, 255))
        bb = draw.textbbox((PAD, y), line, font=f_title)
        y += bb[3] - bb[1] + 8

    y += 16
    # 부제
    f_sub = fnt(42)
    sub_lines = wrapped_lines(draw, subtitle, f_sub, MAX_W)
    for line in sub_lines:
        draw.text((PAD, y), line, font=f_sub, fill=(*WHITE, 180))
        bb = draw.textbbox((PAD, y), line, font=f_sub)
        y += bb[3] - bb[1] + 6

    return img

def truncate(draw, text, font, max_w):
    while draw.textbbox((0,0), text, font=font)[2] > max_w and len(text) > 4:
        text = text[:-2] + "…"
    return text

def overlay_spot_a(name: str, category: str, region: str, rating: float,
                   index: int, total: int) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    gradient(draw, H - 620, 620, max_alpha=200)

    PAD, MAX_W = 80, W - 160
    y = H - 570

    # 카운터 필
    f_sm = fnt(32, bold=True)
    pill(draw, f"{index} / {total}", PAD, y, f_sm, bg=(20, 20, 20, 180))
    y += 72

    # 카테고리 필 (오렌지)
    pill(draw, category.upper(), PAD, y, f_sm)
    y += 72

    # 구분선
    draw.rectangle([(PAD, y), (PAD + 60, y + 4)], fill=(*ORANGE, 200))
    y += 24

    # 스팟 이름 (길이에 따라 폰트 자동 축소, 최대 2줄)
    for size in [86, 72, 60, 50, 44, 38]:
        f_name = fnt(size, bold=True)
        lines = wrapped_lines(draw, name, f_name, MAX_W)
        if len(lines) <= 2:
            break
    lines = lines[:2]
    for line in lines:
        draw.text((PAD, y), line, font=f_name, fill=(*WHITE, 255))
        bb = draw.textbbox((PAD, y), line, font=f_name)
        y += bb[3] - bb[1] + 4
    y += 18

    # 별점 + 지역
    f_info = fnt(40)
    star_cy = y + 22
    draw_star(draw, PAD + 16, star_cy, 16, (*ORANGE, 255))
    region_clean = en_only(region)
    info_text = f"{rating}   {region_clean}"
    draw.text((PAD + 42, y), info_text, font=f_info, fill=(*WHITE, 195))

    # 우상단 워터마크
    paste_logo(img)

    return img

def overlay_spot_b(what_to_order: list, subway: str, price: str) -> Image.Image:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    gradient(draw, H - 700, 700, max_alpha=210)

    PAD, MAX_W = 80, W - 160
    y = H - 650

    # 헤더
    f_hdr = fnt(30, bold=True)
    pill(draw, "WHAT TO ORDER", PAD, y, f_hdr, bg=(20, 20, 20, 190))
    y += 68

    # 구분선
    draw.rectangle([(PAD, y), (PAD + 60, y + 4)], fill=(*ORANGE, 200))
    y += 24

    # 메뉴 아이템 (최대 2개)
    f_item = fnt(48, bold=True)
    f_desc = fnt(34)
    shown = 0
    for item in what_to_order:
        if shown >= 2:
            break
        item = en_only(item)
        if not item or is_korean(item):
            continue
        parts = item.split(" — ", 1)
        name_part = truncate(draw, parts[0].strip(), f_item, MAX_W - 20)

        # 아이템 이름
        draw.text((PAD, y), name_part, font=f_item, fill=(*WHITE, 255))
        bb = draw.textbbox((PAD, y), name_part, font=f_item)
        y += bb[3] - bb[1] + 6

        # 설명 (최대 2줄)
        if len(parts) > 1:
            desc = en_only(parts[1].strip())
            if desc:
                for dline in wrapped_lines(draw, desc, f_desc, MAX_W)[:2]:
                    draw.text((PAD, y), dline, font=f_desc, fill=(*WHITE, 155))
                    bb = draw.textbbox((PAD, y), dline, font=f_desc)
                    y += bb[3] - bb[1] + 2

        y += 28
        shown += 1

    paste_logo(img)
    return img

def overlay_outro(spot_count: int) -> Image.Image:
    """아웃트로: CTA"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    gradient(draw, H // 2, H // 2, max_alpha=230)

    PAD = 80
    y = H * 3 // 5

    f_big = fnt(72, bold=True)
    draw.text((PAD, y), f"{spot_count} local spots.", font=f_big, fill=(*WHITE, 255))
    y += 90
    draw.text((PAD, y), "Zero tourist traps.", font=f_big, fill=(*WHITE, 255))
    y += 110

    f_mid = fnt(48)
    draw.text((PAD, y), "Find them all at", font=f_mid, fill=(*WHITE, 180))
    y += 68

    f_url = fnt(62, bold=True)
    draw.text((PAD, y), "bapmap.com", font=f_url, fill=(*ORANGE, 255))
    y += 90
    paste_logo(img, width=200, x=PAD, y=y, alpha=200)

    return img

# ── 클립 생성 헬퍼 ──────────────────────────────────────────────

def make_slide(img_pil: Image.Image, duration: float, zoom_dir: str = "in") -> VideoClip:
    arr = np.array(img_pil)
    def make_frame(t):
        p = t / duration
        zoom = 1.0 + 0.07 * (p if zoom_dir == "in" else 1 - p)
        nw, nh = int(W * zoom), int(H * zoom)
        resized = Image.fromarray(arr).resize((nw, nh), Image.LANCZOS)
        x, y = (nw - W) // 2, (nh - H) // 2
        return np.array(resized.crop((x, y, x + W, y + H)))
    return VideoClip(make_frame, duration=duration)

def composite(slide: VideoClip, overlay_pil: Image.Image, do_fade: bool = False) -> CompositeVideoClip:
    if do_fade:
        slide = slide.with_effects([CrossFadeIn(FADE_DUR)])
    ov = ImageClip(np.array(overlay_pil), duration=slide.duration)
    return CompositeVideoClip([slide, ov])

# ── 메인 ────────────────────────────────────────────────────────

def generate_guide_video(guide_slug: str) -> Path:
    # 가이드 데이터
    gr = sb.table("guides").select("*").eq("slug", guide_slug).single().execute()
    if not gr.data:
        print(f"가이드 없음: {guide_slug}")
        return None
    guide = gr.data

    # 스팟 데이터
    spot_names = guide["spot_slugs"]
    sr = sb.table("spots").select("*").eq("status", "업로드완료").in_("english_name", spot_names).execute()
    order_map = {s: i for i, s in enumerate(spot_names)}
    spots = sorted(sr.data, key=lambda s: order_map.get(s.get("english_name", ""), 99))

    if not spots:
        print("스팟 없음")
        return None

    # ── 이미지 다운로드 ──
    cover_url = guide.get("cover_image")
    intro_bg = download_image(cover_url) if cover_url else None
    if intro_bg is None:
        for spot in spots:
            urls = spot.get("image_urls") or []
            if not urls and spot.get("image_url"): urls = [spot["image_url"]]
            if urls:
                intro_bg = download_image(urls[0])
                break
    if intro_bg is None:
        intro_bg = Image.new("RGB", (W, H), (20, 20, 20))

    spot_imgs = []
    valid_spots = []
    for spot in spots:
        urls = spot.get("image_urls") or []
        if not urls and spot.get("image_url"): urls = [spot["image_url"]]
        imgs = [img for img in [download_image(u) for u in urls[:2]] if img]
        if not imgs:
            print(f"[Video] 이미지 없음: {spot.get('english_name')}")
            continue
        spot_imgs.append(imgs)
        valid_spots.append(spot)
    spots = valid_spots

    # ── 나레이션 생성 ──
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        narrations = build_narrations(guide, spots, tmp_dir)
        nar_map = {n["slide"]: n for n in narrations}

        def dur(slide_id, fallback=4.0):
            return nar_map[slide_id]["duration"] if slide_id in nar_map else fallback

        def audio_clip(slide_id):
            if slide_id in nar_map:
                return AudioFileClip(str(nar_map[slide_id]["audio"]))
            return None

        clips = []
        audio_clips = []

        # 인트로
        intro_img = crop916(intro_bg)
        d = dur("intro", 4.0)
        clip = composite(make_slide(intro_img, d), overlay_intro(guide["title"], guide["subtitle"]), do_fade=False)
        clips.append(clip)
        if ac := audio_clip("intro"): audio_clips.append(ac)

        # 스팟 슬라이드
        for i, spot in enumerate(spots):
            imgs = spot_imgs[i]
            img_a = crop916(imgs[0])
            img_b = crop916(imgs[1] if len(imgs) > 1 else imgs[0])
            name = spot.get("english_name") or spot["name"]
            category = spot.get("category", "")
            region = spot.get("region") or spot.get("city", "")
            rating = spot.get("rating", 0)
            what_to_order = spot.get("what_to_order") or []
            price = spot.get("price_level") or ""
            subway = spot.get("subway") or ""

            d_a = dur(f"spot_a_{i}", SLIDE_DUR)
            d_b = dur(f"spot_b_{i}", SLIDE_DUR)

            ov_a = overlay_spot_a(name, category, region, rating, i + 1, len(spots))
            clips.append(composite(make_slide(img_a, d_a, "in"), ov_a, do_fade=True))
            if ac := audio_clip(f"spot_a_{i}"): audio_clips.append(ac)

            ov_b = overlay_spot_b(what_to_order, subway, price)
            clips.append(composite(make_slide(img_b, d_b, "out"), ov_b, do_fade=True))
            if ac := audio_clip(f"spot_b_{i}"): audio_clips.append(ac)

        # 아웃트로
        d = dur("outro", 3.0)
        outro_img = crop916(intro_bg)
        clips.append(composite(make_slide(outro_img, d), overlay_outro(len(spots)), do_fade=True))
        if ac := audio_clip("outro"): audio_clips.append(ac)

        # ── 합치기 ──
        video = concatenate_videoclips(clips, method="compose", padding=-FADE_DUR)

        # 나레이션 오디오 연결
        if audio_clips:
            full_audio = concatenate_audioclips(audio_clips).with_duration(video.duration)
            video = video.with_audio(full_audio)

        # BGM (있으면 나레이션 위에 낮게 믹스)
        bgm_path = ASSETS_DIR / "bgm.mp3"
        if bgm_path.exists() and audio_clips:
            bgm = AudioFileClip(str(bgm_path)).with_duration(video.duration).volumex(0.12).audio_fadeout(1.0)
            from moviepy import CompositeAudioClip
            video = video.with_audio(CompositeAudioClip([video.audio, bgm]))

    out_path = OUTPUT_DIR / f"{guide_slug}.mp4"
    print(f"[Video] 렌더링 중 ({len(clips)}개 클립, {video.duration:.1f}초)...")
    video.write_videofile(str(out_path), fps=FPS, codec="libx264", audio_codec="aac", logger=None)
    print(f"[Video] 완료: {out_path}")
    return out_path


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug:
        r = sb.table("guides").select("slug").eq("status", "published").order("created_at", desc=True).limit(1).execute()
        slug = r.data[0]["slug"] if r.data else None
    if not slug:
        print("가이드 없음")
        sys.exit(1)
    print(f"[Video] 가이드: {slug}")
    generate_guide_video(slug)
