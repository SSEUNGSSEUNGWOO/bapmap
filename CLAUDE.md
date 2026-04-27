# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 폴더 구조

```
bapmap/
├── frontend/        # Next.js 웹사이트
├── ai-service/      # Python: admin, pipeline, marketing, branding, memory
├── docs/            # 추가 문서
├── CLAUDE.md
└── README.md
```

## Commands

### Python (Admin + Pipeline)
```bash
cd ai-service

# 어드민 UI 실행
streamlit run admin.py

# 스팟 임베딩 (BGE-M3, spot_chunks 테이블)
python -m pipeline.rag.embed_v2 --cap 512

# OpenAI 임베딩 누락분 채우기 (spots.embedding 필드, 웹 검색용)
python -m pipeline.rag.embed --missing
```

### 콘텐츠 발행 (Claude Code 커맨드)
```bash
# 신규 스팟 발굴 + 블로그 포스팅 발행
/spot-publish          # 기본 5개
/spot-publish 3        # N개 지정

# 스팟 묶어서 가이드 발행
/guide-publish

# 일일 마케팅 브리핑 (Reddit 기회 발굴 + 댓글 초안)
/marketing
```

### 브랜딩
```bash
cd ai-service

# Blue Ribbon 로그인 (쿠키 갱신 필요할 때)
.venv/bin/python branding/blog/login.py

# YouTube Shorts 영상 + 업로드
python3 branding/video/pipeline.py {guide-slug}
python3 branding/video/upload_youtube.py
```

### Next.js (Frontend)
```bash
cd frontend
npm run dev      # 개발 서버 (localhost:3000)
npm run build    # 프로덕션 빌드
npm run lint     # ESLint
```

## 아키텍처 개요

### 콘텐츠 발행 흐름

모든 LLM 생성(포스팅/가이드 작성, 품질 평가, 번역)은 Claude Code가 직접 담당. API 종량제 비용 없음.

```
[스팟 발행 /spot-publish]
ai-service/branding/blog/agents/discover.py   → Blue Ribbon 크롤링 (쿠키 필요)
ai-service/branding/blog/agents/ingest.py     → Google Places API → Supabase 저장
Claude Code                                   → 포스팅 작성 → 품질 평가(60점) → 일본어 번역 → 검수
ai-service/pipeline/rag/embed_v2.py           → BGE-M3 임베딩 → spot_chunks 테이블

[가이드 발행 /guide-publish]
Supabase 미사용 스팟 조회 → Claude Code 클러스터링 → 평가(25점) → 사용자 선택
→ 가이드 본문 작성 → 품질 평가(60점) → 일본어 번역 → 검수 → Supabase 저장
ai-service/pipeline/rag/embed_guides.py → OpenAI 1536d 임베딩 → guides.embedding

[마케팅 /marketing]
ai-service/marketing/scout.py  → Reddit JSON 엔드포인트 크롤링 (API 키 불필요)
→ SQLite 저장 → Claude Code 적합도 평가 → 댓글 초안 → 검토 → 일일 리포트
```

### Supabase 핵심 테이블/RPC

| 이름 | 유형 | 역할 |
|---|---|---|
| `spots` | 테이블 | 스팟 전체 데이터 + OpenAI 1536d 임베딩 |
| `spot_chunks` | 테이블 | BGE-M3 임베딩 (RAG v2, Admin 임베딩 버튼) |
| `guides` | 테이블 | 가이드 (spot_slugs로 스팟 연결) + OpenAI 1536d 임베딩 |
| `hybrid_search_spots` | RPC | 벡터 + FTS + RRF 하이브리드 검색 |
| `search_guides` | RPC | 가이드 벡터 유사도 검색 |

### 임베딩 이중 전략

- **스팟 v1**: `ai-service/pipeline/rag/embed.py` → OpenAI `text-embedding-3-small` → `spots.embedding` (1536d) — 웹 검색에서 사용
- **스팟 v2**: `ai-service/pipeline/rag/embed_v2.py` → BGE-M3 → `spot_chunks` — Admin 임베딩 버튼, API 비용 없음. 기본 incremental, `--rebuild-all` 명시 시 전체 재구축
- **가이드**: `ai-service/pipeline/rag/embed_guides.py` → OpenAI `text-embedding-3-small` → `guides.embedding` (1536d) — `search_guides` RPC가 사용

### 웹 API Routes

| 경로 | 역할 |
|---|---|
| `frontend/app/api/search/route.ts` | 쿼리 분류(Haiku) → OpenAI 임베딩 → 하이브리드 검색 → SSE 스트리밍(Haiku) |
| `frontend/app/api/chat/route.ts` | RAG + 대화 히스토리 챗봇, SSE 스트리밍 |
| `frontend/app/api/messages/route.ts` | 사용자 문의 저장 |
| `frontend/app/api/messages/notify/route.ts` | 문의 알림 발송 |

### Admin (ai-service/admin.py)

Streamlit UI. 스팟 목록 조회 (상태/도시 필터), 메모/본문/지역/카테고리/매운맛 편집, 저장, BGE-M3 임베딩 재실행. LLM 호출 없음.

### spots 상태 필드

`status`: `메모필요` → `메모완료` → `업로드완료`

### 마케팅 시스템 (ai-service/marketing/)

SQLite DB (`ai-service/marketing/data/bapmap_marketing.db`): opportunities, drafts, feedback, daily_reports 테이블.
일일 리포트는 `ai-service/marketing/daily_reports/YYYY-MM-DD.md`로 저장.
피드백 기록: `cd ai-service && python -m marketing.feedback <opp_id> <draft_id> <1/0> [reason]`

### 일본어 버전

`frontend/app/ja/` 하위에 별도 라우트. 스팟/가이드 일본어 컬럼: `content_ja`, `title_ja`, `subtitle_ja`, `intro_ja`, `body_ja`. `/spot-publish`, `/guide-publish` 커맨드에서 Claude Code가 직접 번역.

### 영상 파이프라인

`ai-service/branding/video/`: 1080×1920 YouTube Shorts. FFmpeg + edge-tts. 로컬 전용 (OAuth 제약).
`youtube_token.pickle` 최초 1회 브라우저 인증 필요.

## 환경 변수

```
# Python (ai-service/.env)
ANTHROPIC_API_KEY
OPENAI_API_KEY
SUPABASE_URL
SUPABASE_SERVICE_KEY
GOOGLE_PLACES_API_KEY

# Next.js (frontend/.env.local)
ANTHROPIC_API_KEY
OPENAI_API_KEY
NEXT_PUBLIC_SUPABASE_URL
SUPABASE_SERVICE_KEY
NEXT_PUBLIC_MAPBOX_TOKEN
```

## 콘텐츠 톤 규칙

절대 사용 금지: `nestled`, `bustling`, `hidden gem`, `must-try`, `culinary journey`, `food lovers`, `vibrant`, `authentic experience`

한국인이 실제로 가는 로컬 맛집을 외국 관광객에게 소개하는 컨셉. 서울 사는 친구가 카톡으로 귀띔해주는 느낌. 구체적 수치(도보 몇 분, 가격, 영업시간)와 솔직한 단점 포함.

### 품질 평가 기준 (spot-publish / guide-publish 공통)

**하드룰 + 4축 5점 (만점 20, 통과 15)**

- 하드룰: 금지어 / 금지 구조 / 필수 정보 누락 — 하나라도 위반 시 자동 재작성
- 4축: `Specificity / Voice / Usefulness / Findability` (Findability = SEO+GEO 통합)
- 상세 기준은 각 슬래시 커맨드 본문 참조
