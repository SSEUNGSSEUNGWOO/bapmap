---
description: Blue Ribbon에서 신규 스팟 N개를 발굴하고 블로그 포스팅까지 발행한다 (기본 5개)
argument-hint: "[N]"
---

# /spot-publish

신규 스팟을 발굴하고 블로그 포스팅을 발행한다. 인자가 없으면 5개, 있으면 그 숫자만큼 처리한다.

인자: `$ARGUMENTS` (없으면 `5`로 간주)

---

## 1단계 — 스팟 발굴 + Supabase 저장

```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
python -m branding.blog.fetch_new_spots --max-spots <N>
```

- `branding/blog/agents/discover.py`: Blue Ribbon 크롤링 (쿠키 필요)
- `branding/blog/agents/ingest.py`: Google Places API → 체인/비음식점 필터링 → Supabase `spots` INSERT (status="업로드완료")
- 출력: 신규 spot id 리스트

**쿠키 만료 시**: `.venv/bin/python branding/blog/login.py` 로 갱신.

신규 스팟이 0개면 즉시 종료하고 사용자에게 보고.

---

## 2단계 — 포스팅 본문 작성 (Claude Code 직접)

각 신규 스팟에 대해 Supabase에서 다음 컬럼을 조회: `name, english_name, category, city, region, lat, lng, rating, rating_count, price_level, hours, subway, google_maps_url, image_url, google_reviews, reservable, good_for_groups`.

스팟 1개당 영문 마크다운 500~700자. 구조:

1. **H1**: 50~60자, SEO 검색어 타겟 (예: "Korean BBQ in Gangnam")
2. **오프닝 1~2문장**: 이 가게가 왜 특별한지, 친구가 카톡하는 톤
3. **메뉴 + 가격**: 시그니처 2~3개, 한글/영문 병기, 가격 명시
4. **솔직한 단점**: 대기, 좁음, 매움 등 1~2개
5. **로지스틱**: 도보 시간 (지하철 출구 기준), 영업시간, 예약/카드 여부
6. **마무리 링크**: `[See on Bapmap](https://bapmap.com/spots/{english_name을-slug화})`

**금지어**: `nestled`, `bustling`, `hidden gem`, `must-try`, `culinary journey`, `food lovers`, `vibrant`, `authentic experience`, `in the best way`, `rounds things out`, `doesn't disappoint`.

**금지 구조**: FAQ 박스, Quick Facts 테이블, "Whether you're..." 시작, 일반적 장려문.

---

## 3단계 — 품질 평가 (하드룰 + 4축 5점)

### 하드룰 — 하나라도 위반하면 즉시 재작성

- [ ] **금지어 0개**: `nestled`, `bustling`, `hidden gem`, `must-try`, `culinary journey`, `food lovers`, `vibrant`, `authentic experience`, `in the best way`, `rounds things out`, `doesn't disappoint`
- [ ] **금지 구조 0개**: FAQ 박스 / Quick Facts 테이블 / "Whether you're..." 시작 / 일반장려문 ("You won't regret it", "Don't miss it" 등)
- [ ] 시그니처 메뉴 ≥ 1개 + 가격 명시
- [ ] 도보 시간 또는 지하철 출구 정보 명시
- [ ] 솔직한 단점 1개 이상 (대기/좁음/매움/조용함 부족 등)
- [ ] H1 길이 50~60자

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

## 4단계 — 일본어 번역 (Claude Code 직접)

통과한 포스팅을 일본어로 번역:
- `content` → `content_ja`
- `title` → `title_ja`
- `what_to_order` 컬럼이 있으면 → `what_to_order_ja`

**규칙**:
- 마크다운 형식 유지
- 식당명은 로마자 그대로 (ex: "Menya Konoha")
- `[spot:English Name]` 마커가 있으면 그대로 유지

---

## 5단계 — 검수 + Supabase 저장

각 스팟에 대해 영문/일본어 본문을 사용자에게 보여주고 컨펌 받기. OK면 Supabase `spots` UPDATE:

```
content, title, content_ja, title_ja
```

---

## 6단계 — BGE-M3 임베딩

저장 완료된 스팟에 대해:

```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
python -m pipeline.rag.embed_v2 --cap 512
```

`spot_chunks` 테이블에 BGE-M3 임베딩 저장.

---

## 마무리 보고

- 발굴된 신규 스팟 수
- 발행 완료 스팟 수 (영문 + 일본어)
- 평가 미달로 빠진 스팟 (있으면 사유)
- 임베딩된 chunk 수
