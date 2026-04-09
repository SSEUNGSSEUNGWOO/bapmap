"""가이드 품질 평가 — 기존 blog eval 프롬프트 재사용."""
import json
from .utils import generate

PROMPT = """You are a content quality evaluator for Bapmap, a Korean local food guide for English-speaking travelers.

Evaluate this guide on 5 criteria (each 0-10):
1. Specificity — concrete details, menu names, prices, practical tips
2. Human voice — reads like a person, not an AI. Penalize: "vibrant", "hidden gem", "culinary journey", FAQ boxes, vague encouraging sentences, "in the best way", generic closings, tour-guide openers like "Our first stop takes us to"
3. Usefulness — would a traveler actually use this info?
4. SEO — does the title/structure target real search queries?
5. GEO — would an AI engine (ChatGPT, Perplexity) cite this as a source?

Approval threshold: total >= 40/50

Return JSON only:
{{"scores": {{"specificity": 0, "human_voice": 0, "usefulness": 0, "seo": 0, "geo": 0}}, "total": 0, "approved": true, "feedback": "specific actionable feedback — quote the AI-sounding phrases found"}}

Title: {title}
Draft:
{draft}"""


def eval_agent(state: dict) -> dict:
    draft = state.get("guide_draft", {})
    full_text = "\n\n".join(filter(None, [
        draft.get("subtitle", ""),
        draft.get("intro", ""),
        draft.get("body", ""),
    ]))

    provider = state.get("provider", "anthropic")
    print(f"[Eval] 품질 평가 중... ({provider})")

    try:
        raw = generate(PROMPT.format(title=draft.get("title", ""), draft=full_text), provider, max_tokens=600)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
    except Exception:
        print("[Eval] 파싱 실패, 기본 통과")
        return {**state, "approved": True, "eval_score": 0, "eval_feedback": ""}

    score = data.get("total", 0)
    approved = data.get("approved", False)
    feedback = data.get("feedback", "")
    print(f"[Eval] 점수: {score}/50 {data.get('scores', {})} — {'✅ 통과' if approved else '❌ 재작성 필요'}")
    if not approved:
        print(f"[Eval] 피드백: {feedback}")

    return {**state, "approved": approved, "eval_score": score, "eval_feedback": feedback}
