# Bapmap Branding 파이프라인 개요

## 폴더 구조

```
branding/
├── blog/          # 블로그 포스트 자동 생성
├── video/         # YouTube Shorts 영상 자동 생성
└── OVERVIEW.md    # 이 파일
```

---

## 1. 블로그 파이프라인 (`blog/`)

### 실행
```bash
# 가이드 기반 리스트 포스트
python3 branding/blog/run.py --type guide --guide-id {UUID} --target local

# 로컬 저장 후 미디엄 업로드
python3 branding/blog/run.py --type guide --guide-id {UUID} --target medium

# 단일 스팟 포스트
python3 branding/blog/run.py --type spot --spot-ids {id}
```

### 에이전트 흐름 (LangGraph)
```
spot_fetch → writer → seo_geo → eval → publish
```

| 에이전트 | 역할 |
|---|---|
| `spot_fetch` | Supabase에서 가이드/스팟 데이터 fetch |
| `writer` | Claude Sonnet으로 블로그 포스트 작성 (500-1000자) |
| `seo_geo` | Claude Haiku로 제목/메타/슬러그/키워드 최적화, GEO(AI 검색 최적화) 적용 |
| `eval` | 퀄리티 평가 (50점 만점, 42점 이상 통과) |
| `publish` | 로컬 md 저장 또는 미디엄 Selenium 자동 업로드 |

### 생성된 포스트 (`blog/output/`)
| 파일 | 내용 |
|---|---|
| `late-night-seoul-bars-drinks.md` | 서울 심야 바/술집 4곳 리스트 |
| `menya-konoha-seongsu-ramen.md` | 멘야코노하 성수 단일 스팟 |
| `seoul-cherry-blossom-where-to-eat-locals.md` | 벚꽃 시즌 서울 맛집 4곳 |

### 미디엄 업로드
- Safari + Selenium으로 자동 로그인 → 글 작성 → 태그 추가 → 발행
- 로컬에서만 실행 가능 (브라우저 필요)
- 하루 2-3개 이상 올리면 계정 제한 위험

---

## 2. 영상 파이프라인 (`video/`)

### 실행
```bash
# 가이드 slug로 전체 파이프라인 (영상 생성 + YouTube 업로드 + DB 저장)
python3 branding/video/pipeline.py best-samgyeopsal-seoul

# slug 없이 → 최신 published 가이드 자동 선택
python3 branding/video/pipeline.py

# 영상만 생성
python3 branding/video/generate_guide.py best-samgyeopsal-seoul

# YouTube 업로드만 (최신 mp4 자동 선택)
python3 branding/video/upload_youtube.py
```

### 파이프라인 흐름
```
[1/3] generate_guide.py  →  영상 생성
[2/3] Claude Haiku       →  SEO 메타데이터 + 인스타 캡션 생성
[3/3] YouTube API        →  업로드 + DB youtube_url 저장
```

### 영상 생성 상세
- 해상도: 1080x1920 (9:16 Shorts/Reels)
- FPS: 30
- 슬라이드 구성: 인트로 → 스팟 A(이름/별점) → 스팟 B(What to Order) → 아웃트로
- 효과: Ken Burns 줌, CrossFadeIn 0.35초
- 나레이션: Claude Haiku 스크립트 → edge-tts (en-US-GuyNeural)
- BGM: `assets/bgm.mp3` 있으면 나레이션 위에 낮게 믹스 (볼륨 12%)
- 목표 길이: 50-60초

### 생성된 파일 (`video/output/`)
| 파일 | 상태 |
|---|---|
| `best-samgyeopsal-seoul.mp4` | YouTube 업로드 완료 (`youtube.com/shorts/axwl26094qE`) |
| `late-night-seoul.mp4` | 로컬 생성 완료 |
| `cherry-blossom-seoul-where-to-eat.mp4` | 로컬 생성 완료 |
| `where-to-eat-in-myeongdong.mp4` | 로컬 생성 완료 |
| `idaepaljjuggumi.mp4` | 로컬 생성 완료 |

### 캡션 파일
- `output/{slug}_caption.txt` — YouTube 설명 + 인스타 캡션 자동 생성
- 인스타/틱톡 수동 업로드 시 복붙 사용

### YouTube 설정
- 채널: [@bapmap-guide](https://www.youtube.com/@bapmap-guide)
- 계정: sseungsseungwoo@gmail.com
- OAuth 토큰: `youtube_token.pickle` (루트 폴더, 최초 1회 브라우저 인증)
- 기본 공개 설정: public

### 주의사항
- **로컬에서만 실행** (Streamlit Cloud 불가 — FFmpeg + OAuth 제약)
- 영상 렌더링 소요 시간: 스팟 수에 따라 3-10분
- `client_secret_*.json`, `youtube_token.pickle` → `.gitignore` 처리됨
