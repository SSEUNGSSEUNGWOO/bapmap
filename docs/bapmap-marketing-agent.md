# Bapmap 마케팅 에이전트 시스템

## 프로젝트 개요

Bapmap(영어권 관광객 대상 한국 식당 큐레이션 사이트, bapmap.com)의 1인 마케팅을 멀티 에이전트로 운영하는 시스템. Claude Code 기반으로 동작하며, 자동 봇이 아닌 **운영자가 하루 1회 직접 실행하는 Human-in-the-loop** 구조.

### 배경

- Bapmap은 출시 이후 마케팅이 거의 진행되지 않아 트래픽 일 10명 이하
- 1인 운영 한계로 마케팅 시간 확보 어려움
- Reddit/인스타 자동 포스팅은 정책상 불가, 계정 정지 위험
- 단순 카피 생성기가 아닌 발굴/분석/초안/검토가 협업하는 시스템 필요

### 핵심 원칙

1. **Human-in-the-loop**: AI는 발굴/분석/초안만, 실행은 운영자
2. **Claude Code 전용**: API 종량제 사용 안 함, Max 구독 한도 내에서 운영
3. **단일 사용자**: 멀티 사용자 서비스가 아님, 운영자 본인만 사용
4. **MVP 우선**: Phase 1을 3-4일 내 출시, 단계적 확장
5. **학습 루프**: 운영자의 채택/거절 피드백을 다음 실행 시 반영

### Agent Factory와의 관계

- Agent Factory는 코딩/개발 작업용 에이전트 시스템으로 그대로 유지
- 본 프로젝트는 별개의 신규 시스템으로, 마케팅 도메인 전용 페르소나 보유
- Agent Factory의 오케스트레이션 패턴(서브 에이전트 호출, Critic 게이팅, 무한 재시도 루프)에서 영감을 받되, 독립 코드베이스로 구축

---

## 시스템 아키텍처

```
운영자: claude 실행 → "오늘 일일 브리핑 시작"
   ↓
[Scout] 발굴 에이전트
- Reddit 신규 글 크롤링 (PRAW)
- 키워드 매칭 1차 필터
- Bapmap 타겟 적합도 점수화
   ↓
[Analyst] 분석 에이전트
- GA 어제 데이터 수집
- 광고 ROAS, 이탈 패턴, 검색어 분석
- 콘텐츠 성과 패턴 추출
   ↓
[Writer] 작가 에이전트
- 발굴된 후보별 댓글 초안 작성
- 카드뉴스 카피 초안
- 톤 가이드 준수
   ↓
[Reviewer] 검토자 에이전트
- 광고 티 안 나는지 체크
- 톤/문체 일관성 검사
- Bapmap 브랜드 가이드 위반 여부
   ↓
[PM] 디렉터 에이전트
- 모든 결과물 종합
- 우선순위 정리
- 일일 리포트 마크다운 생성
   ↓
운영자: 리포트 검토 → 직접 Reddit/인스타에 실행
   ↓
운영자 피드백 → DB 저장 → 다음 실행 시 학습 데이터로 활용
```

---

## 에이전트 구성

### 1. Scout (발굴 에이전트)

**역할**: 외부 채널에서 Bapmap 추천 기회 발견

**입력**:
- 모니터링 대상 (Phase 1): r/koreatravel, r/seoul, r/Korea
- 마지막 실행 이후 신규 글
- 필터링 키워드: "where to eat", "restaurant", "first time", "vegetarian", "halal", "no English menu", "recommendation"

**처리 단계**:
1. PRAW로 신규 글 가져오기 (코드, LLM 호출 X)
2. 키워드 사전 필터링 (코드)
3. 통과한 글에 대해 LLM 분석:
   - OP 페르소나 (어디서 왔는지, 여행 일정, 제약사항)
   - Bapmap 타겟 적합도 1-10점
   - 추천 이유 / 주의점

**출력**: 점수 7점 이상 후보 글 리스트

---

### 2. Analyst (분석 에이전트)

**역할**: GA + 광고 + 콘텐츠 성과 분석

**입력**:
- GA Data API에서 어제 데이터
- (Phase 2 추가) 구글 광고 데이터
- 어제까지의 콘텐츠 성과 누적 DB

**처리 단계**:
1. GA 핵심 지표 자동 수집 (코드)
2. 어제 vs 그제 vs 지난 7일 평균 비교 (코드)
3. LLM으로 인사이트 추출:
   - 이상 패턴 감지
   - 검색어 트렌드 변화
   - 콘텐츠 우선순위 제안

