---
description: Reddit에서 Bapmap 추천 기회를 발굴하고 댓글 초안을 만든 뒤 일일 리포트로 정리한다
---

# /marketing

Reddit에서 한국 여행/식당 관련 포스트를 크롤링해서 적합도 평가, 댓글 초안 작성, 사용자 검토, 일일 리포트 저장까지 진행한다.

---

## 1단계 — Reddit 포스트 크롤링

```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
python -m marketing.scout
```

- 대상 subreddit: `koreatravel`, `seoul`, `Korea`
- 키워드 필터: where to eat / restaurant / food / recommendation / vegetarian / halal 등
- 블록 키워드: visa / job / apartment / dating 등 (음식 무관)
- 결과는 SQLite `marketing/data/bapmap_marketing.db` 의 `opportunities` 테이블에 저장 (status="pending")

---

## 2단계 — 적합도 평가 (Claude Code 직접)

`opportunities` 중 `status = 'pending'` 이고 `fit_score IS NULL` 인 것들을 조회.

각 포스트를 0~10점으로 평가:
- 8~10: 명확한 식당 추천 요청, 지역/조건 구체적 → 댓글 가치 큼
- 5~7: 모호하지만 답변 여지 있음
- 0~4: 음식 관련 약함 또는 이미 답변 충분 → 스킵

`opportunities.fit_score`, `fit_reason` (한 문장) 업데이트.

---

## 3단계 — 댓글 초안 작성 (Claude Code 직접)

`fit_score >= 7` 인 포스트들 대상.

각 댓글:
- 200~300단어, 자연스러운 톤, 홍보스럽지 않게
- 질문자 조건(지역/예산/식이/일행)을 짚어주고
- Bapmap 등록 스팟 중 적합한 곳 1~3개를 구체적으로 추천 (메뉴/가격/도보/단점 명시)
- 마지막에 `https://bapmap.com/spots/{slug}` 또는 `/guides/{slug}` 링크 1개 (필요할 때만, 강요 X)
- Supabase `spots` (status='업로드완료') 또는 `guides` (status='published') 에서 실제 등록된 것만 추천

`drafts` 테이블에 INSERT (`opportunity_id`, `draft`, `status='pending'`).

---

## 4단계 — 사용자 검토

각 (opportunity, draft) 쌍을 사용자에게 보여주기:
- 포스트 제목/URL/본문 요약
- 적합도 점수 + 사유
- 댓글 초안 전문

사용자 응답: 채택(1) / 거절(0) / 수정 요청.

수정 요청이면 피드백 반영해 재작성 후 다시 컨펌.

채택/거절 결정은 다음 명령으로 저장:
```bash
cd /Users/sseung/Projects/personal/bapmap/ai-service
python -m marketing.feedback <opp_id> <draft_id> <1|0> [reason]
```

---

## 5단계 — 일일 리포트 저장

오늘 처리 결과를 `ai-service/marketing/daily_reports/YYYY-MM-DD.md` 로 저장. 형식:

```markdown
# 마케팅 브리핑 YYYY-MM-DD

## 요약
- 신규 발굴: N개
- 적합 (≥7점): M개
- 댓글 작성: K개
- 채택: X개 / 거절: Y개

## 채택된 댓글
### [포스트 제목](url) — 적합도 9
**사유**: ...
**댓글**:
> ...

## 거절된 댓글
### [포스트 제목](url) — 적합도 7
**거절 사유**: ...

## 다음 액션
- (필요시) 새로 발굴할 만한 키워드/subreddit 제안
```

`daily_reports` 테이블에도 `(date, report_path)` INSERT.

---

## 마무리 보고

- 발굴 / 적합 / 작성 / 채택 카운트
- 리포트 파일 경로
- 채택된 댓글은 사용자가 직접 Reddit에 게시 (자동 게시 X)
