import os
import json
from anthropic import Anthropic
from openai import OpenAI

anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _generate(prompt: str, provider: str) -> str:
    if provider == "openai":
        res = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content
    else:
        res = anthropic_client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.content[0].text

PROMPT = """You are a content quality evaluator for Bapmap, a Korean local food guide for English-speaking travelers.

Evaluate this blog post on 5 criteria (each 0-10):
1. Specificity — concrete details, menu names, prices, practical tips
2. Human voice — reads like a person, not an AI. Penalize: "vibrant", "hidden gem", "culinary journey", FAQ boxes, vague encouraging sentences, "in the best way", generic closings
3. Usefulness — would a traveler actually use this info?
4. SEO — does the title/structure target real search queries?
5. GEO — would an AI engine (ChatGPT, Perplexity) cite this as a source?

Return JSON:
{{
  "scores": {{"specificity": 0, "human_voice": 0, "usefulness": 0, "seo": 0, "geo": 0}},
  "total": 0,
  "approved": true/false,
  "feedback": "specific actionable feedback if not approved — quote the AI-sounding phrases found"
}}

Approval threshold: total >= 40/50

Title: {title}
Draft:
{draft}

Return JSON only."""


def eval_agent(state: dict) -> dict:
    provider = state.get("provider", "anthropic")
    print(f"[Eval] 품질 평가 중... ({provider})")
    raw = _generate(PROMPT.format(
        title=state.get("title", ""),
        draft=state.get("draft", ""),
    ), provider)
    try:
        text = raw
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(text)
    except Exception:
        print("[Eval] JSON 파싱 실패, 기본 통과")
        return {**state, "approved": True, "eval_score": 0, "eval_feedback": ""}

    score = data.get("total", 0)
    approved = data.get("approved", False)
    feedback = data.get("feedback", "")
    scores = data.get("scores", {})

    print(f"[Eval] 점수: {score}/50 {scores}")
    print(f"[Eval] {'✅ 통과' if approved else '❌ 재작성 필요'}")
    if not approved:
        print(f"[Eval] 피드백: {feedback}")

    return {**state, "eval_score": score, "approved": approved, "eval_feedback": feedback}
