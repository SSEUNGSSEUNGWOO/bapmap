# Plan C — bapmap.com 쇼츠/릴스/틱톡 영상 자동화 파이프라인

> 목표: bapmap.com 맛집 데이터를 기반으로 세로형 숏폼 영상 콘텐츠를 자동 생성 + 멀티 플랫폼 퍼블리싱

---

## 1. 타겟 & 채널

| 채널 | 타겟 | 언어 | 형식 |
|------|------|------|------|
| **YouTube Shorts** | 외국인 여행객, K-pop 팬 | 영어 | 세로형 60초 이내 |
| **Instagram Reels** | 외국인 + 한국인 | 영어/한국어 | 세로형 30~90초 |
| **TikTok** | 10~30대 외국인 | 영어 | 세로형 15~60초 |

---

## 2. 영상 콘텐츠 유형

### 타입 1: 맛집 단일 소개 (가장 기본)
```
"POV: You found the best [음식] in Korea 🇰🇷"
구성:
  - 훅 (0~3초): 충격적인 음식 비주얼 or 반전 멘트
  - 식당 소개 (3~15초): 이름, 위치, 분위기
  - 시그니처 메뉴 (15~40초): 메뉴 설명 + 가격
  - 팁 (40~55초): 주문법, 가는 법, 웨이팅 여부
  - CTA (55~60초): "Full guide at bapmap.com"
```

### 타입 2: 지역 맛집 Top 3~5
```
"Top 5 restaurants in [지역] that locals actually go to"
구성:
  - 훅: "Skip the tourist traps"
  - 식당 5개 빠르게 소개 (각 10초)
  - 공통 팁 (예약, 가격대)
  - CTA: bapmap 지도 링크
```

### 타입 3: 테마/시즌 큐레이션
```
"Best food spots for [벚꽃시즌/야간/혼밥] in Korea"
구성:
  - 시즌/테마 배경 설명 (5초)
  - 장소 3개 소개
  - 분위기 강조 (BGM, 자막)
  - CTA
```

### 타입 4: 바이럴 쇼츠 재편집 (실전 전략)
```
- 이미 바이럴 된 한국 음식 영상 분석
- 같은 포맷으로 bapmap 식당 버전 제작
- 트렌딩 BGM + 자막 스타일 적용
```

---

## 3. 파이프라인 단계

```
[STEP 1] 트렌드 리서치
    - TikTok 트렌딩 해시태그 (#koreanfood, #seoultravel 등)
    - YouTube Shorts 인기 한국 음식 영상 분석
    - 시즌 이벤트 (벚꽃, 연말, K-pop 콘서트)

[STEP 2] 영상 주제 선정
    - 트렌드 + bapmap DB 매칭
    - 콘텐츠 타입 결정 (단일/리스트/테마/재편집)

[STEP 3] 스크립트 생성 (LLM)
    - 훅 문구 3가지 생성 → 최적안 선택
    - 자막 스크립트 작성 (영어)
    - 해시태그 세트 생성

[STEP 4] 영상 소스 수집
    - bapmap 식당 이미지 수집
    - Unsplash / Pexels API (라이선스 무료 영상)
    - 이미지 슬라이드쇼 or 기존 바이럴 영상 레퍼런스

[STEP 5] 영상 자동 편집
    - 이미지 → 슬라이드쇼 영상 생성 (MoviePy / Remotion)
    - 자막 오버레이 자동 삽입
    - BGM 추가 (저작권 무료 트랙)
    - 세로형 (9:16) 렌더링

[STEP 6] 콘텐츠 평가
    - 훅 강도 체크 (3초 이내 임팩트)
    - 자막 가독성 체크
    - CTA 포함 여부 확인

[STEP 7] 멀티플랫폼 퍼블리싱
    - YouTube Shorts API
    - Instagram Graph API (Reels)
    - TikTok API
    - 캡션, 해시태그, 썸네일 자동 설정

[STEP 8] 성과 수집 & 개선
    - 조회수, 좋아요, 공유, 팔로워 증가 추적
    - 잘 된 영상 패턴 분석 → 스크립트 프롬프트 개선
```

---

## 4. 기술 스택

| 컴포넌트 | 도구 |
|----------|------|
| 트렌드 리서치 | TikTok API, YouTube Data API |
| 스크립트 생성 | Claude API (claude-sonnet-4-6) |
| 이미지 소스 | Unsplash API, Pexels API, bapmap 스크래핑 |
| 영상 편집 | MoviePy (Python) or Remotion (JS) |
| 자막 생성 | 자동 자막 오버레이 |
| BGM | YouTube Audio Library, Pixabay Music API |
| 퍼블리싱 | YouTube Data API, Instagram Graph API, TikTok API |
| DB | Supabase (Plan A와 공유) |
| 스케줄러 | GitHub Actions |

---

## 5. 데이터 스키마

### videos 테이블
```sql
id           UUID
title        TEXT
type         ENUM(single, list, theme, reformat)
restaurant   TEXT[]
script       TEXT
platform     TEXT[]        -- youtube, instagram, tiktok
url          TEXT[]
published_at TIMESTAMP
views        INT
likes        INT
shares       INT
hook_score   FLOAT
prompt_ver   TEXT
created_at   TIMESTAMP
```

---

## 6. Phase별 구현 계획

### Phase 1 — 수동 워크플로우 검증
- [ ] 바이럴 한국 음식 쇼츠 5개 분석 (훅 패턴 파악)
- [ ] bapmap 식당 1개로 스크립트 수동 작성
- [ ] 이미지 슬라이드쇼 수동 편집 (CapCut or 직접)
- [ ] TikTok / Reels 수동 업로드 → 반응 확인

### Phase 2 — 자동화 구현
- [ ] MoviePy로 이미지 슬라이드쇼 자동 생성
- [ ] Claude API 스크립트 생성 파이프라인
- [ ] 멀티플랫폼 API 연동
- [ ] GitHub Actions 스케줄러

### Phase 3 — LangGraph 전환
- [ ] 각 단계 LangGraph 노드화
- [ ] 영상 품질 자동 평가 에이전트
- [ ] A/B 테스트 훅 문구 자동화

---

## 7. 성공 지표 (KPI)

| 지표 | 목표 (1개월) |
|------|-------------|
| 발행 영상 수 | 12개+ (채널당 4개) |
| 평균 조회수 | 1,000+ / 영상 |
| 팔로워 증가 | 500+ |
| bapmap 클릭 유입 | 300+ / 월 |
| 자동화율 | 70%+ |
