---
description: 가이드에 아직 사용되지 않은 스팟들을 묶어서 가이드 1편을 발행한다
---

# /guide-publish

미사용 스팟을 클러스터링하고 사용자가 선택한 테마로 가이드 1편을 작성/평가/번역해서 Supabase `guides` 테이블에 저장한다.

---

## 1단계 — 미사용 스팟 조회 + 클러스터링

Supabase `spots`에서 `status = '업로드완료'`인 스팟을 모두 조회. 단, 기존 `guides.spot_slugs` 어디에도 들어있지 않은 스팟만.

조회 컬럼: `english_name, name, category, region, city, memo, tagline, content`

**클러스터링 (Claude Code 직접)** — 후보 5개 만들기:
- 각 클러스터는 3~5개 스팟
- 명확한 테마: 지역(예: "성수동"), 음식(예: "한식 곰탕"), 상황(예: "혼밥 가능한 점심집"), K-pop/K-drama 연결 우선
- "좋은 식당" 같은 추상 X, 구체적 테마 O
- 스팟들이 서로 다른 가치를 줘야 함 (중복 X)

각 클러스터를 **25점 만점 (5개 항목 × 5점)** 으로 자체 평가:
- Theme specificity, Spot diversity, K-culture link, Search intent, Local insider value

---

## 2단계 — 사용자에게 후보 5개 제시

각 후보에 대해 보여줄 것:
- 테마명, 점수, 한 줄 추천 사유
- 포함 스팟 (english_name 리스트)

사용자가 1개 선택. 또는 "다시 뽑아줘" / "스팟 직접 지정"도 허용.

---

## 3단계 — 가이드 본문 작성 (Claude Code 직접)

선택된 클러스터 스팟의 풀 데이터(`name, english_name, category, region, memo, what_to_order, tagline, image_url, subway, price_level, rating`)를 컨텍스트로 본문 작성.

**스팟 수**: 표준은 **4개** (운영 가이드 전부 4개). 3개나 5개도 가능하지만 4개가 기본.

**출력 JSON**:
```json
{
  "slug": "url-friendly-slug",
  "title": "30-75자, 후크가 있는 제목 (SEO+GEO 키워드 포함)",
  "subtitle": "60-160자, 가이드의 구체적 핵심을 한 줄에 요약",
  "category_tag": "Korean BBQ, K-pop, Late Night (1~3개, 쉼표+공백 구분)",
  "intro": "100-500자, 1~3문단. 왜 이 가이드인지, 스팟들이 묶이는 이유, 살짝 자극적인 후크",
  "body": "마크다운 본문, [spot:English Name] 마커 + 그 아래 한 단락(150-250자) per spot"
}
```

**본문 길이 가이드 (실제 운영 평균)**:
- body: 영문 **2,000~3,500자** (1,400자 미만은 빈약, 3,500자 초과는 산만)
- body_ja: 일본어 **800~1,800자**

**본문 구조** (실제 발행 패턴):
```
[spot:Name1]

[150~250자, 자연스러운 한 단락]
- 첫 줄: 왜 이 동네에서 이곳인지 (특이점/배경)
- 메뉴 + 가격 (한글 병기 가능)
- 솔직한 단점 또는 운영 팁 1개

[spot:Name2]
... (반복)

[spot:Name4]

[마지막 단락은 outro 역할 — 별도 헤더 없이 운영 팁 자연스럽게 녹임]
```

**톤 규칙**:
- 서울 사는 친구가 카톡으로 귀띔하는 톤
- "Itaewon Is Over", "Where Locals Actually Eat" 같은 강한 후크 환영
- 한국인이 실제로 가는 로컬 맛집을 외국 관광객에게 소개하는 컨셉
- 단점은 솔직하지만 비난조 X ("the wait regularly hits 2 hours" 식)

**금지어/구조**: spot-publish 와 동일 (`hidden gem`, `must-try`, FAQ 박스, "Whether you're..." 등). 단 가이드 본문은 자연스러운 산문이라 "in the best and most literal sense" 같은 미묘한 변형은 컨텍스트 보고 판단 (직접 금지어 매칭만 hard rule).

---

## 4단계 — 품질 평가 (하드룰 + 4축 5점)

