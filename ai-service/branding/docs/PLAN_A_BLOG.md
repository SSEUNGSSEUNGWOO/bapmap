# Plan A — bapmap.com 블로그 자동화 파이프라인

> 목표: bapmap.com의 맛집 데이터를 기반으로 2채널 블로그 포스트를 자동 생성 + 퍼블리싱

---

## 1. 타겟 & 채널

| 채널 | 언어 | 역할 | 타겟 |
|------|------|------|------|
| **Medium** | 영어 | 콘텐츠 허브 (SEO, 장기 트래픽) | 외국인 여행객 (K-pop 팬, 음식 여행자) |
| **Reddit** | 영어 | 배포 채널 (단기 바이럴) | r/korea, r/seoul, r/JapanTravel 등 |

| 항목 | 내용 |
|------|------|
| 포스팅 빈도 | Medium 주 3회 / Reddit 포스트마다 공유 |
| 콘텐츠 타입 | 맛집 리뷰, 지역별 가이드, 테마 큐레이션 |

---

## 2. 파이프라인 단계

```
[STEP 1] 트렌드 리서치
    - 구글 트렌드 / Reddit r/Korea / TikTok 인기 검색어
    - 여행 시즌 (벚꽃, 연말, K-pop 콘서트 시즌 등)
    - bapmap 신규 등록 식당

[STEP 2] 주제 선정
    - 트렌드 + bapmap DB 교차 분석
    - 후보 3개 생성 → 점수 평가 (검색량, 경쟁도, 관련성)
    - 최종 1개 선택

[STEP 3] 콘텐츠 생성 (LLM)
    - 식당 데이터 수집 (bapmap 스크래핑 or API)
    - 블로그 포스트 초안 작성 (Claude)
    - SEO 최적화 (제목, 메타설명, 키워드)
    - 이미지 프롬프트 생성 (→ DALL-E / Unsplash API)

[STEP 4] 콘텐츠 평가
    - 가독성 점수 체크
    - SEO 점수 체크
    - 사실 정확성 검증 (bapmap 원본과 대조)
    - 통과 기준 미달 시 → 재생성

[STEP 5] 퍼블리싱
    - Medium API → 영어 포스트 발행
    - Naver 블로그 API → 한국어 포스트 발행
    - 발행 URL + 메타데이터 DB 저장

[STEP 6] 성과 수집 (24시간 후)
    - 조회수, 좋아요, 공유 수집
    - DB 업데이트

[STEP 7] 회고 & 셀프 개선
    - 잘 된 포스트 패턴 분석
    - 프롬프트 자동 업데이트
    - 리포트 생성 → 이메일/메신저 발송
```

---

## 3. 콘텐츠 구조 (2-Layer)

> bapmap의 Spots / Guides 구조를 블로그에 그대로 반영

```
[가이드 포스트] → 트래픽 유입, 바이럴
"강남 고기집 TOP 5"
"서울 야식 맛집 추천"
        ↓ 링크 연결
[스팟 포스트] → SEO 롱테일, 상세 정보
"금돼지식당 완전 가이드"
"불이아 역삼점 솔직 리뷰"
```

---

## 4. 콘텐츠 유형 & 템플릿

### 타입 1: 스팟 포스트 (단일 맛집 딥다이브)
```
제목: "Why [식당명] Is the Most Underrated Restaurant in [지역]"
구성:
  - Hook (현지인 비밀 맛집 스토리)
  - 식당 기본 정보 (위치, 가격, 운영시간)
  - 시그니처 메뉴 설명
  - 가는 방법 (지하철 기준)
  - 주문 팁 (영어 메뉴 유무 등)
  - 관련 가이드 포스트 링크
  - bapmap 링크 CTA
```

### 타입 2: 가이드 포스트 — 테마 큐레이션
```
제목: "5 Best [음식종류] in Korea Only Locals Know"
구성:
  - 왜 이 리스트가 다른지 (광고 없음, 직접 검증)
  - 5개 식당 각 소개 (200자) + 개별 스팟 포스트 링크
  - 지도 임베드 (bapmap 링크)
  - 여행 팁 (시즌, 예약 필요 여부)
```

### 타입 3: 가이드 포스트 — 여행 시즌/지역
```
제목: "Complete Food Guide for [시즌/지역] in Korea"
구성:
  - 시즌/지역 소개
  - 지역별 추천 식당 맵핑 + 스팟 포스트 링크
  - 예산별 옵션 ($, $$, $$$)
  - 실전 여행 일정 (하루 먹방 코스)
```

---

## 4. 기술 스택

| 컴포넌트 | 도구 |
|----------|------|
| 트렌드 리서치 | Google Trends API, Reddit API, SerpAPI |
| 데이터 소스 | bapmap.com 스크래핑 (BeautifulSoup / Playwright) |
| LLM | Claude API (claude-sonnet-4-6) |
| 이미지 | Unsplash API (라이선스 무료) |
| 퍼블리싱 | Medium API, Naver Blog API |
| DB | Supabase (PostgreSQL) |
| 스케줄러 | GitHub Actions (매일 자동 실행) |
| 리포트 | 이메일 (SendGrid) or 카카오 알림톡 |
| 프레임워크 | LangGraph (Phase 2 전환 시) |

---

## 5. 데이터 스키마

### posts 테이블
```sql
id          UUID
title       TEXT
type        ENUM(single_review, list, guide)
restaurant  TEXT[]       -- 포함된 식당명
platform    ENUM(medium, naver)
url         TEXT
published_at TIMESTAMP
views       INT
likes       INT
score       FLOAT        -- 평가 점수
prompt_ver  TEXT         -- 사용된 프롬프트 버전
created_at  TIMESTAMP
```

### restaurants 테이블
```sql
id          UUID
name        TEXT
district    TEXT
rating      FLOAT
price_range TEXT         -- $, $$, $$$
signature   TEXT[]       -- 시그니처 메뉴
subway      TEXT         -- 가장 가까운 지하철역
tags        TEXT[]       -- 테마 태그
bapmap_url  TEXT
last_synced TIMESTAMP
```

---

## 6. Phase별 구현 계획

### Phase 1 — Claude Code 하네스로 워크플로우 검증 (지금)
- [ ] bapmap.com 데이터 수동 수집 (식당 10개)
- [ ] 프롬프트 작성: 블로그 포스트 초안 생성
- [ ] 수동으로 Medium 퍼블리싱 테스트
- [ ] 결과물 평가 & 프롬프트 개선

### Phase 2 — 코드 자동화
- [ ] bapmap 스크래퍼 구현
- [ ] Claude API 연동 파이프라인
- [ ] Supabase DB 연결
- [ ] Medium API 자동 퍼블리싱
- [ ] GitHub Actions 스케줄러

### Phase 3 — LangGraph 전환
- [ ] 각 단계를 LangGraph 노드로 변환
- [ ] 에이전트 오케스트레이터 구성
- [ ] 셀프 개선 루프 구현

---

## 7. 성공 지표 (KPI)

| 지표 | 목표 (1개월) |
|------|-------------|
| 발행 포스트 수 | 12개+ |
| 평균 조회수 | 500+ / 포스트 |
| bapmap 클릭 유입 | 200+ / 월 |
| 자동화율 | 80%+ (사람 개입 최소화) |

---

## 8. 다음 액션 (Phase 1 시작)

1. bapmap.com 식당 10개 데이터 스크래핑
2. 블로그 포스트 프롬프트 v1 작성
3. Claude로 샘플 포스트 3개 생성
4. 품질 평가 후 프롬프트 개선
5. Medium 수동 퍼블리싱 → 반응 확인
