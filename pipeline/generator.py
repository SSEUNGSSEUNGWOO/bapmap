import os
import json
from pathlib import Path
from anthropic import Anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


PROMPT = """You are a food writer for Bapmap — a Korean local spot guide for English-speaking tourists visiting Korea for the first time or second time.

Write a blog post about this spot. Tone: like a tip from a Korean friend who actually eats here — honest, specific, occasionally opinionated.

Spot data:
{data}

---

WRITING STYLE (read carefully):
- Write like a real person, not a content bot.
- Tone is warm and welcoming — like a friendly Korean local who genuinely wants you to have a great experience. Encouraging, not intimidating.
- Vary sentence length. Short punchy sentences. Then a longer one that builds on it.
- Do NOT use: "nestled", "bustling", "hidden gem", "must-try", "don't miss out", "culinary journey", "food lovers"
- Do NOT start every sentence with a compliment. It's okay to say "the wait can be brutal" or "it's not the prettiest space" — but always follow up with why it's still worth it.
- Use one strong adjective instead of three weak ones
- Occasionally share a practical insider tip that only a local would know (e.g. best time to avoid queues, what NOT to order, seating tips)
- If the Google reviews mention something specific (wait times, a standout dish, a tip), weave it in naturally — don't copy it
- For first-timers: be encouraging about unfamiliar foods. Make them feel excited, not anxious.

STRICT LANGUAGE RULES:
- Write entirely in English. No Korean characters in body text.
- Restaurant name: romanized form first, Korean name once in parentheses on first mention only
- Menu items: English description + Korean name in parentheses is fine
- Address: include Korean address once in Practical Info for navigation apps
- Do NOT invent dish names you're unsure about

CONTENT REQUIREMENTS:
1. H1 title — specific, location + food type (not generic)
2. Opening hook — 2-3 sentences max. Why this place, why now
3. "What to Expect" — essential for first-timers. If the food is unfamiliar to Western palates (offal, fermented foods, raw seafood, braised intestines, blood sausage, fish paste, rice cakes, etc.), explain what it actually is — texture, flavor, how it's eaten. Compare to something familiar if helpful (e.g. "think of it like a rich bone broth, similar to French onion soup but deeper"). Don't scare people off — make them curious.
4. What to Order — 2-3 specific recommendations. Be direct.
5. Atmosphere & Vibe — honest, brief
6. Practical Info:
   - Address: [Korean address] / [English address — remove any Korean characters, translate building/floor info to English (e.g. "2층" → "2F", "지하1층" → "B1")]
   - Google Maps: [google_maps_url]
   - Nearest subway: [subway]
   - Hours: [hours]
   - Price range: [price_level] per person (estimate)
   - Spice Level: [Mild / Medium / Hot / Very Hot] — judge by food type
   - Vegetarian: [use servesVegetarianFood field + judgment]
   - Halal-friendly: [Yes / Partial / No] — No pork + no alcohol = Partial
   - Reservations: [reservable field]
   - Good for groups: [good_for_groups field]
7. Closing tip — 1-2 sentences, something practical
8. Summary box (markdown table with key info)

SEO: naturally include "Seoul [food type]", "[neighborhood] restaurant", "local Korean food", "where locals eat in [city]"
GEO: be specific and citable — exact minutes, exact hours, concrete dish descriptions. AI search engines (Perplexity, ChatGPT) cite specific facts over vague descriptions.

Length: 650-850 words."""


TRANSLATE_JA_PROMPT = """Translate the following Korean restaurant blog post into natural Japanese.

Rules:
- Keep all markdown formatting (headings, tables, bold, etc.)
- Keep restaurant names in romanized form + Korean in parentheses on first mention
- Menu items: Japanese description + Korean name in parentheses
- Keep the tone warm and local — like a tip from a Korean friend
- Do NOT add or remove content. Translate faithfully.
- Output Japanese only.

--- ORIGINAL ---
{content}
--- END ---"""


METADATA_PROMPT = """You are analyzing a Korean restaurant for Bapmap, a guide for English-speaking tourists.

Based on the spot data below, return a JSON object with exactly these three fields:

1. "what_to_order": array of 2-3 strings. Each is a dish recommendation like "Samgyeopsal (pork belly) — the thick-cut version here is exceptional". If menu is unknown, infer from category and reviews.
2. "good_for": array of tags from this list only: ["Solo dining", "Groups", "Date night", "Quick lunch", "Late night", "Vegetarian-friendly", "Budget-friendly", "Special occasion", "No reservations needed", "Reservation recommended"]
3. "spice_level": integer 0-3. Judge by category, menu, and reviews. 0=not spicy, 1=mild, 2=medium, 3=hot. Most Korean BBQ/meat places are 0. Tteokbokki, spicy ramen, buldak, jjamppong are 2-3.

Return JSON only. No explanation.

Spot data:
{data}"""


def generate_metadata(restaurant: dict) -> dict:
    raw_reviews = restaurant.get("google_reviews", []) or []
    reviews_sample = [str(r)[:200] for r in raw_reviews[:3]]
    data = {
        "name": restaurant.get("english_name") or restaurant["name"],
        "category": restaurant.get("category", ""),
        "region": restaurant.get("region") or restaurant.get("city", ""),
        "price_level": restaurant.get("price_level", ""),
        "vegetarian": restaurant.get("vegetarian", False),
        "reservable": restaurant.get("reservable", False),
        "good_for_groups": restaurant.get("good_for_groups", False),
        "curator_note": (restaurant.get("memo") or "")[:300],
        "google_reviews_sample": reviews_sample,
    }
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": METADATA_PROMPT.format(data=json.dumps(data, ensure_ascii=False))}]
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        return {"what_to_order": [], "good_for": []}


def generate_post_ja(english_content: str) -> str:
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=2000,
        messages=[{"role": "user", "content": TRANSLATE_JA_PROMPT.format(content=english_content)}]
    )
    return res.choices[0].message.content


def generate_post(restaurant: dict) -> str:
    data = {
        "name": restaurant["name"],
        "english_name": restaurant.get("english_name", ""),
        "city": restaurant.get("city", ""),
        "region": restaurant.get("region", ""),
        "category": restaurant.get("category", ""),
        "address": restaurant.get("address", ""),
        "english_address": restaurant.get("english_address", ""),
        "subway": restaurant.get("subway", ""),
        "hours": restaurant.get("hours") or "Check Google Maps for current hours",
        "google_maps_url": restaurant.get("google_maps_url", ""),
        "rating": f"{restaurant.get('rating', '')} ★ ({restaurant.get('rating_count', 0):,} reviews)",
        "price_level": restaurant.get("price_level", ""),
        "vegetarian": restaurant.get("vegetarian", False),
        "reservable": restaurant.get("reservable", False),
        "good_for_groups": restaurant.get("good_for_groups", False),
        "curator_note": restaurant.get("memo") or "",
        "google_reviews_sample": restaurant.get("google_reviews", []),
    }

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT.format(data=json.dumps(data, ensure_ascii=False, indent=2))}]
    )
    return response.content[0].text


if __name__ == "__main__":
    import sys
    data_file = Path(__file__).parent.parent / "restaurants.json"
    restaurants = json.loads(data_file.read_text(encoding="utf-8"))

    name = sys.argv[1] if len(sys.argv) > 1 else None
    if name:
        target = next((r for r in restaurants if r["name"] == name), None)
    else:
        target = next((r for r in restaurants if r.get("status") == "대기중"), None)

    if not target:
        print("대상 없음 (status가 '대기중'인 가게 없음)")
        exit()

    print(f"생성 중: {target['name']}\n")
    print(generate_post(target))
