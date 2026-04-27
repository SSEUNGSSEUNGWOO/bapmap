---
description: Blue Ribbon에서 신규 스팟 N개를 발굴하고 블로그 포스팅까지 발행한다 (기본 5개)
argument-hint: "[N]"
---

# /spot-publish

신규 스팟을 발굴하고 블로그 포스팅을 발행한다. 인자가 없으면 5개, 있으면 그 숫자만큼 처리한다.

인자: `$ARGUMENTS` (없으면 `5`로 간주)

> ⚠️ Python 실행은 모두 `ai-service/.venv/bin/python` 사용 (uv venv). 시스템 파이썬으로 실행 금지.

---

## 1단계 — 스팟 발굴 + Supabase 저장

```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
.venv/bin/python -m branding.blog.fetch_new_spots --max-spots <N>
```

- `branding/blog/agents/discover.py`: Blue Ribbon 크롤링 (쿠키 필요, selenium 사용)
- `branding/blog/agents/ingest.py`: Google Places API → 체인/비음식점 필터링 → Supabase `spots` INSERT (status="업로드완료")
- 출력: 신규 spot id 리스트

**쿠키 만료 시**: `.venv/bin/python branding/blog/login.py` 로 갱신.

**영문명 자동 음역 주의**: Google Places가 한글 displayName을 반환하면 unidecode로 음역하는데 자연스럽지 않은 경우가 많음 (예: "물고기(2호점)" → `mulgogijutaeg2hojeom`). 발굴 후 `english_name`을 사람이 읽을 수 있는 형태로 수동 수정 권장 (예: `Mulgogi (Yongsan Branch)`).

신규 스팟이 0개면 즉시 종료하고 사용자에게 보고.

---

## 2단계 — 가격/메뉴/지하철 검증 (필수)

Google Places가 주는 정보는 부족하다 (가격 없음, 지하철 거리 모호). 본문 작성 전에 **각 스팟마다** 다이닝코드/네이버/식신 등에서 다음을 검증:

- 시그니처 메뉴 2~4개 + **정확한 가격** (₩ 단위)
- 가까운 지하철역 + 도보 시간 (Google이 1km 내 못 찾으면 택시 거리로)
- 영업시간 (Google `hours`가 비어있으면 다이닝코드에서)
- 휴무일

검증 못 하면 사용자에게 "가격 정보 부족 — A) 추정 / B) 검색 / C) 가격대만"으로 결정 받기.

---

## 3단계 — 포스팅 본문 작성 (Claude Code 직접)

각 신규 스팟에 대해 Supabase에서 다음 컬럼을 조회: `name, english_name, category, city, region, lat, lng, rating, rating_count, price_level, hours, subway, google_maps_url, google_reviews, reservable, good_for_groups, vegetarian, spice_level`.

스팟 1개당 영문 마크다운 **3,500~4,500자**. 다음 구조 엄수:

```markdown
# H1: 50~70자, 식당의 본질을 한 줄로 (SEO+GEO 키워드 포함)

[오프닝 2~3문단]
- 동네/문화 컨텍스트
- 이 가게가 왜 다른가
- 한국인이 친구한테 카톡으로 귀띔하는 톤

---

## What to Expect

[2~4문단]
- 시그니처 메뉴의 디테일 (맛, 식재료, 조리법)
- 음식 외 경험 (분위기, 서비스, 운영 특징)
- 솔직한 단점 1~2개 자연스럽게 녹이기
- 리뷰 인용 가능 ("reviewers say...", "locals describe...")

---

## What to Order

**Menu 1 (한글 병기, ₩가격)** — 한 줄 설명, 왜 이걸 시켜야 하는지.
**Menu 2 (한글 병기, ₩가격)** — 한 줄 설명.
**Menu 3 (한글 병기, ₩가격)** — 한 줄 설명.

(2~4개. 가격 검증 못 한 메뉴는 빼는 것이 낫다.)

---

## Atmosphere & Vibe

[1~2문단]
- 어떤 사람/상황에 맞는지 (데이트/단체/혼밥/늦은시간 등)
- 동네/주변과의 연결
- 분위기 (조용함/시끄러움/모던/로컬 등)

---

## Practical Info

- **Address:** [구/동]
- **Google Maps:** [URL]
- **Nearest subway:** [역, 도보 X분 또는 택시 X분]
- **Hours:** [요일별 또는 통합]
- **Price range:** [Budget / Mid-range / Upscale / Luxury 또는 ₩숫자~숫자]
- **Spice Level:** [Mild / Medium / Spicy]
- **Vegetarian:** [Yes / No / Partial]
- **Halal-friendly:** [Yes / No / Partial]
- **Reservations:** [Required / Recommended / Walk-in OK / Not accepted]
- **Good for groups:** [Yes / Yes (small groups) / No]

[운영 팁 1줄: 동선 가이드, 예약 우회, 주차 등]

---

## Summary

| | |
|---|---|
| **Best for** | [용도 키워드 3~4개]
| **Location** | [구/동, 시]
| **Subway** | [역, 도보 X분]
| **Hours** | [짧게]
| **Reservations** | [한 단어]
| **Rating** | ★[평점] ([리뷰수])
```

### 톤 가이드 (참고: TWG, Sunbaek Hoegwan)
- 정보 + 이야기 결합. 단순 나열 X.
- 동네 컨텍스트 깊게 (TWG의 "Seongsu's design district", Sunbaek의 "Yangcheon-gu doesn't make it onto most Seoul itineraries").
- 시적 표현 1~2개 OK (TWG의 "lighting that makes afternoon feel like it has permission to stretch").
- 단점은 솔직하지만 비난조 X (TWG의 "pasta portions come in smaller than expected").

