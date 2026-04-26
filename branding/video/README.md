# Bapmap Video Pipeline

로컬에서만 실행. Streamlit admin에서는 돌리지 않음 (FFmpeg + OAuth 제약).

## 실행

```bash
cd /Users/sseung/Documents/business/Bapmap

# 영상 생성 + YouTube 업로드 한 번에
python3 branding/video/pipeline.py best-samgyeopsal-seoul

# slug 없이 → 최신 published 가이드 자동 선택
python3 branding/video/pipeline.py
```

## 단계별 실행

```bash
# 영상만 생성 (output/{slug}.mp4)
python3 branding/video/generate_guide.py best-samgyeopsal-seoul

# 업로드만 (최신 mp4 자동 선택)
python3 branding/video/upload_youtube.py

# 특정 파일 업로드
python3 branding/video/upload_youtube.py branding/video/output/best-samgyeopsal-seoul.mp4
```

## 파이프라인 흐름

```
[1/3] generate_guide.py
  - Supabase에서 가이드 + 스팟 fetch
  - 이미지 다운로드
  - Claude Haiku로 나레이션 스크립트 생성
  - edge-tts로 슬라이드별 mp3 생성
  - PIL 오버레이 + Ken Burns 효과 + CrossFadeIn
  - 나레이션 + BGM 믹스
  - output/{slug}.mp4 렌더링 (1080x1920, 30fps)

[2/3] Claude Haiku → SEO 메타데이터 (제목/설명/태그)

[3/3] YouTube Data API v3
  - OAuth 토큰: youtube_token.pickle (최초 1회 브라우저 인증)
  - public 업로드
  - guides.youtube_url DB 저장
```

## 파일 구조

```
branding/video/
├── pipeline.py          # 메인 (생성 + 업로드 + DB 저장)
├── generate_guide.py    # 영상 생성
├── narration.py         # 나레이션 스크립트 + TTS
├── upload_youtube.py    # YouTube 업로드 (단독 실행용)
├── assets/
│   └── bgm.mp3          # 배경음악 (없으면 나레이션만)
└── output/              # 생성된 mp4 저장
```

## 초기 설정 (최초 1회)

1. 밥맵 루트에 `client_secret_*.json` (Google Cloud OAuth Desktop 앱) 넣기
2. `python3 pipeline.py` 실행 → 브라우저에서 `sseungsseungwoo@gmail.com` 으로 인증
3. `youtube_token.pickle` 생성됨 → 이후 자동 재사용
