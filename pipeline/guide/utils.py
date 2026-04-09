import os
from anthropic import Anthropic
from openai import OpenAI

_anthropic = None
_openai = None


def get_anthropic():
    global _anthropic
    if _anthropic is None:
        _anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _anthropic


def get_openai():
    global _openai
    if _openai is None:
        _openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai


def generate(prompt: str, provider: str = "anthropic", max_tokens: int = 2000) -> str:
    if provider == "openai":
        res = get_openai().chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content
    try:
        res = get_anthropic().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.content[0].text
    except Exception:
        res = get_openai().chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return res.choices[0].message.content