---

## 4단계 — 품질 평가 (하드룰 + 4축 5점)

### 하드룰 — 하나라도 위반하면 즉시 재작성

- [ ] **금지어 0개**: `nestled`, `bustling`, `hidden gem`, `must-try`, `culinary journey`, `food lovers`, `vibrant`, `authentic experience`, `in the best way`, `rounds things out`, `doesn't disappoint`
- [ ] **금지 구조 0개**: FAQ 박스 / "Whether you're..." 시작 / 일반장려문 ("You won't regret it", "Don't miss it" 등)
  - ✅ Summary 테이블은 정식 형식 (필수)
- [ ] 시그니처 메뉴 ≥ 2개 + 가격 명시
- [ ] 도보 시간 또는 지하철 출구 정보 명시 (먼 경우 택시 거리)
- [ ] 솔직한 단점 1개 이상
- [ ] H1 길이 50~70자
- [ ] 본문 3,500자 이상

### 4축 5점 채점 — 만점 20, 통과 15

점수 의미: `1=실패, 2=약함, 3=보통, 4=좋음, 5=훌륭`

| 축 | 본다 |
|---|---|
| Specificity | 메뉴/가격/시간/위치 디테일이 두루뭉술하지 않은가 |
| Voice | 친구가 카톡하는 톤, AI 티 안 나는가 |
| Usefulness | 여행자가 실제 판단/동선에 쓸 수 있는 정보인가 |
| Findability | 제목+heading이 검색 의도와 맞고, ChatGPT/Perplexity가 인용할만한가 (SEO+GEO 통합) |

### 처리

- 하드룰 위반 → 위반 항목 명시해서 재작성 (최대 2회)
- 4축 합 < 15 → 가장 낮은 1~2개 축 피드백을 반영해 재작성 (최대 2회)
- 그래도 통과 못 하면 사용자에게 보고하고 결정 받기

---

## 5단계 — 부가 컬럼 작성

본문과 함께 다음 컬럼도 채운다:

- `what_to_order`: list[str] — 형식: `"Menu (한글) — 한 줄 설명"`. 보통 2~4개.
- `what_to_order_ja`: list[str] — 위의 일본어 버전. 식당/메뉴 영문/한글 그대로 유지.
- `good_for`: list[str] — 짧은 태그. 예: `["Date night", "Solo dining", "Groups", "Late night", "Budget-friendly", "Special occasion", "Reservation recommended", "No reservations needed"]`.
- `tagline`: str — 한 줄로 식당 본질 (영문). 예: `"Singapore's luxury tea brand inside Seongsu Naknak — come for the 1837 Black Tea, not the pasta."`

---

## 6단계 — 일본어 번역 (Claude Code 직접)

통과한 영문 포스팅을 일본어로 번역. 본문 길이도 영문과 비슷하게 (3,000자 이상).

**규칙**:
- 마크다운 형식 + 섹션 구조 그대로 유지
- 식당명은 영문(또는 영문+한글) 그대로 (ex: `TWG Tea Salon`, `Sunbaek Hoegwan（순백회관）`)
- 한국어 메뉴명/지명: 한글 + 일본어 또는 한자 병기 (ex: `聖水（ソンス）`, `梧木橋駅（オモッキョ）`, `순백정식（純白定食）`)
- `[spot:English Name]` 마커가 있으면 그대로 유지
- 일본 독자 시점: 한국 음식/문화 익숙하지 않다고 가정하고 살짝 더 친절히

---

## 7단계 — 검수 + Supabase 저장

각 스팟에 대해 영문/일본어 본문을 사용자에게 보여주고 컨펌 받기. OK면 Supabase `spots` UPDATE:

```
content, content_ja, what_to_order, what_to_order_ja, good_for, tagline, hours, subway
```

⚠️ `title` 컬럼은 spots 테이블에 **없음**. H1은 `content` 안에 포함.

---

## 8단계 — BGE-M3 임베딩

### 사전 체크 (안전을 위해)

```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
.venv/bin/python -c "import sentence_transformers; print('OK')"
```

미설치 시: `uv pip install sentence-transformers`

### 실행 — 신규 발행 스팟만 (권장)

```bash
.venv/bin/python -m pipeline.rag.embed_v2 --spot-ids <id1>,<id2>,<id3>
```

각 spot_id에 대해 delete-then-insert 방식이라 기존 임베딩은 유지된다. 안전.

### 모드 정리

| 명령 | 동작 |
|---|---|
| (인자 없음) | spot_chunks에 누락된 spots만 임베딩 (incremental) |
| `--spot-ids id1,id2,...` | 지정 spots만 재임베딩 |
| `--rebuild-all` | ⚠️ 전체 삭제 후 전체 재임베딩 (백업 권장) |

`--rebuild-all`은 본문 톤/구조를 일괄 변경한 후처럼 명시적으로 전체 재구축이 필요할 때만 사용.

---

## 마무리 보고

- 발굴된 신규 스팟 수
- 발행 완료 스팟 수 (영문 + 일본어 + 부가 컬럼)
- 평가 미달로 빠진 스팟 (있으면 사유)
- 임베딩된 chunk 수
- 사이드 변경사항 (영문명 수정, hours/subway 보충, requirements.txt 등)