**출력**: 일일 데이터 요약 + 액션 가능한 인사이트 3개

---

### 3. Writer (작가 에이전트)

**역할**: 댓글, 카피, 블로그 초안 작성

**시스템 프롬프트 핵심**:
- Bapmap 브랜드 가이드 (톤: 친근하지만 정보 위주, 컬러 #E8760A 일관성)
- 광고 티 NO ("built a small site" 정도로 가볍게 언급)
- 다른 식당/정보 추천 먼저, Bapmap은 자연스럽게 끝에
- 1인칭 톤 (직접 가본 듯한 경험 기반)
- 영어 작성 (Reddit/인스타) + 한국어 작성 (블로그) 분리

**입력**: Scout가 발굴한 후보 글 (글 내용, OP 페르소나)

**출력**: 후보별 댓글 초안 (영어, 100-200 단어)

---

### 4. Reviewer (검토자 에이전트)

**역할**: Writer 결과물 품질 게이팅

**검사 항목**:
- 광고 톤 점수 (1-10, 7 이상이면 자연스러움)
- 브랜드 가이드 위반 여부
- 사실 정확성 (실제 식당 정보, 메뉴 정보)
- Reddit 서브레딧별 룰 준수 (자기홍보 금지 룰 등)

**출력**:
- 통과: PM에게 전달
- 거절: 거절 사유 + Writer에게 재작성 요청 (최대 2회 재시도)

---

### 5. PM (디렉터 에이전트)

**역할**: 모든 에이전트 출력 종합, 일일 리포트 생성

**입력**: Scout/Analyst/Writer/Reviewer 결과 전체

**출력 포맷**: `daily_reports/YYYY-MM-DD.md`

```markdown
# Bapmap 일일 마케팅 리포트 (YYYY-MM-DD)

## 어제 성과
- 방문자: N명 (+/-X vs 그제)
- TOP 검색어: "..." (N회)
- 광고 ROAS: X% (예산 Y원 사용)

## 인사이트 3
1. ...
2. ...
3. ...

## 오늘 실행 작업 (우선순위순)

### 1. Reddit 댓글 (점수 X/10)
**글 링크**: https://...
**OP 페르소나**: 호주 30대 첫 방문, 매운 음식 못 먹음
**댓글 초안**:
> ...

**왜 추천**: ...
**주의**: ...

### 2. (다음 작업)
...

## 오늘 콘텐츠 제안
- 카드뉴스: "..." (어제 검색어 반영)
- 블로그 주제: "..."

## 피드백 요청
- 어제 작성한 댓글 채택했는지 [Y/N]
- 거절했다면 사유 (학습용)
```

---

## Phase 1: MVP (3-4일)

### Day 1: 인프라 + Scout

- [ ] 프로젝트 디렉토리 생성: `bapmap-marketing/`
- [ ] Python 3.11 가상환경 + 의존성 (`praw`, `google-analytics-data`, `python-dotenv`, `sqlite3`)
- [ ] `.env`: Reddit API 키, GA 서비스 계정 키
- [ ] SQLite DB 초기화: `opportunities`, `drafts`, `feedback`, `daily_reports` 테이블
- [ ] `scout/reddit_fetch.py`: 신규 글 크롤링 + 키워드 필터링
- [ ] `scout/scorer.py`: LLM 호출로 적합도 점수화 (서브 에이전트 호출)

### Day 2: Analyst + Writer

- [ ] `analyst/ga_fetch.py`: GA Data API 어제 지표 수집
- [ ] `analyst/insights.py`: LLM으로 인사이트 추출
- [ ] `writer/draft.py`: 후보 글 → 댓글 초안 (시스템 프롬프트 분리)
- [ ] 시스템 프롬프트 파일: `prompts/writer_system.md` (브랜드 가이드 포함)

### Day 3: Reviewer + PM + 통합

- [ ] `reviewer/check.py`: 댓글 초안 품질 게이팅, 재시도 루프
- [ ] `pm/orchestrator.py`: 메인 실행 진입점, 모든 에이전트 순차 호출
- [ ] `pm/report.py`: 결과 종합 → 마크다운 리포트 생성
- [ ] `claude` 명령어로 실행 가능하게 CLI 진입점 정리

### Day 4: 운영 + 디버깅

- [ ] 실제 운영 시작 (1회 dry run)
- [ ] 노이즈 후보 필터링 강화
- [ ] 시스템 프롬프트 톤 조정
- [ ] README 작성

---

## Phase 2 (1-2주차)

- 광고 분석 고도화: Scout 발굴 키워드 → 광고 타겟팅 자동 제안
- SEO 블로그 주제 발굴 (Google Trends + AnswerThePublic 연동, 주 1회)
- 채택/거절 피드백 기반 Writer 톤 학습 (few-shot 예시 자동 갱신)

## Phase 3 (3-4주차)

- 인스타 카드뉴스 큐레이터 (오늘 어떤 식당 소개 + 카피 초안)
- 다른 채널 추가: Quora, TripAdvisor 한국 포럼
- A/B 테스트 자동 제안

## Phase 4 (필요 시)

- 호텔/에어비앤비 영문 후기 크롤링 → 페인포인트 분석
- 일본/중국 시장 확장 시 다국어 Scout

---

## 기술 스택

- **언어**: Python 3.11+
- **LLM**: Claude Code (Max 구독 한도 내, API 별도 사용 X)
- **Reddit**: PRAW
- **GA**: Google Analytics Data API v1
- **DB**: SQLite (로컬), 추후 Supabase 마이그레이션 검토
- **실행 환경**: 로컬 PC, `claude` CLI

### 디렉토리 구조 (제안)

```
bapmap-marketing/
├── README.md
├── .env.example
├── pyproject.toml
├── prompts/
│   ├── scout_system.md
│   ├── analyst_system.md
│   ├── writer_system.md
│   ├── reviewer_system.md
│   └── pm_system.md
├── scout/
│   ├── reddit_fetch.py
│   └── scorer.py
├── analyst/
│   ├── ga_fetch.py
│   └── insights.py
├── writer/
│   └── draft.py
├── reviewer/
│   └── check.py
├── pm/
│   ├── orchestrator.py
│   └── report.py
├── data/
│   └── bapmap_marketing.db
└── daily_reports/
    └── YYYY-MM-DD.md
```

---

## 비용

- **Claude API: 0원** (Claude Code on Max 사용)
- **Max 구독**: 이미 구독 중
- **Reddit API**: 0원
- **GA API**: 0원
- **호스팅**: 0원 (로컬 실행)

추가 비용 없음.

---

## 운영 체크리스트

### 시작 전 사전 작업

- [ ] **시스템 만들기 전 1주일간 손으로 Reddit 답변 5개 직접 작성**
  - 어디가 시간 잡아먹는지 체험
  - 자동화할 진짜 병목 식별
  - 안 하면 안 쓰는 기능만 만듦

### 매일 운영

- [ ] 정해진 시간 1회 `claude` 실행
- [ ] PM 리포트 검토
- [ ] 우선순위 1-3번 작업 직접 실행 (Reddit 댓글, 인스타 포스팅 등)
- [ ] 채택/거절 피드백 DB에 입력

### 매주 회고

- [ ] 채택률 확인 (목표: 60% 이상)
- [ ] Bapmap 트래픽 변화 측정
- [ ] 노이즈 후보 비율 점검
- [ ] 다음 Phase 진행 여부 결정

---

## 함정 및 주의사항

1. **도구 만들기에 빠지지 말 것**: Phase 1을 4일 넘기면 마케팅 시간 또 0회로 끝남
2. **Reddit 자동 포스팅 절대 X**: 발굴/초안만, 실행은 손으로
3. **Reviewer 재시도 무한루프 방지**: 최대 2회 재시도, 그 이후 거절 사유와 함께 PM에 전달
4. **시스템 프롬프트 버전 관리**: `prompts/` 디렉토리 git으로 추적, 톤 조정 히스토리 보존
5. **운영자가 안 켜면 끝**: 시스템은 동기부여 못 해줌, 매일 실행 룰 사수
6. **Max 구독 한도 모니터링**: 마케팅 작업이 본인 평소 코딩/리서치 한도와 공유됨

---

## 면접/포트폴리오 활용

- **"플랫폼 정책 제약 안에서 Human-in-the-loop 마케팅 시스템 설계"**
- **"AI 어디까지 자동화 가능하고 어디서 인간이 필요한지 판단력 증명"**
- **"closed-loop AI marketing system": 발굴→초안→검토→실행→피드백→학습**
- **단순 카피 생성이 아닌 멀티 에이전트 협업 (5명 역할 분리, Reviewer 게이팅)**
- **수치 기반 결과**: Bapmap MAU, Reddit 답변 채택률, 광고 ROAS 등

AI 기획/서비스 운영 직무에서 단순 개발 경험보다 강한 어필 포인트.
