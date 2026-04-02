import os
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


PROMPT = """You are a food writer for Bapmap — a Korean local spot guide for English-speaking tourists visiting Korea for the first time or second time.

Write a blog post about this spot. Tone: like a tip from a Korean friend who actually eats here — honest, specific, occasionally opinionated.

Spot data:
{data}

---

WRITING STYLE (read carefully):
- Write like a real person, not a content bot.
- Vary sentence length. Short punchy sentences. Then a longer one that builds on it.
- Do NOT use: "nestled", "bustling", "hidden gem", "must-try", "don't miss out", "culinary journey", "food lovers"
- Do NOT start every sentence with a compliment. It's okay to say "the wait can be brutal" or "it's not the prettiest space"
- Use one strong adjective instead of three weak ones
- Occasionally share a practical insider tip that only a local would know (e.g. best time to avoid queues, what NOT to order, seating tips)
- If the Google reviews mention something specific (wait times, a standout dish, a tip), weave it in naturally — don't copy it

STRICT LANGUAGE RULES:
- Write entirely in English. No Korean characters in body text.
- Restaurant name: romanized form first, Korean name once in parentheses on first mention only
- Menu items: English description + Korean name in parentheses is fine
- Address: include Korean address once in Practical Info for navigation apps
- Do NOT invent dish names you're unsure about

CONTENT REQUIREMENTS:
1. H1 title — specific, location + food type (not generic)
2. Opening hook — 2-3 sentences max. Why this place, why now
3. "What to Expect" — essential for first-timers. If the food is unfamiliar (offal, fermented foods, raw seafood, braised intestines, blood sausage, etc.), describe it warmly. Compare to something familiar if helpful. Don't scare people off.
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