### 하드룰 — 하나라도 위반하면 즉시 재작성

- [ ] **금지어 0개** (정확 매칭만 hard rule): `nestled`, `bustling`, `hidden gem`, `must-try`, `culinary journey`, `food lovers`, `vibrant`, `authentic experience`, `in the best way`, `rounds things out`, `doesn't disappoint`
- [ ] **금지 구조 0개**: FAQ 박스 / "Whether you're..." 시작 / 일반장려문 ("You won't regret it" 등)
- [ ] 각 `[spot:Name]` 아래 한 단락(150자+)에 왜/뭘 시키는지/가격/단점 중 ≥3개 포함
- [ ] 마지막 단락 또는 마지막 spot 단락에 실무 팁 (예약 / 시간대 / 동선 / 매진 중 ≥1개)
- [ ] 스팟 간 차이가 본문에서 명확 (같은 톤의 추천 반복 X)
- [ ] Title 길이 30~75자
- [ ] body 길이 1,400자 이상

### 4축 5점 채점 — 만점 20, 통과 15

점수 의미: `1=실패, 2=약함, 3=보통, 4=좋음, 5=훌륭`

| 축 | 본다 |
|---|---|
| Specificity | 스팟별 메뉴/가격/차이가 충분히 구체적인가 |
| Voice | 친구가 카톡하는 톤, AI 티 안 나는가 |
| Usefulness | 여행자가 실제 동선 짤 수 있는가 |
| Findability | 제목+heading이 검색 의도와 맞고, ChatGPT/Perplexity가 인용할만한가 (SEO+GEO 통합) |

### 처리

- 하드룰 위반 → 위반 항목 명시해서 재작성 (최대 2회)
- 4축 합 < 15 → 가장 낮은 1~2개 축 피드백을 반영해 재작성 (최대 2회)
- 그래도 통과 못 하면 사용자에게 보고하고 결정 받기

---

## 5단계 — 일본어 번역 (Claude Code 직접)

`title → title_ja`, `subtitle → subtitle_ja`, `intro → intro_ja`, `body → body_ja`.

**규칙**:
- 마크다운 형식 유지
- `[spot:English Name]` 마커 그대로 유지
- 식당명은 로마자 그대로
- 자연스러운 일본어, 직역 X

---

## 6단계 — 사용자 검수 + Supabase 저장

영문/일본어 본문을 사용자에게 보여주고 컨펌. cover_image URL도 사용자한테 받기 (Unsplash/Pexels 등 직접 링크).

OK면 `guides` 테이블 UPSERT:

```
slug, title, subtitle, cover_image, category_tag, intro, body, spot_slugs (english_name 배열),
title_ja, subtitle_ja, intro_ja, body_ja,
status = 'draft'
```

저장 후 사용자에게 published로 바꿀지 물어보고 OK면 status 업데이트.

---

## 7단계 — OpenAI 임베딩 (검색용)

가이드 저장 후 임베딩 생성. `search_guides` RPC가 frontend `/api/search`, `/api/chat`에서 호출되므로 필수.

```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
.venv/bin/python -m pipeline.rag.embed_guides --slugs <new-slug>
```

`title + subtitle + category_tag + intro + body` 합쳐서 OpenAI `text-embedding-3-small` (1536d) → `guides.embedding` 저장.

### 모드 정리

| 명령 | 동작 |
|---|---|
| (인자 없음) | embedding이 null인 가이드만 (incremental) |
| `--slugs slug1,slug2` | 지정 가이드만 재임베딩 |
| `--rebuild-all` | 모든 가이드 재임베딩 (덮어쓰기, 안전 — 컬럼 update만이라 데이터 유실 위험 없음) |

draft 상태도 임베딩은 생성 (RPC가 `status='published'`로 필터). 추후 published로 바꿀 때 별도 임베딩 불필요.

---

## 마무리 보고

- 가이드 slug, 테마, 포함 스팟 수
- 평가 점수 (재작성 횟수)
- Supabase 저장 status (draft / published)
- 임베딩 생성 여부
- frontend URL: `https://bapmap.com/guides/{slug}` 와 일본어판 `/ja/guides/{slug}`
