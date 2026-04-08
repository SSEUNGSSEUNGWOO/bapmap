import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SPOT_TEMPLATE = """You are a food writer for Bapmap — a Korean local spot guide for English-speaking travelers.

Write a blog post about this restaurant. You've eaten here. You're telling a friend about it over drinks.

VOICE:
- First-person opinions are fine ("This is the one I'd bring someone on a first visit")
- Dry, specific, occasionally funny — not enthusiastic, not cheerleader
- Short sentences when something matters. Longer when you're explaining
- If something is bad or mediocre, say so. Honest > positive

BANNED PHRASES AND PATTERNS:
- "hidden gem", "must-try", "culinary journey", "vibrant", "nestled"
- "in the best way", "rounds things out", "doesn't disappoint"
- "X has something for everyone"
- Starting sentences with "Whether you're..."
- Ending paragraphs with a vague encouraging sentence
- FAQ sections
- Quick Facts boxes or tables
- Any sentence structured as "It's not X, it's Y" unless you mean it
- Passive constructions like "is known for" — just say what it does

STRUCTURE (loose, not rigid):
- Open with a specific observation or scene, not a general statement about the neighborhood
- Dishes: name them, price them, describe the actual taste — not "rich and flavorful" but what specifically
- One honest caveat or limitation
- Practical logistics at the end (how to get there, reservation, hours)
- Last line: bapmap.com/spots/{slug}

Restaurant data:
{spot_data}

Curator's note:
{memo}

LENGTH: 500-700 words.

HEADER: Every post must start with this exact line before the title:
*BAPMAP - Recommended by a Korean who actually eats well.*"""

LIST_TEMPLATE = """You are a food writer for Bapmap - a Korean local spot guide for English-speaking travelers.

Write a listicle blog post. Topic: {topic}

Tone: honest, specific, like a local recommendation. Not promotional.

Restaurants:
{spots_data}

Structure:
- Intro (1 paragraph): why this list, what makes these picks different from tourist guides
- Each restaurant (150-200 words each):
  - Name + one-line hook
  - What to order
  - Price + subway
  - bapmap link: bapmap.com/spots/{{slug}}
- Closing tip: practical advice (reservations, timing, etc.)

Length: 800-1000 words. No "hidden gem". No "must-visit"."""


def writer(state: dict) -> dict:
    post_type = state.get("post_type", "spot")
    spots = state.get("spots_data", [])
    feedback = state.get("eval_feedback", "")

    revision_note = f"\n\nPrevious feedback to address:\n{feedback}" if feedback else ""

    if post_type == "spot" and spots:
        s = spots[0]
        name = s.get("english_name") or s.get("name", "")
        slug = name.lower().replace(" ", "-").replace("/", "-")
        prompt = SPOT_TEMPLATE.format(
            spot_data=_format_spot(s),
            memo=s.get("memo", ""),
            slug=slug,
        ) + revision_note
    else:
        guide = state.get("guide_data") or {}
        topic = state.get("topic") or guide.get("title", "")
        guide_context = ""
        if guide:
            guide_context = f"\nGuide intro (use as editorial direction):\n{guide.get('intro', '')}\n"
        prompt = LIST_TEMPLATE.format(
            topic=topic,
            spots_data="\n\n".join(_format_spot(s) for s in spots),
        ) + guide_context + revision_note

    print(f"[Writer] 포스트 작성 중... (revision #{state.get('revision_count', 0)})")
    res = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    draft = res.content[0].text
    return {**state, "draft": draft}


def _format_spot(s: dict) -> str:
    name = s.get("english_name") or s.get("name", "")
    return (
        f"Name: {name}\n"
        f"Category: {s.get('category', '')}\n"
        f"Region: {s.get('region') or s.get('city', '')}\n"
        f"Rating: {s.get('rating', '')} ({s.get('rating_count', '')} reviews)\n"
        f"Price: {s.get('price_level', '')}\n"
        f"Subway: {s.get('subway', '')}\n"
        f"Hours: {s.get('hours', '')}\n"
        f"What to order: {s.get('what_to_order', '')}\n"
        f"Content: {str(s.get('content', ''))[:500]}"
    )
